# CyclingFlash API

An unofficial Python API wrapper for [cyclingflash.com](https://cyclingflash.com/).

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Rider Information

```python
from cyclingflash_api import Rider

# Create rider instance using URL slug
pogacar = Rider('tadej-pogacar')

# Get profile information
profile = pogacar.profile()
print(profile['name'])        # 'Tadej Pogačar'
print(profile['nationality']) # 'Slovenia'
print(profile['age'])         # 27

# Get results for a specific year
results_2025 = pogacar.results(2025)
print(results_2025.head())

# Get career victories
wins = pogacar.wins()

# Get team history
teams = pogacar.teams()
```

### Race Results

```python
from cyclingflash_api import Race, RaceEdition

# Access a specific race
tdf = Race('tour-de-france-2025')

# Get final GC results
gc = tdf.result()
print(gc.head())

# Get stage results
stage_12 = tdf.stage_result(12)

# Get startlist
startlist = tdf.startlist()

# Alternative: Use RaceEdition for recurring races
tdf_2024 = RaceEdition('tour-de-france', 2024)
tdf_2025 = RaceEdition('tour-de-france', 2025)
```

### Rankings

```python
from cyclingflash_api import Ranking

# Get overall ranking for men elite
overall = Ranking.overall('men-elite')
print(overall.head(10))

# Get specialty rankings
gc_ranking = Ranking.gc('men-elite')
sprint_ranking = Ranking.sprint('women-elite')
mountain_ranking = Ranking.mountain('men-elite')
tt_ranking = Ranking.timetrial('men-elite')
hill_ranking = Ranking.hill('men-elite')

# Get rolling 365-day rankings
rolling_overall = Ranking.overall('men-elite', rolling=True)

# Get team rankings
team_ranking = Ranking.team_overall('men-elite')

# Get victory rankings
victories = Ranking.victories('men-elite', year=2026)

# Custom ranking query
custom = Ranking.get('gc', 'cyclingflash-365-ranking', 'women-elite')
```

### Teams

```python
from cyclingflash_api import Team

# Get team information
uae = Team('uae-emirates-xrg-2026')

# Get roster
roster = uae.roster()
print(roster)

# Get rider names
names = uae.rider_names()
print(names)  # ['Tadej Pogačar', 'Adam Yates', ...]

# Team properties
print(uae.name)  # 'UAE Emirates XRG'
print(uae.year)  # 2026
```

### Calendar

```python
from cyclingflash_api import Calendar

# Get road calendar
calendar_2026 = Calendar.road(2026, 'Men Elite')
world_tour = Calendar.road(2026, 'UCI World Tour')
women_wt = Calendar.road(2026, "UCI Women's World Tour")

# Get cyclocross calendar
cx_calendar = Calendar.cyclocross('2025-2026', 'Men Elite')

# Other disciplines
mtb = Calendar.mountainbike(2026)
gravel = Calendar.gravel(2026)
track = Calendar.track(2026)
```

### Latest Results

```python
from cyclingflash_api import LatestResults

# Get latest results as list
results = LatestResults.get()
for r in results[:5]:
    print(f"{r['race']}: Winner - {r['podium'][0]['rider']}")

# Get as DataFrame
df = LatestResults.as_dataframe()
print(df[['race', 'winner', 'second', 'third']])
```

### Transfers

```python
from cyclingflash_api import Transfers

# Get transfer list
transfers = Transfers.get()
for t in transfers[:10]:
    print(f"{t['rider']}: {t['from_team']} → {t['to_team']}")

# As DataFrame
df = Transfers.as_dataframe()
```

## API Reference

### URL Slugs

CyclingFlash uses URL slugs to identify riders, teams, and races. These are derived from names:

- Riders: `tadej-pogacar`, `mathieu-van-der-poel`, `remco-evenepoel`
- Teams: `uae-emirates-xrg-2026`, `team-visma-lease-a-bike-2026`
- Races: `tour-de-france-2025`, `giro-ditalia-2024`, `paris-roubaix-2025`

You can find slugs by looking at the URLs on cyclingflash.com.

### Gender Categories

Available gender/age categories:
- `men-elite`
- `women-elite`
- `men-u23`
- `women-u23`
- `men-juniors`
- `women-juniors`

### Ranking Types

- `overall`: Overall combined ranking
- `gc`: General classification specialists
- `hill`: Hilly terrain specialists
- `mountain`: Mountain specialists
- `timetrial`: Time trial specialists
- `sprint`: Sprint specialists
- `cyclocross`: Cyclocross ranking

### Ranking Categories

- `cyclingflash-ranking`: Current season ranking
- `cyclingflash-365-ranking`: Rolling 365-day ranking
- `road-victory-ranking`: Victory count ranking
- `team-ranking`: Team rankings
- `team-365-ranking`: Rolling team rankings

## Notes

- This is an unofficial API that scrapes data from cyclingflash.com
- Please be respectful of their servers and implement rate limiting in production
- Data structure may change if the website is updated
- The API returns pandas DataFrames for tabular data

## License

MIT License - Use at your own risk.

---

## Fantasy Manager Integration

The API includes a special `FantasyManager` class designed for fantasy cycling games.

### Basic Usage

```python
from cyclingflash_api import FantasyManager

# Create manager instance
fm = FantasyManager(total_budget=100, max_team_size=20, max_per_team=3)

# Get top riders with estimated values and points
riders = fm.get_top_riders(50)
for rider in riders[:5]:
    print(f"{rider['name']}: {rider['value']}M € - {rider['expectedPoints']} pts")
```

### Get Specialists

```python
# Get GC specialists
gc_riders = fm.get_specialists('gc', 30)

# Get sprinters
sprinters = fm.get_specialists('sprint', 30)

# Get climbers
climbers = fm.get_specialists('mountain', 30)

# Get time trialists
tt_riders = fm.get_specialists('timetrial', 20)
```

### Suggest Optimal Team

```python
# Balanced team (mix of stars and value picks)
team = fm.suggest_team(strategy='balanced')

# Star-focused team
team = fm.suggest_team(strategy='stars')

# Value-focused team
team = fm.suggest_team(strategy='value')

# With custom budget
team = fm.suggest_team(budget=80, strategy='balanced')
```

### Calculate Rider Form

```python
# Get form score (0-100) based on recent results
form = fm.calculate_form('tadej-pogacar', last_n_results=10)
print(f"Pogačar form: {form:.1f}/100")
```

### Get Detailed Rider Info

```python
details = fm.get_rider_details('remco-evenepoel')
print(f"Wins this year: {details['wins_this_year']}")
print(f"Podiums: {details['podiums_this_year']}")
```

### Export for React App

```python
riders = fm.get_top_riders(50)

# Export as JSON
json_data = fm.export_to_json(riders)

# Export as TypeScript
tsx_code = fm.export_to_tsx(riders, variable_name='riders')
```

### Generate Data Script

Use the included script to generate rider data:

```bash
# Generate TypeScript file with 50 riders
python -m cyclingflash_api.generate_fantasy_data --limit 50 --output riders.tsx

# Generate JSON
python -m cyclingflash_api.generate_fantasy_data --limit 100 --format json --output riders.json

# Women's category
python -m cyclingflash_api.generate_fantasy_data --gender women-elite --output women_riders.tsx
```

### Value Tiers

Rider values are estimated based on ranking position:

| Ranking | Value (M €) |
|---------|-------------|
| 1-5     | 55-65       |
| 6-10    | 45-54       |
| 11-20   | 35-44       |
| 21-35   | 25-34       |
| 36-50   | 18-24       |
| 51-75   | 12-17       |
| 76-100  | 8-11        |
| 101-150 | 5-7         |
| 151-250 | 3-4         |
| 251+    | 1-2         |

### Integration with React

The generated TypeScript file can be imported directly:

```tsx
import { riders, Rider } from './riders';

const FantasyCyclingApp = () => {
  const [selectedRiders, setSelectedRiders] = useState<Rider[]>([]);
  
  // Use riders data...
};
```
