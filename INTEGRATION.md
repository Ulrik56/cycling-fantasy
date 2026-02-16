# Integration Guide: CyclingFlash API med Fantasy Manager

Denne guide viser hvordan du integrerer CyclingFlash API med din eksisterende React app.

## 1. Start Backend Server

```bash
cd cyclingflash_api
pip install -r requirements.txt
pip install flask flask-cors

# Start serveren
python server.py
```

Serveren kører nu på `http://localhost:5000`

## 2. Kopier Frontend Filer

Kopier disse filer til dit React projekt:
- `frontend/useCyclingFlash.js` → `src/hooks/useCyclingFlash.js`
- `frontend/RiderModal.jsx` → `src/components/RiderModal.jsx`

## 3. Opdater din App

### Trin 1: Import hooks og modal

Tilføj øverst i din `CyclingFantasyManager.js`:

```jsx
import { useLiveRiders, nameToSlug } from './hooks/useCyclingFlash';
import RiderModal from './components/RiderModal';
```

### Trin 2: Tilføj state for modal og live riders

I din `CyclingFantasyManager` funktion, tilføj:

```jsx
function CyclingFantasyManager() {
  // ... eksisterende state ...
  
  // NY: Modal state
  const [selectedRider, setSelectedRider] = useState(null);
  
  // NY: Hent alle unikke rytternavne fra alle hold
  const allRiderNames = React.useMemo(() => {
    const names = new Set();
    Object.values(TEAMS).forEach(riders => {
      riders.forEach(name => names.add(name));
    });
    return Array.from(names);
  }, []);
  
  // NY: Hook til at checke live status
  const { liveRiders, isLoading: liveLoading } = useLiveRiders(allRiderNames);
  
  // ... resten af din kode ...
```

### Trin 3: Opdater rytter-rækker til at være klikbare

Find din rytter-rendering og tilføj onClick + LIVE badge:

```jsx
{selectedTeamData.map((rider, index) => {
  const isLive = rider in liveRiders;
  const raceInfo = liveRiders[rider]?.race;
  
  return (
    <div
      key={index}
      className="rider-row"
      onClick={() => setSelectedRider(rider)}  // NY: Åbn modal
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        padding: '1rem',
        borderRadius: '0.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        transition: 'all 0.3s',
        cursor: 'pointer',  // NY: Vis at den er klikbar
        // NY: Highlight hvis live
        border: isLive ? '2px solid #ef4444' : '1px solid transparent'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Rytter foto */}
        <div style={{...}}>...</div>
        
        {/* Navn + LIVE badge */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <p style={{ fontWeight: '600', fontSize: '1.125rem', margin: 0 }}>
              {rider}
            </p>
            
            {/* NY: LIVE badge */}
            {isLive && (
              <span style={{
                background: '#ef4444',
                color: 'white',
                fontSize: '0.65rem',
                fontWeight: 'bold',
                padding: '0.15rem 0.4rem',
                borderRadius: '0.25rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                animation: 'pulse 2s infinite'
              }}>
                <span style={{
                  width: '5px',
                  height: '5px',
                  background: 'white',
                  borderRadius: '50%'
                }} />
                LIVE
              </span>
            )}
          </div>
          
          {/* NY: Vis løbsnavn hvis live */}
          {isLive && raceInfo && (
            <p style={{ fontSize: '0.75rem', color: '#fca5a5', margin: 0 }}>
              🏁 {raceInfo.race}
            </p>
          )}
        </div>
      </div>
      
      {/* Points */}
      <div style={{ textAlign: 'right' }}>
        ...
      </div>
    </div>
  );
})}
```

### Trin 4: Tilføj Modal komponent

Tilføj helt til sidst i din return, lige før `</>`:

```jsx
{/* Rytter Modal */}
{selectedRider && (
  <RiderModal
    riderName={selectedRider}
    onClose={() => setSelectedRider(null)}
    isLive={selectedRider in liveRiders}
    raceInfo={liveRiders[selectedRider]?.race}
  />
)}
```

### Trin 5: Tilføj pulse animation

I din `<style>` sektion, tilføj:

```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

## 4. Environment Variable (valgfrit)

For produktion, sæt API URL:

```bash
# .env
REACT_APP_API_URL=https://din-server.com/api
```

## 5. Test

1. Start backend: `python server.py`
2. Start React: `npm start`
3. Klik på en rytter for at se profil
4. Ryttere der kører i dag vises med LIVE badge

## API Endpoints

| Endpoint | Beskrivelse |
|----------|-------------|
| `GET /api/rider/{slug}` | Rytter profil + resultater |
| `GET /api/rider/{slug}/live` | Check om rytter kører i dag |
| `GET /api/today` | Dagens løb med startlister |
| `GET /api/live` | Alle ryttere der kører i dag |
| `POST /api/live/check` | Check liste af ryttere |
| `GET /api/results/latest` | Seneste resultater |

## Troubleshooting

### CORS fejl
Tjek at Flask CORS er konfigureret:
```python
from flask_cors import CORS
CORS(app)
```

### Ingen data
- Tjek at serveren kører på port 5000
- Tjek at CyclingFlash er tilgængelig
- Se server logs for fejl

### Langsom respons
- API'en cacher data i 5 minutter
- Første request kan tage længere tid
