# 🤖 AUTOMATISK UCI POINT OPDATERING - Komplet Guide

## 📋 Oversigt

Dette script henter automatisk UCI points fra ProCyclingStats og opdaterer dit Google Sheet.

**Features:**
- ✅ Henter 2026 season UCI points
- ✅ Opdaterer Google Sheet automatisk
- ✅ Kan køre dagligt automatisk
- ✅ Logger alle opdateringer
- ✅ Omgår Cloudflare problemer

---

## 🚀 Setup (20 minutter)

### Step 1: Installer Python Pakker

Åbn terminal og kør:

```bash
pip install procyclingstats gspread oauth2client
```

### Step 2: Opsæt Google Sheets API

#### A) Gå til Google Cloud Console

1. Gå til: https://console.cloud.google.com
2. Log ind med din Google konto

#### B) Opret Projekt

1. Klik "Select a project" øverst
2. Klik "New Project"
3. Navn: **"Cycling Fantasy"**
4. Klik "Create"
5. Vent 10 sekunder
6. Sørg for at projektet er valgt

#### C) Aktiver Google Sheets API

1. I søgefeltet øverst, skriv: **"Google Sheets API"**
2. Klik på resultatet
3. Klik **"Enable"**
4. Vent til det er aktiveret

#### D) Opret Service Account

1. I venstre menu, klik **"Credentials"**
2. Klik **"Create Credentials"** → **"Service Account"**
3. Service account details:
   - Service account name: **"cycling-updater"**
   - Service account ID: (automatisk)
   - Klik **"Create and Continue"**
4. Grant this service account access:
   - Klik **"Continue"** (spring over)
5. Grant users access:
   - Klik **"Done"**

#### E) Download Credentials

1. Du er nu på "Credentials" siden
2. Under "Service Accounts", find **"cycling-updater"**
3. Klik på email adressen (cycling-updater@xxxx.iam.gserviceaccount.com)
4. Gå til **"Keys"** fanen
5. Klik **"Add Key"** → **"Create new key"**
6. Vælg **"JSON"**
7. Klik **"Create"**
8. Filen downloades automatisk
9. **GEM DENNE FIL!** Flyt den til din `cycling-fantasy` mappe

#### F) Del Google Sheet med Service Account

1. Åbn den JSON fil du lige downloadede
2. Find linjen `"client_email"` - den ser sådan ud:
   ```
   "client_email": "cycling-updater@xxxxx.iam.gserviceaccount.com"
   ```
3. **Kopier denne email adresse**
4. Gå til dit Google Sheet
5. Klik **"Del"** knappen
6. Indsæt email adressen
7. Vælg **"Editor"** (VIGTIGT!)
8. **Fjern flueben** ved "Notify people"
9. Klik **"Del"**

### Step 3: Konfigurer Scriptet

1. Download `update_points.py` filen jeg gav dig
2. Åbn den i en teksteditor
3. **Find linje 13:**
   ```python
   CREDENTIALS_FILE = 'cycling-fantasy-xxxxx.json'
   ```
4. **Erstat** med navnet på din JSON fil
5. **Gem** filen

### Step 4: Test Scriptet

Kør scriptet for at teste:

```bash
python update_points.py
```

Du skulle se:
```
🚴 CYCLING FANTASY - AUTOMATISK UCI POINT OPDATERING
📊 Forbinder til Google Sheets...
✅ Forbundet til Google Sheets!
🚴 Starter opdatering af 78 ryttere...
[1/78] EVENEPOEL Remco → 245 point ✅
[2/78] PHILIPSEN Jasper → 189 point ✅
...
```

**Hvis det virker** → Gå til Step 5! 🎉

**Hvis det IKKE virker**, check:
- Er JSON filen i samme mappe som scriptet?
- Er filnavnet korrekt i scriptet?
- Har du delt Google Sheet med service account email?
- Er sheetet navngivet "Cycling Fantasy 2026"?

---

## ⏰ Step 5: Automatisk Daglig Opdatering

### Option A: Windows Task Scheduler

#### 1. Opret Batch Fil

Opret en fil kaldet `run_update.bat` i din cycling-fantasy mappe:

```batch
@echo off
cd C:\Users\DitBrugernavn\Desktop\cycling-fantasy
python update_points.py >> update_log.txt 2>&1
```

Erstat `C:\Users\DitBrugernavn\Desktop\cycling-fantasy` med din rigtige sti.

#### 2. Test Batch Filen

Dobbeltklik på `run_update.bat` - scriptet skulle køre.

#### 3. Opsæt Task Scheduler

1. Tryk Windows-tast
2. Skriv: **"Task Scheduler"**
3. Åbn det
4. I højre side, klik **"Create Basic Task"**
5. Name: **"Cycling Fantasy Updater"**
6. Description: **"Opdater UCI points dagligt"**
7. Klik **Next**
8. Trigger: **"Daily"**
9. Klik **Next**
10. Start: **06:00** (kl. 6 om morgenen)
11. Recur every: **1 days**
12. Klik **Next**
13. Action: **"Start a program"**
14. Klik **Next**
15. Program/script: **Browse** → Find din `run_update.bat`
16. Klik **Next**
17. Klik **Finish**

**Færdig!** Scriptet kører nu hver dag kl. 06:00 🎉

---

### Option B: Mac/Linux Cron Job

#### 1. Opret Shell Script

Opret en fil kaldet `run_update.sh`:

```bash
#!/bin/bash
cd /Users/DitBrugernavn/Desktop/cycling-fantasy
python3 update_points.py >> update_log.txt 2>&1
```

Gør den eksekverbar:

```bash
chmod +x run_update.sh
```

#### 2. Opsæt Cron Job

Åbn crontab:

```bash
crontab -e
```

Tilføj denne linje:

```
0 6 * * * /Users/DitBrugernavn/Desktop/cycling-fantasy/run_update.sh
```

Gem og luk.

**Færdig!** Scriptet kører nu hver dag kl. 06:00 🎉

---

## 📊 Monitorering

### Se Logs

Scriptet gemmer logs i `update_log.txt`:

```bash
# Windows
type update_log.txt

# Mac/Linux
cat update_log.txt
```

### Manuel Kørsel

Når som helst du vil opdatere manuelt:

```bash
python update_points.py
```

---

## 🔧 Tilpasning

### Ændre Tidspunkt

**Windows Task Scheduler:**
- Højreklik på tasken → Properties → Triggers → Edit

**Mac/Linux Cron:**
- `crontab -e`
- Ændre `0 6` til det ønskede tidspunkt (timer minutter)

### Ændre Frekvens

**Hver time:**
```
0 * * * * /sti/til/run_update.sh
```

**To gange dagligt (06:00 og 18:00):**
```
0 6,18 * * * /sti/til/run_update.sh
```

**Kun på hverdage:**
```
0 6 * * 1-5 /sti/til/run_update.sh
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'procyclingstats'"

```bash
pip install procyclingstats gspread oauth2client
```

### "FileNotFoundError: cycling-fantasy-xxxxx.json"

- Check at JSON filen er i samme mappe som scriptet
- Check at filnavnet er korrekt i scriptet (linje 13)

### "gspread.exceptions.APIError: PERMISSION_DENIED"

- Gå til dit Google Sheet
- Del det med service account email
- Giv "Editor" rettigheder

### "Rider not found in sheet"

- Check at rytternavnet i scriptet PRÆCIS matcher navnet i Google Sheet
- Selv mellemrum og accenter skal være ens

---

## 📈 Hvad Sker Der Nu?

**Hver dag kl. 06:00:**
1. 🤖 Scriptet starter automatisk
2. 🔍 Henter UCI points for alle 78 ryttere
3. 📊 Opdaterer Google Sheet
4. ✅ Din web-app viser nye point automatisk (henter hvert 5. minut)

**Du behøver ikke gøre NOGET!** 🎉

Dine venner ser altid opdaterede point når de besøger siden!

---

## 💡 Pro Tips

### Email Notifikationer

Tilføj email notification når opdateringen er færdig:

```python
# I slutningen af main() funktionen
import smtplib
from email.mime.text import MIMEText

msg = MIMEText(f"Opdatering færdig! {updated} ryttere opdateret")
msg['Subject'] = 'Cycling Fantasy - Point Opdateret'
msg['From'] = 'din@email.com'
msg['To'] = 'din@email.com'

# Send email (kræver SMTP setup)
```

### Backup

Scriptet gemmer automatisk en log. Du kan også:

```bash
# Backup Google Sheet ugentligt
cp cycling-fantasy-xxxxx.json backup-$(date +%Y%m%d).json
```

---

## 🎯 Du Er Færdig!

Nu har du:
- ✅ Automatisk UCI point opdatering
- ✅ Kører dagligt uden din indblanding
- ✅ Logging af alle opdateringer
- ✅ Fuld kontrol over hvornår det kører

**Nyd sæsonen! 🚴‍♂️🏆**
