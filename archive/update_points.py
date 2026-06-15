"""
Automated UCI Points Updater for Cycling Fantasy Manager
Henter point fra ProCyclingStats og opdaterer Google Sheets automatisk
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from procyclingstats import Rider
import time
from datetime import datetime

# =============================================================================
# KONFIGURATION - ERSTAT DISSE VÆRDIER
# =============================================================================

# Sti til din Google credentials JSON fil
CREDENTIALS_FILE = 'cycling-fantasy-485220-faab21c57cd1.json'  # ERSTAT MED DIN FIL

# Dit Google Sheet navn
SHEET_NAME = 'Cycling Fantasy 2026'

# Worksheet navn (fanen i sheetet)
WORKSHEET_NAME = 'Points'

# Mapping af rytternavne til ProCyclingStats URL slugs
# Find slugs ved at søge på procyclingstats.com og kopiere fra URL
RIDER_URLS = {
    # Team Døssing
    "EVENEPOEL Remco": "rider/remco-evenepoel",
    "PHILIPSEN Jasper": "rider/jasper-philipsen",
    "ROGLIČ Primož": "rider/primoz-roglic",
    "GIRMAY Biniam": "rider/biniam-girmay",
    "HIRSCHI Marc": "rider/marc-hirschi",
    "SEIXAS Paul": "rider/paul-seixas",
    "MAS NICOLAU Enric": "rider/enric-mas",
    "O'CONNOR Ben": "rider/ben-oconnor",
    "UIJTDEBROEKS Cian": "rider/cian-uijtdebroeks",
    "KÜNG Stefan": "rider/stefan-kung",
    "PHILIPSEN Albert": "rider/albert-philipsen",
    "VAN GILS Maxim": "rider/maxim-van-gils",
    "GAUDU David": "rider/david-gaudu",
    "MOHORIC Matej": "rider/matej-mohoric",
    "RODRIGUEZ CANO Carlos": "rider/carlos-rodriguez",
    "LAPORTE Christophe": "rider/christophe-laporte",
    "MARTINEZ POVEDA Daniel Felipe": "rider/daniel-martinez",
    "VLASOV Aleksandr": "rider/aleksandr-vlasov",
    "ASGREEN Kasper": "rider/kasper-asgreen",
    "VALTER Attila": "rider/attila-valter",
    
    # Team Vester
    "VAUQUELIN Kévin": "rider/kevin-vauquelin",
    "BRENNAN Matthew": "rider/matthew-brennan",
    "TIBERI Antonio": "rider/antonio-tiberi",
    "RICCITELLO Matthew": "rider/matthew-riccitello",
    "LAPEIRA Paul": "rider/paul-lapeira",
    "LECERF Junior": "rider/junior-lecerf",
    "WIDAR Jarno": "rider/jarno-widar",
    "VAN EETVELT Lennert": "rider/lennert-van-eetvelt",
    "COSNEFROY Benoit": "rider/benoit-cosnefroy",
    "OMRZEL Jakob": "rider/jakob-omrzel",
    "BISIAUX Léo": "rider/leo-bisiaux",
    "AGOSTINACCHIO Mattia": "rider/mattia-agostinacchio",
    "KRON Andreas Lorentz": "rider/andreas-kron",
    
    # Team Peter
    "VINGEGAARD HANSEN Jonas": "rider/jonas-vingegaard",
    "ONLEY Oscar": "rider/oscar-onley",
    "LUND ANDRESEN Tobias": "rider/tobias-lund-andresen",
    "KUBIŠ Lukáš": "rider/lukas-kubis",
    "NIELSEN Magnus Cort": "rider/magnus-cort",
    "DE BONDT Dries": "rider/dries-de-bondt",
    "POOLE Max David": "rider/max-poole",
    "NORDHAGEN Jørgen": "rider/jorgen-nordhagen",
    "LAMPERTI Luke": "rider/luke-lamperti",
    "TEUTENBERG Tim Torn": "rider/tim-torn-teutenberg",
    "MOLARD Rudy": "rider/rudy-molard",
    "LEMMEN Bart": "rider/bart-lemmen",
    "HELLEMOSE Asbjørn": "rider/asbjorn-hellemose",
    
    # Kasper Krabber
    "VAN AERT Wout": "rider/wout-van-aert",
    "MAGNIER Paul": "rider/paul-magnier",
    "GANNA Filippo": "rider/filippo-ganna",
    "ARENSMAN Thymen": "rider/thymen-arensman",
    "SIMMONS Quinn": "rider/quinn-simmons",
    "TOMAS MORGADO António": "rider/antonio-morgado",
    "NYS Thibau": "rider/thibau-nys",
    "DEL GROSSO Tibor": "rider/tibor-del-grosso",
    "VACEK Mathias": "rider/mathias-vacek",
    "SÖDERQVIST Jakob": "rider/jakob-soderqvist",
    "VAN BAARLE Dylan": "rider/dylan-van-baarle",
    "ZINGLE Axel": "rider/axel-zingle",
    
    # T-Dawgs Dogs
    "DEL TORO ROMERO Isaac": "rider/isaac-del-toro",
    "PELLIZZARI Giulio": "rider/giulio-pellizzari",
    "DAINESE Alberto": "rider/alberto-dainese",
    "BLACKMORE Joseph": "rider/joseph-blackmore",
    "PERICAS CAPDEVILA Adria": "rider/adria-pericas",
    "TORRES ARIAS Pablo": "rider/pablo-torres",
    
    # Gewiss Allan
    "KOOIJ Olav": "rider/olav-kooij",
    "MERLIER Tim": "rider/tim-merlier",
    "LANDA MEANA Mikel": "rider/mikel-landa",
    "RONDEL Mathys": "rider/mathys-rondel",
    "SEGAERT Alec": "rider/alec-segaert",
    "FOLDAGER Anders": "rider/anders-foldager",
    "BJERG Mikkel Norsgaard": "rider/mikkel-bjerg",
    "HANSEN Peter": "rider/peter-hansen",
    
    # Don Karnage
    "DE LIE Arnaud": "rider/arnaud-de-lie",
    "BITTNER Pavel": "rider/pavel-bittner",
    "VAN WILDER Ilan": "rider/ilan-van-wilder",
    "GROENEWEGEN Dylan": "rider/dylan-groenewegen",
    "KRAGH ANDERSEN Søren": "rider/soren-kragh-andersen",
    "GAVIRIA RENDON Fernando": "rider/fernando-gaviria",
}

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

def get_rider_uci_points(rider_url):
    """Hent UCI points for en rytter"""
    try:
        rider = Rider(rider_url)
        data = rider.parse()
        return data.get('uci_points', 0)
    except Exception as e:
        print(f"   ⚠️  Fejl: {e}")
        return 0

def update_all_points(sheet):
    """Hent og opdater UCI points for alle ryttere"""
    print(f"\n🚴 Starter opdatering af {len(RIDER_URLS)} ryttere...")
    print("=" * 70)
    
    updated_count = 0
    total = len(RIDER_URLS)
    
    for i, (rider_name, rider_url) in enumerate(RIDER_URLS.items(), 1):
        print(f"[{i}/{total}] {rider_name:35s} ", end="", flush=True)
        
        # Hent UCI points
        points = get_rider_uci_points(rider_url)
        print(f"→ {points:4d} point", end="", flush=True)
        
        # Find rækken i sheetet
        try:
            cell = sheet.find(rider_name)
            row = cell.row
            
            # Opdater Points2026 kolonne (kolonne B = 2)
            sheet.update_cell(row, 2, points)
            
            # Opdater LastUpdated kolonne (kolonne C = 3)
            today = datetime.now().strftime('%Y-%m-%d')
            sheet.update_cell(row, 3, today)
            
            print(" ✅")
            updated_count += 1
            
        except gspread.exceptions.CellNotFound:
            print(f" ❌ Ikke fundet i sheet")
        except Exception as e:
            print(f" ❌ Fejl: {e}")
        
        # Vær høflig - pause mellem requests
        time.sleep(2)
    
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
