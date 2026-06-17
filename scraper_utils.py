"""
Fælles hent-funktion til scraperne.

Strategi (gratis):
  1. Hvis FlareSolverr er konfigureret (FLARESOLVERR_URL), bruges den PRIMÆRT:
     et open source-værktøj der starter en RIGTIG Chrome-browser og løser Cloudflares
     udfordring. Det kører som en container inde i GitHub Actions - ingen konto, ingen
     nøgle, ingen betaling. (Da PCS' Cloudflare blokerer cloudscraper, sparer det tid
     at gå direkte til FlareSolverr i stedet for først at fejle 20 gange.)
  2. cloudscraper bruges som backup (eller primært, hvis FlareSolverr ikke er sat -
     fx ved lokal kørsel uden containeren).

Opsætning:
  - FLARESOLVERR_URL sættes i workflowet til http://localhost:8191/v1 (containeren).
    Lokalt kan du selv køre den med:  docker run -d -p 8191:8191 ghcr.io/flaresolverr/flaresolverr
  - Uden FLARESOLVERR_URL opfører alt sig som før (kun cloudscraper).

  (Valgfrit: hvis du en dag vil bruge en betalt scraping-API som ekstra backup,
   kan SCRAPER_API_KEY + SCRAPER_API_TEMPLATE sættes - bruges kun hvis FlareSolverr
   også fejler.)
"""

import os
import time
import random
import atexit
import urllib.parse

import requests
import cloudscraper

FLARESOLVERR_URL = os.environ.get("FLARESOLVERR_URL", "").strip()
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "").strip()
SCRAPER_API_TEMPLATE = os.environ.get(
    "SCRAPER_API_TEMPLATE",
    "https://api.scraperapi.com/?api_key={key}&url={url}",
)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
}


def _new_scraper():
    s = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )
    s.headers.update(_HEADERS)
    return s


# FlareSolverr-session: løs Cloudflare-udfordringen ÉN gang og genbrug cookien
# til alle efterfølgende sider. Det gør de næste hentninger næsten øjeblikkelige.
_FS_SESSION = None
MAX_TIMEOUT_MS = 120000  # FlareSolverr får op til 120 sek. til at løse en udfordring


def _ensure_session():
    global _FS_SESSION
    if _FS_SESSION is not None:
        return _FS_SESSION
    try:
        r = requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.create"}, timeout=MAX_TIMEOUT_MS / 1000 + 30)
        data = r.json()
        if data.get("status") == "ok" and data.get("session"):
            _FS_SESSION = data["session"]
            print(f"   FlareSolverr-session oprettet ({str(_FS_SESSION)[:8]}…)")
    except Exception as e:
        print(f"   Kunne ikke oprette FlareSolverr-session: {e}")
    return _FS_SESSION


def _destroy_session():
    global _FS_SESSION
    if _FS_SESSION:
        try:
            requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.destroy", "session": _FS_SESSION}, timeout=30)
        except Exception:
            pass
        _FS_SESSION = None


atexit.register(_destroy_session)


def _via_flaresolverr(url):
    """Hent via FlareSolverr (rigtig browser der løser Cloudflare). (html, status).
    Genbruger en session, så udfordringen kun løses én gang."""
    payload = {"cmd": "request.get", "url": url, "maxTimeout": MAX_TIMEOUT_MS}
    sess = _ensure_session()
    if sess:
        payload["session"] = sess
    r = requests.post(FLARESOLVERR_URL, json=payload, timeout=MAX_TIMEOUT_MS / 1000 + 30)
    data = r.json()
    if data.get("status") == "ok":
        sol = data.get("solution", {})
        return sol.get("response"), sol.get("status", 200)
    print(f"   FlareSolverr: {data.get('message', 'ukendt fejl')}")
    return None, None


def _via_api(url, timeout):
    """Valgfri betalt scraping-API som sidste udvej. (html, status)."""
    api_url = SCRAPER_API_TEMPLATE.format(
        key=SCRAPER_API_KEY, url=urllib.parse.quote(url, safe="")
    )
    r = requests.get(api_url, timeout=max(timeout, 90))
    if r.status_code == 200:
        return r.text, 200
    return None, r.status_code


def fetch(url, max_retries=2, timeout=30):
    """Hent en URL robust. Returnerer (html_text, status_code).
    html_text er None hvis alt fejlede.

    Rækkefølge:
      - Hvis FlareSolverr er konfigureret: brug den PRIMÆRT (cloudscraper er
        alligevel blokeret af Cloudflare, så det sparer tid at gå direkte hertil).
      - Ellers / hvis FlareSolverr fejler: cloudscraper.
      - Til sidst: valgfri betalt API (kun hvis nøgle er sat).
    """
    last_status = None

    # 1) FlareSolverr som primær (rigtig browser der omgår Cloudflare)
    if FLARESOLVERR_URL:
        for attempt in range(1, 3):
            try:
                html, status = _via_flaresolverr(url)
                if html is not None:
                    print("   ✅ hentet via FlareSolverr")
                    return html, status or 200
                print(f"   FlareSolverr gav intet (forsøg {attempt}/2)")
            except Exception as e:
                print(f"   FlareSolverr fejl (forsøg {attempt}/2): {e}")
            time.sleep(random.uniform(2, 5))
        print("   → FlareSolverr fejlede, prøver cloudscraper...")

    # 2) cloudscraper (primær hvis ingen FlareSolverr, ellers backup)
    scraper = _new_scraper()
    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(random.uniform(1.5, 3))
            r = scraper.get(url, timeout=timeout)
            last_status = r.status_code
            if r.status_code == 200:
                return r.text, 200
            print(f"   cloudscraper HTTP {r.status_code} (forsøg {attempt}/{max_retries})")
        except Exception as e:
            print(f"   cloudscraper fejl (forsøg {attempt}/{max_retries}): {e}")
        if attempt < max_retries:
            time.sleep(random.uniform(8, 15))
            scraper = _new_scraper()

    # 3) Valgfri betalt API (kun hvis nøgle er sat)
    if SCRAPER_API_KEY:
        try:
            print("   → prøver via betalt scraping-API...")
            html, status = _via_api(url, timeout)
            if html is not None:
                print("   ✅ hentet via scraping-API")
                return html, 200
            last_status = status
        except Exception as e:
            print(f"   scraping-API fejl: {e}")

    return None, last_status
