from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firstcycling_client import get_race_results

app = FastAPI(title="Cycling Fantasy — FirstCycling proxy")

# Tillad din Vercel-front-end origin (opdater hvis nødvendigt)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cycling-fantasy.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/race/{race_id}/{year}")
def race_results(race_id: int, year: int):
    try:
        data = get_race_results(race_id, year)
        if not data:
            raise HTTPException(status_code=404, detail="No results found")
        return {"race_id": race_id, "year": year, "results": data}
    except Exception as e:
        # log evt. fejl her
        raise HTTPException(status_code=500, detail=str(e))

# Kør med: uvicorn fastapi_firstcycling:app --host 0.0.0.0 --port 8000