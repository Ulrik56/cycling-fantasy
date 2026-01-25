"""
Fully Automated UCI Points Updater
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

CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'  # ERSTAT MED DIN FIL
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
        # Brug Ranking klassen til at hente season ranking
        # URL format: "rankings/me/uci-season-individual"
        ranking = Ranking("rankings/me/uci-season-individual")
        
        print("⏳ Parser ranking data...")
        # Hent ranking tabel
        ranking_data = ranking.individual_ranking(
            'rank', 'prev_rank', 'rider_name', 'rider_url', 
            'team_name', 'points', 'age', 'nationality'
        )
        
        print(f"✅ Hentet {len(ranking_data)} ryttere fra ranking!")
        
        # Konverter til dictionary for hurtig lookup
        points_dict = {}
        for rider in ranking_data:
            rider_name = rider.get('rider_name', '')
            points = rider.get('points', 0)
            
            # Prøv at parse points hvis det er en string
            if isinstance(points, str):
                try:
                    points = int(points.replace(',', ''))
                except:
                    points = 0
            
            if rider_name:
                points_dict[rider_name] = points
        
        return points_dict
        
    except Exception as e:
        print(f"❌ Fejl ved hentning af ranking: {e}")
        print(f"   Fejl type: {type(e).__name__}")
        return None

def normalize_name(name):
    """Normaliser rytternavn for matching"""
    # Fjern ekstra mellemrum
    name = ' '.join(name.split())
    # Konverter til uppercase
    name = name.upper()
    return name

def find_rider_points(rider_name, points_dict):
    """Find point for en rytter i ranking data"""
    # Prøv exact match først
    if rider_name in points_dict:
        return points_dict[rider_name]
    
    # Prøv case-insensitive match
    normalized = normalize_name(rider_name)
    for rank_name, points in points_dict.items():
        if normalize_name(rank_name) == normalized:
            return points
    
    # Prøv partial match (efternavn)
    parts = normalized.split()
    if len(parts) >= 2:
        last_name = parts[-1]
        for rank_name, points in points_dict.items():
            if last_name in normalize_name(rank_name):
                return points
    
    return None

def update_sheet_with_ranking(sheet, points_dict):
    """Opdater Google Sheet med ranking data"""
    print("\n🔄 Opdaterer Google Sheet...")
    print("=" * 70)
    
    # Hent alle værdier fra sheet
    all_values = sheet.get_all_values()
    
    updated = 0
    not_found = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Spring header over (række 1)
    for i, row in enumerate(all_values[1:], start=2):
        if not row or not row[0]:
            continue
        
        rider_name = row[0].strip()
        print(f"[{i-1}/{len(all_values)-1}] {rider_name:40s} ", end="", flush=True)
        
        # Find point
        points = find_rider_points(rider_name, points_dict)
        
        if points is not None:
            # Opdater Points2026 (kolonne B)
            sheet.update_cell(i, 2, points)
            # Opdater LastUpdated (kolonne C)
            sheet.update_cell(i, 3, today)
            
            print(f"→ {points:4d} point ✅")
            updated += 1
        else:
            print(f"❌ Ikke fundet i ranking")
            not_found.append(rider_name)
        
        # Lille pause for at undgå rate limiting
        time.sleep(0.5)
    
    print("=" * 70)
    print(f"✅ Opdateret: {updated}/{len(all_values)-1} ryttere")
    
    if not_found:
        print(f"\n⚠️  {len(not_found)} ryttere ikke fundet:")
        for name in not_found[:10]:
            print(f"   - {name}")
        if len(not_found) > 10:
            print(f"   ... og {len(not_found) - 10} flere")
        print("\n💡 Tip: Disse ryttere har sandsynligvis 0 point eller er ikke i top rankingen")
    
    return updated

def main():
    """Main funktion"""
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - FULD AUTOMATISK OPDATERING")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Hent UCI ranking
    points_dict = get_uci_season_ranking()
    if not points_dict:
        print("❌ Kunne ikke hente ranking. Afslutter.")
        return
    
    print(f"\n📊 Ranking indeholder {len(points_dict)} ryttere")
    
    # Vis top 10 for at verificere
    print("\n🏆 Top 10 i rankingen:")
    top_riders = sorted(points_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (name, pts) in enumerate(top_riders, 1):
        print(f"   {i:2d}. {name:35s} {pts:5d} point")
    
    # Forbind til Google Sheets
    sheet = connect_to_sheets()
    if not sheet:
        print("❌ Kunne ikke forbinde til Google Sheets. Afslutter.")
        return
    
    # Opdater sheet
    updated = update_sheet_with_ranking(sheet, points_dict)
    
    # Status
    print(f"\n{'=' * 70}")
    print(f"🏁 Færdig! {updated} ryttere opdateret")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    main()
