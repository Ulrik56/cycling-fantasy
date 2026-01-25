"""
Fully Automated UCI Points Updater - WORKING VERSION
Bruger procyclingstats library til at hente UCI Season Ranking
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from procyclingstats import Ranking
from datetime import datetime
import time

# =============================================================================
# KONFIGURATION
# =============================================================================

CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'
SHEET_NAME = 'Cycling Fantasy 2026'
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
        print(f"❌ Fejl: {e}")
        return None

def get_uci_season_ranking():
    """Hent UCI Season Ranking fra ProCyclingStats"""
    print("\n🔍 Henter UCI Season Ranking fra ProCyclingStats...")
    
    try:
        # Brug Ranking klassen
        ranking = Ranking("rankings/me/uci-season-individual")
        
        print("⏳ Parser ranking data...")
        # Kald uden argumenter - får alle default felter
        ranking_data = ranking.individual_ranking()
        
        print(f"✅ Hentet {len(ranking_data)} ryttere!")
        
        # Debug første rytter
        if ranking_data:
            print(f"\n🔍 Data struktur:")
            first = ranking_data[0]
            print(f"   Felter: {list(first.keys())}")
            print(f"   Eksempel: {first}")
        
        # Konverter til dictionary
        points_dict = {}
        for rider in ranking_data:
            rider_name = rider.get('rider_name', '')
            points = rider.get('points', 0)
            
            if isinstance(points, str):
                points = int(points.replace(',', ''))
            
            if rider_name:
                points_dict[rider_name] = int(points)
        
        return points_dict
        
    except Exception as e:
        print(f"❌ Fejl: {e}")
        import traceback
        traceback.print_exc()
        return None

def normalize_name(name):
    """Normaliser navn"""
    return ' '.join(name.split()).upper()

def find_rider_points(rider_name, points_dict):
    """Find point for rytter"""
    # Exact match
    if rider_name in points_dict:
        return points_dict[rider_name]
    
    # Case-insensitive
    normalized = normalize_name(rider_name)
    for rank_name, points in points_dict.items():
        if normalize_name(rank_name) == normalized:
            return points
    
    return None

def update_sheet_with_ranking(sheet, points_dict):
    """Opdater Google Sheet"""
    print("\n🔄 Opdaterer Google Sheet...")
    print("=" * 70)
    
    all_values = sheet.get_all_values()
    updated = 0
    not_found = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for i, row in enumerate(all_values[1:], start=2):
        if not row or not row[0]:
            continue
        
        rider_name = row[0].strip()
        print(f"[{i-1}/{len(all_values)-1}] {rider_name:40s} ", end="", flush=True)
        
        points = find_rider_points(rider_name, points_dict)
        
        if points is not None:
            sheet.update_cell(i, 2, points)
            sheet.update_cell(i, 3, today)
            print(f"→ {points:4d} point ✅")
            updated += 1
        else:
            print(f"❌ Ikke fundet")
            not_found.append(rider_name)
        
        time.sleep(0.5)
    
    print("=" * 70)
    print(f"✅ Opdateret: {updated}/{len(all_values)-1} ryttere")
    
    if not_found:
        print(f"\n⚠️  {len(not_found)} ryttere ikke fundet:")
        for name in not_found[:10]:
            print(f"   - {name}")
    
    return updated

def main():
    """Main funktion"""
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - AUTOMATISK OPDATERING")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    points_dict = get_uci_season_ranking()
    if not points_dict:
        return
    
    print(f"\n📊 Ranking: {len(points_dict)} ryttere")
    
    print("\n🏆 Top 10:")
    top = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (name, pts) in enumerate(top, 1):
        print(f"   {i:2d}. {name:35s} {pts:5d} point")
    
    sheet = connect_to_sheets()
    if not sheet:
        return
    
    updated = update_sheet_with_ranking(sheet, points_dict)
    
    print(f"\n{'=' * 70}")
    print(f"🏁 Færdig! {updated} ryttere opdateret")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()
