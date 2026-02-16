# 🚀 Deployment Guide

Denne guide viser hvordan du deployer CyclingFlash API til forskellige platforme.

---

## Option 1: Railway (Anbefalet - Nemmest)

Railway er gratis for hobby-projekter og super nemt at bruge.

### Trin 1: Opret GitHub repo

```bash
cd cyclingflash_api
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/DIT-USERNAME/cyclingflash-api.git
git push -u origin main
```

### Trin 2: Deploy på Railway

1. Gå til [railway.app](https://railway.app)
2. Log ind med GitHub
3. Klik **"New Project"** → **"Deploy from GitHub repo"**
4. Vælg dit `cyclingflash-api` repo
5. Railway detecter automatisk Dockerfile og deployer

### Trin 3: Få din URL

Efter deploy får du en URL som:
```
https://cyclingflash-api-production.up.railway.app
```

### Trin 4: Opdater React app

I din React app, sæt environment variable:
```bash
# .env
REACT_APP_API_URL=https://cyclingflash-api-production.up.railway.app/api
```

---

## Option 2: Render (Også gratis)

### Trin 1: Push til GitHub (som ovenfor)

### Trin 2: Deploy på Render

1. Gå til [render.com](https://render.com)
2. Log ind med GitHub
3. Klik **"New"** → **"Web Service"**
4. Vælg dit repo
5. Indstillinger:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 server:app`
6. Klik **"Create Web Service"**

Din URL bliver:
```
https://cyclingflash-api.onrender.com
```

---

## Option 3: Fly.io

### Trin 1: Installer Fly CLI

```bash
# macOS
brew install flyctl

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Trin 2: Login og deploy

```bash
fly auth login
fly launch
fly deploy
```

---

## Option 4: Din egen server (VPS)

Hvis du har en VPS (DigitalOcean, Hetzner, etc.):

### Med Docker

```bash
# På serveren
git clone https://github.com/DIT-USERNAME/cyclingflash-api.git
cd cyclingflash-api
docker build -t cyclingflash-api .
docker run -d -p 5000:5000 --name cyclingflash-api cyclingflash-api
```

### Med systemd (uden Docker)

```bash
# Installer dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Setup
cd /opt
git clone https://github.com/DIT-USERNAME/cyclingflash-api.git
cd cyclingflash-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Opret systemd service
sudo nano /etc/systemd/system/cyclingflash-api.service
```

Service fil:
```ini
[Unit]
Description=CyclingFlash API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/cyclingflash-api
ExecStart=/opt/cyclingflash-api/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cyclingflash-api
sudo systemctl start cyclingflash-api
```

---

## 🔧 Efter Deployment

### Test at API'en virker

```bash
curl https://DIN-URL.com/api/health
# Forventet: {"status": "ok", "timestamp": "..."}

curl https://DIN-URL.com/api/live
# Forventet: {"date": "...", "count": X, "riders": [...]}
```

### Opdater React app

```javascript
// src/hooks/useCyclingFlash.js
const API_BASE = 'https://DIN-URL.com/api';  // Ændr denne linje
```

Eller brug environment variable:
```bash
# .env.production
REACT_APP_API_URL=https://DIN-URL.com/api
```

---

## 💰 Priser

| Platform | Gratis tier | Betalt |
|----------|-------------|--------|
| Railway | $5/måned credits gratis | Fra $5/måned |
| Render | 750 timer/måned gratis | Fra $7/måned |
| Fly.io | 3 shared VMs gratis | Fra $1.94/måned |
| DigitalOcean | - | Fra $4/måned |

---

## 🐛 Troubleshooting

### "Application failed to start"
- Tjek at `requirements.txt` er korrekt
- Tjek logs i Railway/Render dashboard

### "502 Bad Gateway"
- API'en starter måske langsomt første gang
- Vent 30 sekunder og prøv igen

### "CORS error" i browser
- Tjek at Flask CORS er konfigureret
- Tjek at du bruger den rigtige URL

### Langsom respons
- Gratis tiers har "cold starts"
- Første request kan tage 10-30 sekunder
- Efterfølgende er hurtige (caching)
