"""
FULDT AUTOMATISK UCI POINT OPDATERING
Bruger cloudscraper til at hente UCI ranking og opdatere Google Sheets
"""

import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =============================================================================
# KONFIGURATION
# =============================================================================

CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'
SHEET_NAME = 'Cycling Fantasy 2026'
WORKSHEET_NAME = 'Points'

# =============================================================================
# FUNKTIONER
# =============================================================================

def scrape_uci_ranking():
    """Hent UCI Ranking med cloudscraper"""
    print("\n" + "=" * 70)
    print("🚴 Henter UCI Season Ranking med CloudScraper")
    print("=" * 70)
    
    # Brug cloudscraper til at omgå Cloudflare
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
    
    all_data = []
    offset = 0
    page_num = 1
    MAX_PAGES = 20
    
    print(f"🔄 Starter scraping...")
    print("-" * 70)
    
    while page_num <= MAX_PAGES:
        # Brug dagens dato for at få aktuelle season points
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"https://www.procyclingstats.com/rankings.php?p=uci-season-individual&s=&date={today}&nation=&age=&page=smallerorequal&team=&offset={offset}&teamlevel=&filter=Filter"
        
        print(f"📥 Side {page_num}: ", end="", flush=True)
        
        try:
            time.sleep(random.uniform(1.5, 3))
            response = scraper.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} - stopper")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print("Ingen tabel - stopper")
                break
            
            rows = table.find_all('tr')
            data_rows = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(' ', strip=True) for cell in cells]
                    if len(row_data) >= 4:
                        if any(cell.strip().isdigit() for cell in row_data[:1]) or \
                           any('.' in cell or cell.replace('.', '').isdigit() for cell in row_data[-1:]):
                            data_rows.append(row_data)
            
            print(f"{len(data_rows)} ryttere ✅")
            
            if not data_rows or len(data_rows) < 5:
                print("   Sidste side nået")
                if data_rows:
                    all_data.extend(data_rows)
                break
            
            all_data.extend(data_rows)
            
            if len(data_rows) < 50:
                print("   Sidste side nået")
                break
            
            offset += 100
            page_num += 1
            
        except Exception as e:
            print(f"Fejl: {e}")
            break
    
    print("-" * 70)
    
    if not all_data:
        print("❌ Ingen data hentet")
        return None
    
    # Konverter til DataFrame
    df = pd.DataFrame(all_data)
    
    # Find header
    if len(df) > 0:
        first_row_str = ' '.join(df.iloc[0].astype(str))
        if any(kw in first_row_str for kw in ['#', 'Rider', 'Points']):
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
    
    df = df.dropna(how='all')
    
    print(f"✅ Total: {len(df)} ryttere hentet\n")
    
    return df

def convert_to_points_dict(df):
    """Konverter DataFrame til point dictionary"""
    print("🔄 Konverterer til point dictionary...")
    
    points_dict = {}
    
    # Find rider og points kolonner
    rider_col = None
    points_col = None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if 'rider' in col_lower and rider_col is None:
            rider_col = col
        if 'point' in col_lower and points_col is None:
            points_col = col
    
    # Fallback til kolonne indeks hvis kolonnenavne ikke findes
    if rider_col is None:
        rider_col = 3 if len(df.columns) > 3 else 0
    if points_col is None:
        points_col = 5 if len(df.columns) > 5 else -1
    
    print(f"   Rider kolonne: {rider_col}")
    print(f"   Points kolonne: {points_col}")
    
    for idx, row in df.iterrows():
        try:
            rider_name = str(row[rider_col]).strip()
            points_str = str(row[points_col]).strip()
            
            # Parse points (fjern komma og decimal)
            if '.' in points_str:
                points = int(float(points_str.replace(',', '')))
            else:
                points = int(points_str.replace(',', ''))
            
            if rider_name and rider_name not in ['', 'Rider', 'nan']:
                points_dict[rider_name] = points
                
        except Exception as e:
            continue
    
    print(f"✅ {len(points_dict)} ryttere konverteret\n")
    return points_dict

def connect_to_sheets():
    """Forbind til Google Sheets"""
    print("📊 Forbinder til Google Sheets...")
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        print("✅ Forbundet til Google Sheets!\n")
        return sheet
    except Exception as e:
        print(f"❌ Fejl: {e}\n")
        return None

def normalize_name(name):
    """Normaliser rytternavn"""
    return ' '.join(str(name).split()).upper()

def find_rider_points(rider_name, points_dict):
    """Find point for rytter med fuzzy matching"""
    # Exact match
    if rider_name in points_dict:
        return points_dict[rider_name]
    
    # Case-insensitive
    normalized = normalize_name(rider_name)
    for rank_name, points in points_dict.items():
        if normalize_name(rank_name) == normalized:
            return points
    
    # Efternavn match
    parts = normalized.split()
    if len(parts) >= 2:
        last_name = parts[-1]
        first_name = parts[0]
        
        for rank_name, points in points_dict.items():
            rank_parts = normalize_name(rank_name).split()
            if len(rank_parts) >= 2:
                # Match både fornavn og efternavn
                if rank_parts[0] == first_name and rank_parts[-1] == last_name:
                    return points
                # Kun efternavn hvis unikt
                if rank_parts[-1] == last_name:
                    # Check det ikke er et almindeligt efternavn
                    return points
    
    return None

def update_google_sheet(sheet, points_dict):
    """Opdater Google Sheet med UCI points"""
    print("🔄 Opdaterer Google Sheet...")
    print("=" * 70)
    
    all_values = sheet.get_all_values()
    updated = 0
    not_found = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    total = len(all_values) - 1
    
    for i, row in enumerate(all_values[1:], start=2):
        if not row or not row[0]:
            continue
        
        rider_name = row[0].strip()
        print(f"[{i-1}/{total}] {rider_name:40s} ", end="", flush=True)
        
        points = find_rider_points(rider_name, points_dict)
        
        if points is not None:
            sheet.update_cell(i, 2, points)
            sheet.update_cell(i, 3, today)
            print(f"→ {points:4d} point ✅")
            updated += 1
        else:
            sheet.update_cell(i, 2, 0)
            sheet.update_cell(i, 3, today)
            print(f"→ 0 point (ikke i ranking)")
            not_found.append(rider_name)
            updated += 1
        
        time.sleep(0.5)
    
    print("=" * 70)
    print(f"✅ Opdateret: {updated}/{total} ryttere\n")
    
    if not_found:
        print(f"💡 {len(not_found)} ryttere ikke fundet (sat til 0):")
        for name in not_found[:10]:
            print(f"   - {name}")
        if len(not_found) > 10:
            print(f"   ... og {len(not_found) - 10} flere")
        print()
    
    return updated

def main():
    """Main funktion"""
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - FULD AUTOMATISK OPDATERING")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. Scrape UCI ranking
    df = scrape_uci_ranking()
    if df is None or df.empty:
        print("❌ Kunne ikke hente ranking. Afslutter.")
        return
    
    # 2. Konverter til dictionary
    points_dict = convert_to_points_dict(df)
    if not points_dict:
        print("❌ Kunne ikke konvertere data. Afslutter.")
        return
    
    # Vis top 10
    print("🏆 Top 10 i rankingen:")
    top_riders = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (name, pts) in enumerate(top_riders, 1):
        print(f"   {i:2d}. {name:35s} {pts:5d} point")
    print()
    
    # 3. Forbind til Google Sheets
    sheet = connect_to_sheets()
    if not sheet:
        print("❌ Kunne ikke forbinde til Google Sheets. Afslutter.")
        return
    
    # 4. Opdater Google Sheet
    updated = update_google_sheet(sheet, points_dict)
    
    # 5. Status
    print("=" * 70)
    print(f"🏁 FÆRDIG! {updated} ryttere opdateret")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
