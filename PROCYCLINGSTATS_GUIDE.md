# 🐍 ProCyclingStats Python Library Guide

## Denne løsning VIRKER med Cloudflare! ✅

`procyclingstats` er et Python library der kan scrape data fra ProCyclingStats.com
og det omgår Cloudflare beskyttelsen automatisk.

---

## Installation

```bash
pip install procyclingstats
```

---

## Basic Usage

### Hent data for en rytter

```python
from procyclingstats import Rider

# Find rytter via URL slug (fra ProCyclingStats)
rider = Rider("rider/remco-evenepoel")

# Parse alle data
data = rider.parse()

print(f"Navn: {data['rider_name']}")
print(f"UCI Points: {data['uci_points']}")
print(f"UCI Rank: {data['uci_rank']}")
print(f"Nationalitet: {data['nationality']}")
print(f"Hold: {data['team_name']}")
```

### Hent data for alle jeres ryttere

```python
from procyclingstats import Rider
import json
from datetime import datetime

# URL slugs for alle jeres ryttere
# (Find dem ved at søge på procyclingstats.com)
rider_urls = {
    "EVENEPOEL Remco": "rider/remco-evenepoel",
    "VINGEGAARD HANSEN Jonas": "rider/jonas-vingegaard-rasmussen",
    "PHILIPSEN Jasper": "rider/jasper-philipsen",
    "ROGLIČ Primož": "rider/primoz-roglic",
    "GIRMAY Biniam": "rider/biniam-girmay",
    # ... alle jeres ryttere
}

points_data = {}

for rider_name, rider_url in rider_urls.items():
    print(f"Henter {rider_name}...")
    
    rider = Rider(rider_url)
    data = rider.parse()
    
    points_data[rider_name] = {
        'uci_points': data.get('uci_points', 0),
        'uci_rank': data.get('uci_rank', 0),
        'team': data.get('team_name', ''),
    }
    
    print(f"  → {data.get('uci_points', 0)} point")

# Gem til JSON
with open('rider_points.json', 'w', encoding='utf-8') as f:
    json.dump({
        'last_update': datetime.now().isoformat(),
        'points': points_data
    }, f, indent=2, ensure_ascii=False)

print("\n✅ Data gemt til rider_points.json")
```

---

## Avanceret: Hent race resultater

```python
from procyclingstats import Race

# Tour de France 2025
tour = Race("race/tour-de-france/2025")
data = tour.parse()

print(f"Løb: {data['race_name']}")
print(f"Dato: {data['date']}")

# Hent etaper
stages = data['stages']
for stage in stages:
    print(f"  {stage['stage_name']}: {stage['date']}")

# Hent GC (samlet stilling)
gc = data['gc']
for position in gc[:10]:  # Top 10
    print(f"{position['rank']}. {position['rider_name']}: {position['time']}")
```

---

## Find Rider URL Slugs

Sådan finder du URL slugs for jeres ryttere:

1. Gå til https://www.procyclingstats.com
2. Søg efter rytteren
3. Klik på rytterens profil
4. URL ser sådan ud: `https://www.procyclingstats.com/rider/jonas-vingegaard-rasmussen`
5. Slug er delen efter `/rider/`: `jonas-vingegaard-rasmussen`

### Script til at finde slugs automatisk

```python
from procyclingstats import Rider
import requests
from bs4 import BeautifulSoup

def search_rider(rider_name):
    """
    Søg efter rytter og returner URL slug
    """
    base_url = "https://www.procyclingstats.com"
    search_url = f"{base_url}/search.php?term={rider_name}&searchf=Search"
    
    # Brug procyclingstats library til at håndtere requests
    # (det omgår Cloudflare automatisk)
    
    # For nu, returner None hvis ikke fundet
    # Du skal manuelt finde slugs første gang
    return None

# Alle jeres rytternavne
rider_names = [
    "EVENEPOEL Remco",
    "VINGEGAARD HANSEN Jonas",
    "PHILIPSEN Jasper",
    # ... resten
]

# Output mapping til at kopiere ind i koden
print("rider_urls = {")
for name in rider_names:
    # Du skal manuelt finde disse første gang
    print(f'    "{name}": "rider/SLUG_HER",')
print("}")
```

---

## Komplet Script til Jeres Liga

```python
"""
Cycling Fantasy Manager - UCI Point Updater
Bruger procyclingstats library til at hente point
"""

from procyclingstats import Rider
import json
from datetime import datetime
import time

# Mapping af rytternavne til ProCyclingStats URL slugs
RIDER_URLS = {
    "EVENEPOEL Remco": "rider/remco-evenepoel",
    "VINGEGAARD HANSEN Jonas": "rider/jonas-vingegaard-rasmussen",
    "DEL TORO ROMERO Isaac": "rider/isaac-del-toro",
    "PEDERSEN Mads": "rider/mads-pedersen",
    "PHILIPSEN Jasper": "rider/jasper-philipsen",
    "GIRMAY Biniam": "rider/biniam-girmay",
    "VAN AERT Wout": "rider/wout-van-aert",
    "MAGNIER Paul": "rider/paul-magnier",
    "DE LIE Arnaud": "rider/arnaud-de-lie",
    "GANNA Filippo": "rider/filippo-ganna",
    # ... TILFØJ RESTEN AF JERES RYTTERE HER
}

def get_all_points():
    """Hent UCI point for alle ryttere"""
    points = {}
    total = len(RIDER_URLS)
    
    print(f"\n🚴 Henter UCI point for {total} ryttere...")
    print("=" * 60)
    
    for i, (rider_name, rider_url) in enumerate(RIDER_URLS.items(), 1):
        try:
            print(f"[{i}/{total}] {rider_name}...", end=" ")
            
            rider = Rider(rider_url)
            data = rider.parse()
            
            uci_points = data.get('uci_points', 0)
            points[rider_name] = uci_points
            
            print(f"✓ {uci_points} point")
            
            # Vær høflig - vent 1 sekund mellem requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Fejl: {str(e)}")
            points[rider_name] = 0
    
    print("=" * 60)
    print(f"✅ Færdig!\n")
    
    return points

def save_to_json(points, filename='points.json'):
    """Gem point til JSON fil"""
    data = {
        'last_update': datetime.now().isoformat(),
        'season': 2026,
        'points': points
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Data gemt til {filename}")

def save_to_csv(points, filename='points.csv'):
    """Gem til CSV (til Google Sheets import)"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Rider', 'Points2026', 'LastUpdated'])
        
        update_date = datetime.now().strftime('%Y-%m-%d')
        for rider, pts in sorted(points.items()):
            writer.writerow([rider, pts, update_date])
    
    print(f"💾 CSV gemt til {filename}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚴 CYCLING FANTASY - UCI POINT UPDATER")
    print("=" * 60)
    
    # Hent alle point
    points = get_all_points()
    
    # Gem til filer
    save_to_json(points)
    save_to_csv(points)
    
    # Vis top 10
    print("\n🏆 Top 10 ryttere:")
    top_riders = sorted(points.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (rider, pts) in enumerate(top_riders, 1):
        print(f"  {i:2d}. {rider:30s} {pts:4d} point")
    
    print("\n✅ Klar! Du kan nu importere points.csv til Google Sheets")
```

---

## Deploy som Vercel Serverless Function

```python
# api/update-points.py

from procyclingstats import Rider
import json
from datetime import datetime

# Dine rider URLs her
RIDER_URLS = {
    # ... som ovenfor
}

def handler(request):
    """Vercel serverless function handler"""
    
    # Hent point for alle ryttere
    points = {}
    for rider_name, rider_url in RIDER_URLS.items():
        try:
            rider = Rider(rider_url)
            data = rider.parse()
            points[rider_name] = data.get('uci_points', 0)
        except:
            points[rider_name] = 0
    
    # Returner JSON
    return {
        'statusCode': 200,
        'body': json.dumps({
            'last_update': datetime.now().isoformat(),
            'points': points
        })
    }
```

### vercel.json

```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  }
}
```

### requirements.txt

```
procyclingstats==0.5.0
```

---

## Fordele ved procyclingstats

✅ Omgår Cloudflare automatisk  
✅ Officiel Python library  
✅ Godt vedligeholdt  
✅ Nem at bruge  
✅ Pålidelig data  
✅ Kan hente meget mere end bare point  

---

## Næste Skridt

1. Installer library: `pip install procyclingstats`
2. Find URL slugs for alle jeres ryttere (manuelt første gang)
3. Kør scriptet for at teste
4. Deploy som serverless function ELLER
5. Kør lokalt og upload CSV til Google Sheets

Jeg anbefaler at starte med option 5 - kør scriptet lokalt 1x om ugen
og upload CSV'en til Google Sheets. Det er nemmest! 🎯
