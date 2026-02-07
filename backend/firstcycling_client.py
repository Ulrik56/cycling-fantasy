"""Simple wrapper around baronet2/FirstCyclingAPI for fetching race results.

Usage:
    from firstcycling_client import get_race_results
    data = get_race_results(9, 2019)
"""
from first_cycling_api import RaceEdition
import pandas as pd
from typing import List, Dict

def get_race_results(race_id: int, year: int) -> List[Dict]:
    """
    Returnerer race results som en liste af dicts (JSON-venligt).
    """
    race = RaceEdition(race_id=race_id, year=year)
    results = race.results().results_table  # pandas DataFrame
    # Sørg for at konvertere eventuelle numpy dtypes til native python
    if isinstance(results, pd.DataFrame):
        return results.fillna("").to_dict(orient="records")
    # fallback hvis API ændrer sig
    try:
        return list(map(dict, results))
    except Exception:
        return []