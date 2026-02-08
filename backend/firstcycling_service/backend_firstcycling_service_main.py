from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re
import os
from typing import List, Dict

# Import fra firstcycling-mcp (installeret via requirements)
# package path i repo: first_cycling_api
try:
    from first_cycling_api.rider.rider import Rider
    from first_cycling_api.api import FirstCyclingAPI
except Exception as e:
    # Giver en klar fejl hvis pakken ikke er installeret korrekt
    raise RuntimeError(
        "Kunne ikke importere first_cycling_api. Har du installeret dependency fra GitHub? "
        "Kør: pip install -r requirements.txt"
    ) from e

app = FastAPI(title="FirstCycling proxy for Cycling-Fantasy")

fc_api = FirstCyclingAPI()

def _safe_text(el):
    return el.text.strip() if el else None

def _parse_rider_from_html(html: bytes) -> Dict:
    soup = BeautifulSoup(html, "lxml")

    # navn
    h1 = soup.find("h1")
    name = h1.text.strip() if h1 else None

    # prøv at finde team (ofte et <a href="team.php?...">Team Name</a>)
    team = None
    team_link = soup.find("a", href=re.compile(r"team\.php"))
    if team_link:
        team = team_link.text.strip()

    # nationality - ofte vist som en <img alt="NAT" ...> eller tekst nær navnet
    nationality = None
    # tjek for img med alt som landekode
    flag_img = soup.find("img", alt=re.compile(r"^[A-Z]{2,3}$"))
    if flag_img and flag_img.has_attr("alt"):
        nationality = flag_img["alt"].strip()
    else:
        # alternativ: find en lille tekst eller span efter navnet
        possible = soup.find(text=re.compile(r"[A-Z]{2,3}"))
        if possible:
            nationality = possible.strip()

    # forsøg at finde rytterbillede
    image_url = None
    # almindelige mønstre: <img class="rider" ...>, eller store billeder i en div
    selectors = [
        {"name": "img", "attrs": {"class": re.compile(r"rider|avatar|photo", re.I)}},
        {"name": "img", "attrs": {"src": re.compile(r"rider|riders|photos", re.I)}},
    ]
    for sel in selectors:
        img = soup.find(sel["name"], attrs=sel["attrs"])
        if img and img.has_attr("src"):
            image_url = img["src"]
            break

    # hvis image_url er relativ (starter ikke med http), gør det absolut mod førstecycling base
    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url
    if image_url and image_url.startswith("/"):
        image_url = "https://firstcycling.com" + image_url

    # simple ekstra info: fødselsdato (ofte i en <li> eller <p> med fødselsdato)
    dob = None
    dob_match = soup.find(text=re.compile(r"Date of birth|Født|Born", re.I))
    if dob_match:
        # hent linje eller næste element tekst (simpelt)
        parent = dob_match.parent
        if parent:
            txt = parent.text.strip()
            # strip label
            dob = re.sub(r"Date of birth[:\s]*", "", txt, flags=re.I)

    return {
        "name": name,
        "team": team,
        "nationality": nationality,
        "image_url": image_url,
        "dob": dob,
    }

@app.get("/search_rider", response_class=JSONResponse)
async def search_rider(q: str):
    """
    Search riders by name.
    Example: /search_rider?q=pogacar
    Returns a list of matches with id, name, nationality, team (where available).
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query 'q' is required and should be at least 2 characters")

    try:
        matches = Rider.search(q)
    except Exception as e:
        # fallback: use FirstCyclingAPI search (if available)
        try:
            html = fc_api.search_race(query=q)
            # hvis denne call ikke passer til ryttere, returner tomt
            return {"results": []}
        except Exception:
            raise HTTPException(status_code=500, detail=f"Søgning fejlede: {str(e)}")

    # forvente en liste af dicts; map til enkel struktur
    out = []
    for m in matches:
        entry = {
            "id": m.get("id") or m.get("ID") or m.get("RiderID"),
            "name": m.get("name") or m.get("Name") or m.get("text"),
            "nationality": m.get("country") or m.get("nationality"),
            "team": m.get("team"),
        }
        out.append(entry)
    return {"results": out}

@app.get("/rider/{rider_id}", response_class=JSONResponse)
async def get_rider(rider_id: int):
    """
    Get basic rider info for a given FirstCycling rider ID.
    Example: /rider/16973
    """
    try:
        rider = Rider(rider_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fejl ved oprettelse af Rider: {str(e)}")

    # Første forsøg: brug rider.year_results() som ofte loader side og header_details
    try:
        year_results = rider.year_results()
        # header_details bor ofte i det returnerede objekt
        header = getattr(year_results, "header_details", None)
        if header and isinstance(header, dict) and header.get("name"):
            result = {
                "id": rider_id,
                "name": header.get("name"),
                "team": header.get("team"),
                "nationality": header.get("country"),
            }
            # forsøg finde billede i header (hvis der)
            if header.get("image"):
                result["image_url"] = header.get("image")
            else:
                # fallback: parse HTML
                html = fc_api.get_rider_endpoint(rider_id)
                parsed = _parse_rider_from_html(html)
                result.update(parsed)
            return result
    except Exception:
        # ikke kritisk — fortsæt med HTML fallback
        pass

    # Fallback: hent direkte HTML via fc_api og parse med BeautifulSoup
    try:
        html = fc_api.get_rider_endpoint(rider_id)
        parsed = _parse_rider_from_html(html)
        parsed["id"] = rider_id
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kunne ikke hente rytterdata: {str(e)}")

@app.get("/rider/{rider_id}/image")
async def get_rider_image(rider_id: int):
    """
    Proxy endpoint for rider images. Returnerer billedbytes (image/jpeg eller image/png).
    Bruges fra frontend som: <img src="/api/rider/{id}/image" />
    """
    try:
        # hent rider-info for at finde image_url
        html = fc_api.get_rider_endpoint(rider_id)
        parsed = _parse_rider_from_html(html)
        image_url = parsed.get("image_url")
        if not image_url:
            raise HTTPException(status_code=404, detail="Rytterbillede ikke fundet")

        resp = requests.get(image_url, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Fejl ved hent af billedet fra FirstCycling")
        # content-type fra response hvis tilgængelig
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        return Response(content=resp.content, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fejl ved hent af billedet: {str(e)}")