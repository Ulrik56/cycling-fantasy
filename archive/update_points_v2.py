"""
Automated UCI Points Updater for Cycling Fantasy Manager - IMPROVED VERSION
Henter point fra ProCyclingStats og opdaterer Google Sheets automatisk
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re

# =============================================================================
# KONFIGURATION - ERSTAT DISSE VÆRDIER
# =============================================================================

# Sti til din Google credentials JSON fil
CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'  # ERSTAT MED DIN FIL

# Dit Google Sheet navn
SHEET_NAME = 'Cycling Fantasy 2026'

# Worksheet navn (fanen i sheetet)
WORKSHEET_NAME = 'Points'

# =============================================================================
# FUNKTIONER
# =============================================================================

def connect_to_sheets():
    """Forbind til Google Sheets"""
    print("📊 Forbinder til Google Sheets...")
    
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        print("✅ Forbundet til Google Sheets!")
        return sheet
    except Exception as e:
        print(f"❌ Fejl ved forbindelse til Google Sheets: {e}")
        return None

def search_rider_on_pcs(rider_name):
    """Søg efter rytter på ProCyclingStats og returner URL"""
    try:
        # Lav søgning URL-venlig
        search_term = rider_name.replace(' ', '+')
        search_url = f"https://www.procyclingstats.com/search.php?term={search_term}&searchf=Search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find første rider link
        for link in soup.find_all('a', href=True):
            if '/rider/' in link['href'] and 'statistics' not in link['href']:
                return 'https://www.procyclingstats.com' + link['href']
        
        return None
        
    except Exception as e:
        print(f"Søgefejl: {e}")
        return None

def get_rider_uci_points_from_page(rider_url):
    """Hent UCI points direkte fra rytterens side"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(rider_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Metode 1: Find i UCI ranking info
        uci_divs = soup.find_all('div', class_='rdr-info-cont')
        for div in uci_divs:
            text = div.get_text()
            if 'UCI' in text and 'points' in text.lower():
                # Udtræk tal
                numbers = re.findall(r'(\d+(?:,\d+)?)\s*(?:points?|pts?)', text, re.IGNORECASE)
                if numbers:
                    # Fjern komma og konverter
                    points = int(numbers[0].replace(',', ''))
                    return points
        
        # Metode 2: Find i stats tabeller
        stats = soup.find_all('div', class_='statDiv')
        for stat in stats:
            text = stat.get_text()
            if 'UCI' in text:
                numbers = re.findall(r'(\d{1,4})', text)
                if numbers:
                    for num in numbers:
                        points = int(num)
                        if 0 < points < 10000:  # Sanity check
                            return points
        
        return 0
        
    except Exception as e:
        return 0

def update_all_points(sheet):
    """Hent og opdater UCI points for alle ryttere i sheetet"""
    print(f"\n🚴 Starter opdatering...")
    print("=" * 70)
    
    # Hent alle rækker fra sheetet
    try:
        all_values = sheet.get_all_values()
    except Exception as e:
        print(f"❌ Kunne ikke læse sheet: {e}")
        return 0
    
    updated_count = 0
    total = len(all_values) - 1  # Minus header
    
    # Spring header over (række 1)
    for i, row in enumerate(all_values[1:], start=2):
        if not row or not row[0]:  # Spring tomme rækker over
            continue
        
        rider_name = row[0]
        current_points = row[1] if len(row) > 1 else 0
        
        print(f"[{i-1}/{total}] {rider_name:35s} ", end="", flush=True)
        
        # Søg efter rytteren
        rider_url = search_rider_on_pcs(rider_name)
        
        if not rider_url:
            print(f"❌ Ikke fundet")
            continue
        
        # Hent UCI points
        points = get_rider_uci_points_from_page(rider_url)
        
        if points == 0:
            print(f"⚠️  0 point (eller kunne ikke hente)")
        else:
            print(f"→ {points:4d} point", end="", flush=True)
        
        # Opdater sheetet
        try:
            # Opdater Points2026 kolonne (kolonne B = 2)
            sheet.update_cell(i, 2, points)
            
            # Opdater LastUpdated kolonne (kolonne C = 3)
            today = datetime.now().strftime('%Y-%m-%d')
            sheet.update_cell(i, 3, today)
            
            print(" ✅")
            updated_count += 1
            
        except Exception as e:
            print(f" ❌ Sheet opdatering fejl: {e}")
        
        # Vær høflig - pause mellem requests
        time.sleep(3)
    
    print("=" * 70)
    print(f"✅ Opdatering færdig! {updated_count}/{total} ryttere opdateret")
    return updated_count

def main():
    """Main funktion"""
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - AUTOMATISK UCI POINT OPDATERING")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Forbind til Google Sheets
    sheet = connect_to_sheets()
    if not sheet:
        print("❌ Kunne ikke forbinde til Google Sheets. Afslutter.")
        return
    
    # Opdater alle point
    updated = update_all_points(sheet)
    
    # Status
    print(f"\n{'=' * 70}")
    print(f"🏁 Færdig! {updated} ryttere opdateret")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()
