```markdown
# FirstCycling microservice for Cycling-Fantasy

Denne lille service henter ryttere fra FirstCycling via projectet `r-huijts/firstcycling-mcp` og eksponerer simple REST endpoints.

Mapper:
- main.py : FastAPI-app med endpoints
- requirements.txt : dependencies

Installation (lokalt)
1. Opret virtuel miljø:
   - python -m venv .venv
   - Linux/macOS: source .venv/bin/activate
   - Windows: .venv\Scripts\activate

2. Installer dependencies:
   - pip install -r requirements.txt

3. Kør server:
   - uvicorn main:app --reload --port 8000

Endpoints
- GET /search_rider?q={query}
  - Søg efter ryttere. Returnerer JSON liste med id, name, nationality, team.

- GET /rider/{id}
  - Henter basisinfo for rytter med {id}. Returnerer JSON med name, team, nationality, image_url, dob.

- GET /rider/{id}/image
  - Proxy: returnerer billedbytes for rytterens billede (bruges fra frontend).

Eksempel (frontend / Next.js)
- Hent rytterdata:
  fetch("http://localhost:8000/rider/16973").then(r => r.json())

- Vis billede:
  <img src="http://localhost:8000/rider/16973/image" alt="rider photo" />

Tips og fejlhåndtering
- Hvis du får importfejl for `first_cycling_api`, tjek at du installerede via requirements.txt og at din virtuelenv er aktiv.
- Hvis FirstCycling ændrer HTML-struktur kan parsing fejle — service har en række fallback-mekanismer og logger fejlsituationer via undtagelser.

Sikkerhed og deployment
- Til produktion: overvej at køre som container eller på en lille VM; sæt rate-limiting (FirstCycling kan have begrænsninger).
- Overvej at cache svar (Redis eller lokal filcache) så du ikke gentagne gange henter samme data.
```