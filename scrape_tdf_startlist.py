"""
TOUR DE FRANCE STARTLISTE -> Google Sheet
- Henter den officielle TDF-startliste fra ProCyclingStats
- Markerer udtagne ryttere med "TDF" i kolonne D i Points-arket
- Frontenden viser så et 🇫🇷 + TDF-badge ud for dem (kun i juni/juli)

Defensiv:
- Hvis startlisten endnu ikke er offentliggjort (få/ingen ryttere),
  rører scriptet IKKE arket - så vi aldrig sletter noget ved en fejl.
- Alle fejl fanges og scriptet afslutter pænt (exit 0), så det aldrig
  vælter den daglige point-opdatering i samme workflow.
"""

import re
import sys
import time
import random
from datetime import datetime

import cloudscraper
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Samme opsætning som point-scriptet
CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'
SHEET_NAME = 'Cycling Fantasy 2026'
WORKSHEET_NAME = 'Points'

TDF_COLUMN = 'D'                 # kolonne hvor "TDF" skrives
MIN_RIDERS_TO_TRUST = 50         # under dette antal regnes startlisten som "ikke klar"


def scrape_startlist(year):
    """Hent rytternavne fra PCS' TDF-startliste. Returnerer en liste af navne
    i 'EFTERNAVN Fornavn'-format (samme format som arket bruger)."""
    url = f"https://www.procyclingstats.com/race/tour-de-france/{year}/startlist/startlist"
    print(f"📥 Henter startliste: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
    }

    def new_scraper():
        s = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'darwin', 'mobile': False}
        )
        s.headers.update(headers)
        return s

    scraper = new_scraper()
    resp = None
    for attempt in range(1, 4):  # op til 3 forsøg
        time.sleep(random.uniform(1.5, 3))
        resp = scraper.get(url, timeout=30)
        if resp.status_code == 200:
            break
        print(f"HTTP {resp.status_code} (forsøg {attempt}/3)")
        if attempt < 3:
            time.sleep(random.uniform(20, 40))
            scraper = new_scraper()  # frisk session hjælper mod Cloudflare

    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code} - opgiver efter gentagne forsøg")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    names = []
    seen = set()
    for a in soup.find_all('a', href=True):
        if '/rider/' not in a['href']:
            continue
        text = a.get_text(' ', strip=True)
        if not text:
            continue
        # Startliste-navne er "EFTERNAVN Fornavn": første ord er STORE bogstaver.
        # Det udelukker sidebjælkens "Fornavn Efternavn"-links.
        first = text.split(' ', 1)[0]
        if len(first) < 2 or not first.isupper():
            continue
        if text not in seen:
            seen.add(text)
            names.append(text)

    print(f"✅ Fandt {len(names)} ryttere på startlisten")
    return names


def normalize(name):
    """Til sammenligning: store bogstaver, ét mellemrum, accenter/apostroffer fjernet."""
    import unicodedata
    s = unicodedata.normalize('NFD', str(name))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('ø', 'o').replace('Ø', 'O').replace('å', 'a').replace('Å', 'A')
    s = s.replace('æ', 'ae').replace('Æ', 'AE')
    for q in ("'", '‘', '’'):
        s = s.replace(q, '')
    return ' '.join(s.split()).upper()


def is_on_startlist(rider_name, startlist_norm):
    n = normalize(rider_name)
    if n in startlist_norm:
        return True
    # match på for- + efternavn (rækkefølge kan variere)
    parts = n.split()
    if len(parts) >= 2:
        for sn in startlist_norm:
            sp = sn.split()
            if len(sp) >= 2 and {sp[0], sp[-1]} == {parts[0], parts[-1]}:
                return True
    return False


def main():
    year = datetime.now().year
    try:
        startlist = scrape_startlist(year)
    except Exception as e:
        print(f"⚠️  Kunne ikke hente startliste: {e}")
        return  # exit 0 - bryd ikke workflowet

    if len(startlist) < MIN_RIDERS_TO_TRUST:
        print(f"ℹ️  Kun {len(startlist)} ryttere fundet - startlisten er nok ikke "
              f"offentliggjort endnu. Rører ikke arket.")
        return

    startlist_norm = {normalize(n) for n in startlist}

    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        sheet = gspread.authorize(creds).open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        rows = sheet.get_all_values()
    except Exception as e:
        print(f"⚠️  Kunne ikke forbinde til Google Sheet: {e}")
        return

    updates = []
    selected = 0
    for i, row in enumerate(rows[1:], start=2):  # spring header over
        if not row or not row[0].strip():
            continue
        rider = row[0].strip()
        mark = 'TDF' if is_on_startlist(rider, startlist_norm) else ''
        if mark:
            selected += 1
        updates.append({'range': f'{TDF_COLUMN}{i}', 'values': [[mark]]})

    if updates:
        try:
            sheet.batch_update(updates)
            print(f"✅ Opdateret kolonne {TDF_COLUMN}: {selected} ryttere markeret som TDF")
        except Exception as e:
            print(f"⚠️  Kunne ikke skrive til arket: {e}")


if __name__ == '__main__':
    main()
    sys.exit(0)
