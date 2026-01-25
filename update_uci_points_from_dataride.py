import re
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# =========================
# KONFIG
# =========================

CREDENTIALS_FILE = "cycling-fantasy-485220-faab21c57cd1.json"

# Dit Google Sheet
SHEET_KEY = "1RfoTiYhMI-Yr7123evM4_PeSYn87W20UCBerhqV_Ztg"
WORKSHEET_NAME = "Points"   # ret hvis fanen hedder noget andet

# Sæt DEN ranking du vil bruge her:
# Tip: Åbn den ønskede ranking i browseren og copy/paste URL'en her.
RANKING_DETAILS_URL = (
    "https://dataride.uci.ch/iframe/RankingDetails/11?"
    "categoryId=22&disciplineId=10&disciplineSeasonId=464&groupId=8&momentId=196898&raceTypeId=0&rankingTypeId=3"
)

PAGE_SIZE = 200
SLEEP_BETWEEN_PAGES = 0.2

# Prøv flere endpoints automatisk (DataRide flytter nogle gange rundt)
CANDIDATE_ENDPOINTS = [
    "https://dataride.uci.ch/Results/iframe/ObjectRankings/",
    "https://dataride.uci.ch/Results/iframe/ObjectRankings",
    "https://dataride.uci.ch/iframe/ObjectRankings/",
    "https://dataride.uci.ch/iframe/ObjectRankings",
]


# =========================
# HELPERS
# =========================

def normalize_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name.strip())
    return name.casefold()

def parse_ranking_details_url(url: str) -> dict:
    """
    Udtrækker:
    - rankingId (fra path)
    - query params: categoryId, disciplineId, disciplineSeasonId, groupId, momentId, raceTypeId, rankingTypeId
    """
    u = urlparse(url)
    qs = parse_qs(u.query)

    # rankingId ligger i path: /iframe/RankingDetails/<ID>
    m = re.search(r"/RankingDetails/(\d+)", u.path)
    if not m:
        raise ValueError("Kunne ikke finde RankingDetails/<id> i URL'en.")
    ranking_id = int(m.group(1))

    def get_int(key, default=None):
        if key not in qs or not qs[key]:
            if default is None:
                raise ValueError(f"Mangler '{key}' i URL querystring.")
            return default
        return int(qs[key][0])

    return {
        "rankingId": ranking_id,
        "categoryId": get_int("categoryId"),
        "disciplineId": get_int("disciplineId"),
        "disciplineSeasonId": get_int("disciplineSeasonId"),
        "groupId": get_int("groupId", 1),
        "momentId": get_int("momentId"),
        "raceTypeId": get_int("raceTypeId", 0),
        "rankingTypeId": get_int("rankingTypeId", 3),
    }

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


# =========================
# UCI DataRide hentning
# =========================

def _build_request_payload(params: dict, skip: int) -> dict:
    return {
        "rankingId": params["rankingId"],
        "disciplineId": params["disciplineId"],
        "currentRankingTypeId": 1,
        "rankingTypeId": params["rankingTypeId"],

        "take": PAGE_SIZE,
        "skip": skip,
        "page": (skip // PAGE_SIZE) + 1,
        "pageSize": PAGE_SIZE,

        # Filtre (som DataRide normalt forventer)
        "filter[filters][0][field]": "RaceTypeId",
        "filter[filters][0][value]": params["raceTypeId"],
        "filter[filters][1][field]": "CategoryId",
        "filter[filters][1][value]": params["categoryId"],
        "filter[filters][2][field]": "SeasonId",
        "filter[filters][2][value]": params["disciplineSeasonId"],
        "filter[filters][4][value]": 0,

        "momentId": params["momentId"],
        "groupId": params["groupId"],
    }

def fetch_uci_points(params: dict) -> dict:
    """
    Henter ranking-data fra UCI DataRide ObjectRankings endpoint.
    Return: normalized_name -> points (float)
    """
    print("🌐 Henter UCI points fra DataRide...")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": RANKING_DETAILS_URL,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    last_error = None

    for endpoint in CANDIDATE_ENDPOINTS:
        try:
            out = {}
            skip = 0
            pages = 0

            while True:
                payload = _build_request_payload(params, skip)

                r = requests.post(endpoint, headers=headers, data=payload, timeout=30)

                # Hvis endpoint ikke findes/ikke accepterer POST, prøv næste
                if r.status_code in (404, 405):
                    raise RuntimeError(f"Endpoint fejler ({r.status_code})")

                r.raise_for_status()

                # Nogle gange kan man få HTML fejlside -> så vil .json() fejle
                data = r.json()

                rows = data.get("data", [])
                if not rows:
                    break

                for item in rows:
                    name = (item.get("DisplayName") or "").strip()
                    pts = item.get("Points")
                    if name and pts is not None:
                        out[normalize_name(name)] = float(pts)

                skip += PAGE_SIZE
                pages += 1
                time.sleep(SLEEP_BETWEEN_PAGES)

                # sikkerhedsstop
                if pages > 400:
                    break

            # Hvis vi faktisk fik data, er endpointet OK
            if out:
                print(f"✅ Endpoint OK: {endpoint}")
                print(f"✅ Hentet {len(out)} ryttere med points fra DataRide")
                return out

            # 200 OK men 0 data kan betyde forkert kombination af params
            last_error = RuntimeError(f"200 OK men 0 data fra {endpoint}")

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(
        "Kunne ikke hente data fra UCI DataRide.\n"
        f"Sidste fejl: {last_error}\n"
        "Tip: Tjek at RANKING_DETAILS_URL kan åbnes i din browser og viser den ranking du vil bruge."
    )


# =========================
# Sheet opdatering
# =========================

def update_sheet(ws, points_by_name: dict):
    print("🔄 Opdaterer sheet (batch)...")

    all_values = ws.get_all_values()
    if len(all_values) < 2:
        print("⚠️ Sheet har ingen data-rækker.")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")

    points_col = []
    updated_col = []

    updated = 0
    missing = []

    for row in all_values[1:]:  # skip header
        rider = row[0].strip() if row and row[0] else ""
        if not rider:
            points_col.append([""])
            updated_col.append([""])
            continue

        key = normalize_name(rider)
        pts = points_by_name.get(key)

        if pts is None:
            # Hvis ikke fundet: sæt 0 og opdater dato
            points_col.append([0])
            updated_col.append([today])
            missing.append(rider)
        else:
            points_col.append([pts])
            updated_col.append([today])
            updated += 1

    last_row = len(all_values)

    # Batch update (2 writes i alt)
    ws.update(f"B2:B{last_row}", points_col, value_input_option="USER_ENTERED")
    ws.update(f"C2:C{last_row}", updated_col, value_input_option="USER_ENTERED")

    print(f"✅ Opdateret {updated} ryttere med points fundet i DataRide")
    if missing:
        print(f"ℹ️ {len(missing)} ryttere ikke matchet → sat til 0 (eksempel: {missing[:10]})")

    return updated


# =========================
# Main
# =========================

def main():
    print("\n" + "=" * 70)
    print("🚴 CYCLING FANTASY - AUTO UCI POINTS (DataRide) → GOOGLE SHEET")
    print("=" * 70)

    params = parse_ranking_details_url(RANKING_DETAILS_URL)
    print("🔎 Bruger ranking parametre:", params)

    ws = connect_sheet()
    points = fetch_uci_points(params)
    updated = update_sheet(ws, points)

    print("\n" + "=" * 70)
    print(f"🏁 Færdig! ({updated} ryttere opdateret med points)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
