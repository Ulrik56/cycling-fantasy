"""
WORKING CYKELKALENDEREN.DK SCRAPER
Parser RAW HTML for at finde "X danskere til start"
"""

import cloudscraper
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# =============================================================================
# KONFIGURATION  
# =============================================================================

CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'
SHEET_NAME = 'Cycling Fantasy 2026'
WORKSHEET_NAME = 'Kommende Løb'

# =============================================================================
# FUNKTIONER
# =============================================================================

def get_danish_riders_from_race(race_url, race_name):
    """Hent danske ryttere fra løbets side på cykelkalenderen.dk"""
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'mobile': False
        }
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
    }
    scraper.headers.update(headers)
    
    try:
        time.sleep(random.uniform(1, 2))
        response = scraper.get(race_url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        danish_riders = []
        
        # Find DK flag billeder
        dk_flags = soup.find_all('img', src=lambda x: x and 'dk.png' in x.lower())
        
        for flag in dk_flags:
            parent = flag.find_parent(['tr', 'td', 'div', 'li', 'p', 'span'])
            if parent:
                # Find rytter link (bedste metode)
                rider_link = parent.find('a', href=lambda x: x and '/rytter/' in x)
                if rider_link:
                    rider_name = rider_link.get_text(strip=True)
                    if rider_name and len(rider_name) > 3 and rider_name not in danish_riders:
                        danish_riders.append(rider_name)
                else:
                    # Backup: Parse text manuelt
                    text = parent.get_text(strip=True)
                    # Format kan være:
                    # "Kristian EgholmLidl - Trek (WT)"
                    # "Sebastian Kolze ChangiziTudor Pro Cycling Team (PRT)"
                    
                    # Find rytter navn (stopper ved holdnavn)
                    # Holdnavne starter typisk med stort bogstav + flere store bogstaver eller " - " eller "("
                    # Rytter navne har mellemrum mellem ord
                    
                    # Split ved første forekomst af enten:
                    # - To store bogstaver i træk (UAErTeam)
                    # - " - " (Lidl - Trek)
                    # - "(" (Tudor (PRT))
                    parts = re.split(r'(?=[A-ZÆØÅ]{2,})|(?=\s+-\s+)|(?=\()', text, maxsplit=1)
                    if parts:
                        rider_name = parts[0].strip()
                        # Tjek at det ligner et navn (har mindst 2 ord med mellemrum)
                        if ' ' in rider_name and len(rider_name) > 5 and rider_name not in danish_riders:
                            danish_riders.append(rider_name)
        
        return danish_riders[:20]
        
    except Exception as e:
        return []

def scrape_cykelkalenderen():
    """Hent kommende løb fra Cykelkalenderen.dk"""
    print("\n" + "=" * 70)
    print("🚴 HENTER KOMMENDE LØB FRA CYKELKALENDEREN.DK")
    print("=" * 70)
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'mobile': False
        }
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
    }
    scraper.headers.update(headers)
    
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    races = []
    
    # Hent denne måned
    url = f"https://cykelkalenderen.dk/loebskalender?vis=liste&m={today.strftime('%Y-%m')}"
    
    print(f"\n📅 Henter {today.strftime('%B %Y')}...")
    
    try:
        time.sleep(random.uniform(2, 4))
        response = scraper.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find alle rows i kalenderen
        table_rows = soup.find_all('tr')
        
        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Første celle = dato
            date_cell = cells[0]
            date_text = date_cell.get_text(strip=True)
            
            # Parse dato
            date_match = re.search(r'd\. (\d+)/(\d+)', date_text)
            if not date_match:
                continue
            
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = today.year
            
            try:
                race_date = datetime(year, month, day)
            except:
                continue
            
            # Kun løb i de næste 7 dage
            if not (today.date() <= race_date.date() <= next_week.date()):
                continue
            
            # Anden celle = løb - få RAW HTML
            races_cell = cells[1]
            cell_html = str(races_cell)
            
            print(f"\n   📅 {race_date.strftime('%d.%m')}:")
            
            # Find alle løb links
            race_links = races_cell.find_all('a', href=lambda x: x and '/loeb/' in x)
            
            for link in race_links:
                race_text = link.get_text(strip=True)
                race_text_lower = race_text.lower()
                
                # SKIP kvindeløb, cyklecross og bane
                if any([
                    '[K]' in race_text,
                    'cyklecross' in race_text_lower,
                    'cyclocross' in race_text_lower,
                    'cykelcross' in race_text_lower,
                    'bane' in race_text_lower,
                    'track' in race_text_lower,
                    'vm i cyklecross' in race_text_lower
                ]):
                    continue
                
                # Inkluder alle andre landevejsløb
                print(f"      🚴 {race_text[:60]}")
                
                # Ekstraher race navn
                race_name_simple = re.sub(r'\s*-\s*\d+\.\s*etape.*', '', race_text).strip()
                race_name_short = race_name_simple.split('[')[0].strip()
                
                # Søg i RAW HTML efter: ">4 danskere til start i AlUla Tour"
                # Flere mønstre
                patterns = [
                    rf'>(\d+)\s+danskere?\s+til\s+start\s+i\s+{re.escape(race_name_short)}',
                    rf'(\d+)\s+danskere?\s+til\s+start\s+i\s+{re.escape(race_name_short)}',
                ]
                
                danish_count = 0
                for pattern in patterns:
                    danish_match = re.search(pattern, cell_html, re.IGNORECASE)
                    if danish_match:
                        danish_count = int(danish_match.group(1))
                        print(f"         ✅ {danish_count} danskere!")
                        break
                
                # Hvis ingen danskere fundet, tjek om det er et mænds landevejsløb
                if danish_count == 0:
                    print(f"         ℹ️  Ingen danskere")
                
                # Hent danske ryttere navne hvis der er nogen
                danish_riders = []
                if danish_count > 0:
                    print(f"         🔍 Henter {danish_count} danske navne...", end=" ", flush=True)
                    race_url = 'https://cykelkalenderen.dk' + link.get('href', '')
                    danish_riders = get_danish_riders_from_race(race_url, race_name_simple)
                    if danish_riders:
                        print(f"✅ Fundet {len(danish_riders)} navne:")
                        for rider in danish_riders:
                            print(f"            • {rider}")
                    else:
                        print(f"⚠ Ingen navne fundet")
                
                # Gem ALLE mænds landevejsløb (også uden danskere)
                races.append({
                    'name': race_name_simple,
                    'date': race_date,
                    'danish_count': danish_count,
                    'danish_riders': danish_riders,
                    'url': 'https://cykelkalenderen.dk' + link.get('href', '')
                })
        
        print(f"\n✅ Fundet {len(races)} løb")
        
    except Exception as e:
        print(f"❌ Fejl: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return races

def consolidate_races(races):
    """Konsolider løb (samme løb kan have flere etaper)"""
    consolidated = {}
    
    for race in races:
        name = race['name']
        if name not in consolidated:
            consolidated[name] = {
                'name': name,
                'date': race['date'],
                'danish_count': race['danish_count'],
                'danish_riders': race['danish_riders'],
                'url': race['url']
            }
        else:
            # Opdater hvis dette er en tidligere etape
            if race['date'] < consolidated[name]['date']:
                consolidated[name]['date'] = race['date']
            # Merge danske ryttere (fjern duplikater)
            existing_riders = set(consolidated[name]['danish_riders'])
            new_riders = set(race['danish_riders'])
            consolidated[name]['danish_riders'] = list(existing_riders | new_riders)
    
    return list(consolidated.values())

def save_to_google_sheets(races):
    """Gem til Google Sheets"""
    print("\n" + "=" * 70)
    print("💾 GEMMER TIL GOOGLE SHEETS")
    print("=" * 70)
    
    try:
        # Forbind til Google Sheets
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        client = gspread.authorize(creds)
        
        # Åbn spreadsheet
        spreadsheet = client.open(SHEET_NAME)
        
        # Tjek om worksheet eksisterer, ellers opret
        try:
            sheet = spreadsheet.worksheet(WORKSHEET_NAME)
            sheet.clear()
        except:
            sheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=100, cols=4)
        
        print(f"✅ Forbundet til Google Sheets")
        
        # Opbyg data
        data = [['Dato', 'Løb', 'Danske Ryttere', 'Opdateret']]
        
        for race in sorted(races, key=lambda x: x['date']):
            date_str = race['date'].strftime('%d.%m')
            
            # Lav liste af danske ryttere
            if race['danish_riders']:
                riders_str = ', '.join(race['danish_riders'])
            else:
                riders_str = f"{race['danish_count']} danskere" if race['danish_count'] > 0 else "Ingen danske"
            
            data.append([
                date_str,
                race['name'],
                riders_str,
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ])
        
        # Skriv til sheet
        sheet.update(range_name='A1', values=data)
        
        print(f"✅ Gemt {len(races)} løb til sheet")
        
    except Exception as e:
        print(f"❌ Fejl ved gemning: {e}")

def main():
    """Main funktion"""
    print("\n" + "=" * 70)
    print("🚴 CYKELKALENDEREN.DK SCRAPER - WORKING VERSION")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. Hent kommende løb
    races = scrape_cykelkalenderen()
    
    if not races:
        print("\n❌ Ingen kommende løb fundet")
        return
    
    # 2. Konsolider (fjern duplikater)
    consolidated = consolidate_races(races)
    
    print(f"\n📊 {len(consolidated)} unikke løb de næste 7 dage")
    
    # 3. Gem til Google Sheets
    save_to_google_sheets(consolidated)
    
    # 4. Vis resultat
    print("\n" + "=" * 70)
    print("📊 RESULTAT")
    print("=" * 70)
    for race in sorted(consolidated, key=lambda x: x['date']):
        print(f"\n📅 {race['date'].strftime('%d.%m')} - {race['name']}")
        if race['danish_riders']:
            print(f"   🇩🇰 {len(race['danish_riders'])} danske ryttere:")
            for rider in race['danish_riders']:
                print(f"      • {rider}")
        elif race['danish_count'] > 0:
            print(f"   🇩🇰 {race['danish_count']} danske ryttere (navne ikke fundet)")
        else:
            print(f"   Ingen danske ryttere")
    
    print("\n" + "=" * 70)
    print(f"🏁 FÆRDIG!")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()