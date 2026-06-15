"""
Cycling Fantasy Manager - Semi-Automatisk Opdatering
Du kopierer data fra ProCyclingStats, scriptet opdaterer Google Sheet
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import csv  # (bruges ikke lige nu, men beholdt for kompatibilitet)

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

def read_points_from_file(filename='rider_points.txt'):
    """Læs point fra tekstfil"""
    points_dict = {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Format: "EVENEPOEL Remco: 245" eller "EVENEPOEL Remco,245"
                if ':' in line:
                    parts = line.split(':', 1)
                elif ',' in line:
                    parts = line.split(',', 1)
                elif '\t' in line:
                    parts = line.split('\t', 1)
                else:
                    continue

                if len(parts) >= 2:
                    rider_name = parts[0].strip()
                    try:
                        pts = int(parts[1].strip())
                        points_dict[rider_name] = pts
                    except ValueError:
                        continue

        print(f"✅ Læst {len(points_dict)} ryttere fra {filename}")
        return points_dict

    except FileNotFoundError:
        print(f"❌ Fil ikke fundet: {filename}")
        print(f"\n📝 Opret en fil kaldet '{filename}' med dette format:")
        print("   EVENEPOEL Remco: 245")
        print("   PHILIPSEN Jasper: 189")
        print("   osv...")
        return None

def update_sheet_with_points(sheet, points_dict):
    """Opdater Google Sheet med point (batch update for at undgå 429 quota)"""
    print("\n🔄 Opdaterer Google Sheet...")

    # Hent alle værdier fra sheet (inkl header)
    all_values = sheet.get_all_values()
    updated = 0
    not_found = []

    if len(all_values) < 2:
        print("⚠️  Ingen datarækker fundet (kun header eller tomt ark).")
        return 0

    today = datetime.now().strftime('%Y-%m-%d')

    # Byg nye kolonne-værdier til B og C for alle rækker (starter fra række 2)
    # Bemærk: vi opdaterer kun rækker med navn i kolonne A; tomme rækker bevares tomme.
    points_col = []
    updated_col = []

    for row in all_values[1:]:  # Skip header (række 1)
        rider_name = (row[0].strip() if row and len(row) > 0 and row[0] else "")

        if not rider_name:
            points_col.append([""])
            updated_col.append([""])
            continue

        if rider_name in points_dict:
            pts = points_dict[rider_name]
            points_col.append([pts])
            updated_col.append([today])
            print(f"✅ {rider_name:40s} → {pts:4d} point")
            updated += 1
        else:
            # Hvis rytter ikke findes i datafilen, så behold eksisterende værdier i B og C
            existing_points = row[1] if len(row) > 1 else ""
            existing_updated = row[2] if len(row) > 2 else ""
            points_col.append([existing_points])
            updated_col.append([existing_updated])
            not_found.append(rider_name)

    last_row = len(all_values)  # total rows inkl header
    # Batch update: 2 writes (B-kolonne og C-kolonne) i stedet for 2 pr rytter
    sheet.update(f"B2:B{last_row}", points_col, value_input_option="USER_ENTERED")
    sheet.update(f"C2:C{last_row}", updated_col, value_input_option="USER_ENTERED")

    print(f"\n✅ Opdateret {updated} ryttere")

    if not_found:
        print(f"\n⚠️  {len(not_found)} ryttere ikke fundet i datafilen (beholder eksisterende værdier i sheet):")
        for name in not_found[:10]:  # Vis kun første 10
            print(f"   - {name}")
        if len(not_found) > 10:
            print(f"   ... og {len(not_found) - 10} flere")

    return updated

def main():
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - SEMI-AUTOMATISK OPDATERING")
    print("=" * 70)
    print(f"⏰ Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Forbind til sheets
    sheet = connect_to_sheets()
    if not sheet:
        return

    # Læs point fra fil
    points = read_points_from_file('rider_points.txt')
    if not points:
        return

    # Opdater sheet
    updated = update_sheet_with_points(sheet, points)

    print("\n" + "=" * 70)
    print(f"🏁 Færdig! {updated} ryttere opdateret")
    print(f"⏰ Sluttid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
