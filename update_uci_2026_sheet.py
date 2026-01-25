import re
from datetime import datetime

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# =========================
# KONFIG
# =========================

CREDENTIALS_FILE = "cycling-fantasy-485220-faab21c57cd1.json"

# Dit Google Sheet (fra dit link)
SHEET_KEY = "1RfoTiYhMI-Yr7123evM4_PeSYn87W20UCBerhqV_Ztg"
WORKSHEET_NAME = "Points"   # ret hvis dit faneblad hedder noget andet

# Kolonner i arket:
# A = navn, B = points, C = last updated
NAME_COL = 1
POINTS_COL = 2
UPDATED_COL = 3

# ---- UCI DataRide: Road (disciplineId=10), Men Elite (categoryId=22), Season 2026 (disciplineSeasonId=464)
# World Ranking (rankingId=1) for season 2026. :contentReference[oaicite:1]{index=1}
RANKING_ID = 1
DISCIPLINE_ID = 10
CATEGORY_ID = 22
RACE_TYPE_ID = 0
DISCIPLINE_SEASON_ID = 464

# "Moment" er UCI’s snapshot (opdateringsdato). Denne er fra 19/01/2026. :contentReference[oaicite:2]{index=2}
# Hvis I senere vil have nyere, så find en nyere RankingDetails-URL med nyt momentId og ret her.
MOMENT_ID = 197295

PAGE_SIZE = 200
MAX_SKIP = 20000  # sikkerhedsstop


# =========================
# HELPERS
# =========================

def normalize_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name.strip())
    return name.casefold()

def connect_sheet():
    print("📊 Forbinder til Google Sheets...")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    ws = client.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME)
    print("✅ Forbundet!")
    return ws

def fetch_uci_points_2026():
    """
    Henter hele UCI ranking-listen (2026 season) fra UCI DataRide og returnerer:
    dict[normalized_displayname] = points (float)
    """
    print(f"🌐 Henter UCI points (2026) fra UCI DataRide... (momentId={MOMENT_ID})")

    url = "https://dataride.uci.ch/Results/iframe/ObjectRankings/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://dataride.uci.ch/iframe/RankingDetails/{RANKING_ID}",
    }

    out = {}
    skip = 0

    while skip <= MAX_SKIP:
        data = {
            "rankingId": RANKING_ID,
            "disciplineId": DISCIPLINE_ID,
            "currentRankingTypeId": 1,
            "rankingTypeId": 1,
            "take": PAGE_SIZE,
            "skip": skip,
            "page": (skip // PAGE_SIZE) + 1,
            "pageSize": PAGE_SIZE,

            # filters
            "filter[filters][0][field]": "RaceTypeId",
            "filter[filters][0][value]": RACE_TYPE_ID,
            "filter[filters][1][field]": "CategoryId",
            "filter[filters][1][value]": CATEGORY_ID,
            "filter[filters][2][field]": "SeasonId",
            "filter[filters][2][value]": DISCIPLINE_SEASON_ID,
            "filter[filters][4][value]": 0,

            "momentId": MOMENT_ID,
        }

        r = requests.post(url, headers=headers, data=data, timeout=30)

        if r.status_code != 200:
            raise RuntimeError(f"UCI DataRide request fejlede: HTTP {r.status_code} (skip={skip})\n{r.text[:300]}")

        payload = r.json()
        rows = payload.get("data", [])
        if not rows:
            break

        for item in rows:
            name = (item.get("DisplayName") or "").strip()
            pts = item.get("Points")
            if name and pts is not None:
                out[normalize_name(name)] = float(pts)

        skip += PAGE_SIZE

    print(f"✅ Hentet {len(out)} ryttere fra UCI ranking (2026)")
    return out

def update_sheet(ws, uci_points: dict):
    print("🔄 Opdaterer sheet (batch)...")

    all_values = ws.get_all_values()
    if len(all_values) < 2:
        print("⚠️ Sheet har ingen data-rækker (kun header/eller tomt).")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")

    points_col = []
    updated_col = []

    updated_count = 0
    missing = []

    for row in all_values[1:]:
        name = ""
        if row and len(row) >= NAME_COL and row[NAME_COL - 1]:
            name = row[NAME_COL - 1].strip()

        if not name:
            points_col.append([""])
            updated_col.append([""])
            continue

        key = normalize_name(name)
        pts = uci_points.get(key, 0.0)

        # hvis du vil have heltal i sheet, brug: int(round(pts))
        points_col.append([pts])
        updated_col.append([today])

        if pts > 0:
            updated_count += 1
        else:
            missing.append(name)

    last_row = len(all_values)
    ws.update(f"B2:B{last_row}", points_col, value_input_option="USER_ENTERED")
    ws.update(f"C2:C{last_row}", updated_col, value_input_option="USER_ENTERED")

    print(f"✅ Sat points for alle rækker. ({updated_count} ryttere havde >0 points)")
    if missing:
        print(f"ℹ️ {len(missing)} ryttere fik 0 points (enten 0 i 2026 eller navn-match). Eksempel: {missing[:8]}")
    return updated_count

def main():
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - AUTO UCI 2026 POINTS → GOOGLE SHEET")
    print("=" * 70)

    ws = connect_sheet()
    uci_points = fetch_uci_points_2026()
    update_sheet(ws, uci_points)

    print("\n" + "=" * 70)
    print("🏁 Færdig!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
