import React, { useState, useEffect } from 'react';
import { Trophy, Users, TrendingUp, RefreshCw, Calendar, Award, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

// GOOGLE SHEETS CONFIGURATION
const GOOGLE_SHEET_ID = '1RfoTiYhMI-Yr7123evM4_PeSYn87W20UCBerhqV_Ztg';

// Helper funktion til at få points for en rytter
const getRiderPoints = (riderName, pointsData) => {
  return pointsData[riderName] || 0;
};

// KOSTPRIS pr. rytter = hvad rytteren blev købt for (2025-point).
// Bruges til investerings-trackeren: hvor god en investering har rytteren været i 2026?
const RIDER_COSTS = {
  "ABRAHAMSEN Jonas": 989,
  "AGOSTINACCHIO Mattia": 100,
  "ANDRESEN Tobias Lund": 1252,
  "ARENSMAN Thymen": 1543,
  "ASGREEN Kasper": 230,
  "BISIAUX Léo": 311,
  "BITTNER Pavel": 1126,
  "BJERG Mikkel": 114,
  "BLACKMORE Joseph": 379,
  "BRENNAN Matthew": 1507,
  "Benoît Cosnefroy": 385,
  "CHRISTEN Jan": 1347,
  "CORT Magnus": 808,
  "DAINESE Alberto": 569,
  "DE BONDT Dries": 487,
  "DE LIE Arnaud": 2781,
  "DEL GROSSO Tibor": 760,
  "DEL TORO Isaac": 5664,
  "EVENEPOEL Remco": 4118,
  "FISHER-BLACK Finn": 705,
  "FOLDAGER Anders": 241,
  "Fernando Gaviria": 125,
  "GALL Felix": 2216,
  "GANNA Filippo": 2153,
  "GAUDU David": 494,
  "GEOGHEGAN HART Tao": 256,
  "GIRMAY Biniam": 1646,
  "GROENEWEGEN Dylan": 698,
  "HELLEMOSE Asbjørn": 92,
  "HIRSCHI Marc": 1262,
  "KOOIJ Olav": 2123,
  "KRAGH ANDERSEN Søren": 216,
  "KRON Andreas": 57,
  "KUBIŠ Lukáš": 1194,
  "KÜNG Stefan": 757,
  "LAMPERTI Luke": 385,
  "LANDA Mikel": 740,
  "LAPEIRA Paul": 778,
  "LAPORTE Christophe": 369,
  "LECERF Junior": 680,
  "LEKNESSUND Andreas": 593,
  "LEMMEN Bart": 193,
  "MAGNIER Paul": 2327,
  "MARTÍNEZ Daniel Felipe": 276,
  "MAS Enric": 1021,
  "MERLIER Tim": 1951,
  "MOHORIČ Matej": 484,
  "MOLARD Rudy": 195,
  "MORGADO António": 985,
  "NORDHAGEN Jørgen": 402,
  "NYS Thibau": 846,
  "O'CONNOR Ben": 945,
  "OMRZEL Jakob": 365,
  "ONLEY Oscar": 2910,
  "PELLIZZARI Giulio": 1473,
  "PERICAS Adrià": 195,
  "PHILIPSEN Jasper": 2438,
  "PLAPP Luke": 997,
  "POOLE Max David": 425,
  "RICCITELLO Matthew": 1020,
  "RODRÍGUEZ Carlos": 435,
  "ROGLIČ Primož": 1856,
  "RONDEL Mathys": 552,
  "SEGAERT Alec": 398,
  "SEIXAS Paul": 1128,
  "SIMMONS Quinn": 1280,
  "SÖDERQVIST Jakob": 489,
  "TEUTENBERG Tim Torn": 379,
  "TIBERI Antonio": 1110,
  "TORRES Pablo": 164,
  "UIJTDEBROEKS Cian": 809,
  "VACEK Mathias": 711,
  "VALGREN Michael": 153,
  "VALTER Attila": 175,
  "VAN AERT Wout": 2908,
  "VAN BAARLE Dylan": 140,
  "VAN EETVELT Lennert": 439,
  "VAN GILS Maxim": 538,
  "VAN WILDER Ilan": 947,
  "VAUQUELIN Kévin": 2459,
  "VINGEGAARD Jonas": 5944,
  "VLASOV Aleksandr": 260,
  "WIDAR Jarno": 515,
  "WITHEN PHILIPSEN Albert": 726,
  "ZINGLE Axel": 131,
  "ØXENBERG Peter": 60,
};

// Hent kostpris for en rytter (null hvis ukendt)
const getRiderCost = (riderName) => {
  const c = RIDER_COSTS[riderName];
  return (c === undefined || c === null) ? null : c;
};

// Beregn investerings-status: hvor meget af kostprisen har rytteren tjent ind i 2026?
// Skala på baren: 0–100 % = andel af kostprisen tjent ind (>100 % = profit, baren bliver fuld og grøn).
// Markøren "halvvejs-pace" sidder ved 50 %: en fair investering bør være cirka her midt på sæsonen.
const getInvestment = (riderName, pointsData) => {
  const cost = getRiderCost(riderName);
  const earned = getRiderPoints(riderName, pointsData);
  if (!cost || cost <= 0) {
    return { cost: null, earned, ratio: null };
  }
  const ratio = earned / cost; // 1.0 = tjent kostprisen ind
  let color, label, emoji;
  // Italienske cykeltermer der eskalerer gennem hierarkiet:
  // Pacco (fiasko-køb) → Brocco (krikke) → Gregario (hjælperytter) →
  // Capitano (kaptajn) → Campionissimo (supermester) → Cannibale (Il Cannibale / Merckx)
  if (ratio >= 2.5)       { color = '#22c55e'; label = 'Cannibale';     emoji = '🦈'; }
  else if (ratio >= 1.5)  { color = '#4ade80'; label = 'Campionissimo'; emoji = '🤑'; }
  else if (ratio >= 1)    { color = '#a3e635'; label = 'Capitano';      emoji = '💰'; }
  else if (ratio >= 0.66) { color = '#facc15'; label = 'Gregario';      emoji = '⏳'; }
  else if (ratio >= 0.33) { color = '#f97316'; label = 'Brocco';        emoji = '😬'; }
  else                    { color = '#ef4444'; label = 'Pacco';         emoji = '🥶'; }
  const fill = Math.min(ratio, 1) * 100; // bar-bredde i %
  // Pænt multiplikator-tal: "1,4×" (komma), heltal når ≥ 10
  const mult = ratio >= 10 ? Math.round(ratio).toString() : ratio.toFixed(1).replace('.', ',');
  return { cost, earned, ratio, color, label, emoji, fill, mult };
};

// TDF-badge må kun vises i juni og juli
const isTdfPeriod = () => {
  const m = new Date().getMonth(); // 0=januar ... 5=juni, 6=juli
  return m === 5 || m === 6;
};

// Lille 🇫🇷 + TDF-mærke til ryttere der er udtaget til Tour de France
const TdfBadge = () => (
  <span
    title="Udtaget til Tour de France"
    style={{
      background: 'rgba(255, 255, 255, 0.12)',
      border: '1px solid rgba(255, 255, 255, 0.25)',
      borderRadius: '0.25rem',
      padding: '0.05rem 0.35rem',
      fontSize: '0.6rem',
      fontWeight: 'bold',
      letterSpacing: '0.5px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.2rem',
      whiteSpace: 'nowrap',
      lineHeight: 1.6
    }}
  >
    🇫🇷 TDF
  </span>
);

// INVESTERINGS-MÅLER: viser hvor god en investering en rytter har været i 2026
// i forhold til kostprisen (2025-point). Farvet bar + multiplikator-badge.
const InvestmentMeter = ({ riderName, pointsData, compact = false }) => {
  const inv = getInvestment(riderName, pointsData);

  // Ingen kostpris kendt → diskret note i stedet for måler
  if (inv.ratio === null) {
    return (
      <span style={{ fontSize: '0.7rem', color: '#9ca3af', fontStyle: 'italic' }}>
        ingen kostpris
      </span>
    );
  }

  // Kompakt udgave: kun badge (bruges i "Alle hold")
  if (compact) {
    return (
      <span
        title={`Tjent ${inv.earned.toLocaleString('da-DK')} af ${inv.cost.toLocaleString('da-DK')} kostpoint`}
        style={{
          background: inv.color,
          color: '#0f172a',
          fontSize: '0.65rem',
          fontWeight: 'bold',
          padding: '0.1rem 0.4rem',
          borderRadius: '0.25rem',
          whiteSpace: 'nowrap'
        }}
      >
        {inv.mult}× {inv.emoji}
      </span>
    );
  }

  return (
    <div style={{ marginTop: '0.6rem' }}>
      {/* Toplinje: kostpris + status-badge */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
        <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
          Kostpris: <span style={{ color: '#e5e7eb', fontWeight: 600 }}>{inv.cost.toLocaleString('da-DK')}</span> pt
        </span>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem',
            background: inv.color,
            color: '#0f172a',
            fontSize: '0.72rem',
            fontWeight: 'bold',
            padding: '0.12rem 0.45rem',
            borderRadius: '0.35rem',
            whiteSpace: 'nowrap'
          }}
        >
          {inv.emoji} {inv.mult}× tjent ind · {inv.label}
        </span>
      </div>

      {/* Selve måleren */}
      <div style={{ position: 'relative', height: '0.75rem' }}>
        {/* Spor */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '999px',
          overflow: 'hidden'
        }}>
          {/* Fyld */}
          <div style={{
            width: `${inv.fill}%`,
            height: '100%',
            background: `linear-gradient(90deg, ${inv.color}99, ${inv.color})`,
            borderRadius: '999px',
            transition: 'width 0.6s ease'
          }} />
        </div>
        {/* Halvvejs-pace markør (50 %) */}
        <div style={{
          position: 'absolute',
          left: '50%',
          top: '-2px',
          bottom: '-2px',
          width: '2px',
          background: 'rgba(255, 255, 255, 0.85)',
          transform: 'translateX(-1px)'
        }} />
      </div>
      <div style={{ position: 'relative', height: '0.9rem', marginTop: '0.1rem' }}>
        <span style={{
          position: 'absolute',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: '0.6rem',
          color: '#9ca3af',
          whiteSpace: 'nowrap'
        }}>
          ▲ halvvejs-pace
        </span>
      </div>
    </div>
  );
};

// DANSKE CYKELCITATER - Legendariske kommentarer
const DANISH_CYCLING_QUOTES = [
  { quote: "Virenque kører. Han står helt stille. Han står stille som et tysk træ i Harzen.", author: "Jørn Mader" },
  { quote: "Jeg vidste godt vi skulle køre på brosten, men jeg vidste ikke, de havde kylet dem ned fra en helikopter.", author: "Jesper Skibby" },
  { quote: "Hold kæft det blæste derude og der var også en spaniak der ikke have lært det der med at man ikke skulle pisse imod vinden. Så han pissede og jeg fik hans pis på mit ben. Så det var jeg ikke helt tilfreds med.", author: "Chris Anker Sørensen" },
  { quote: "Når jeg om aftenen går i seng, så håber jeg de er væk næste morgen, men de er der sgu stadigvæk næste morgen.", author: "Jesper Skibby" },
  { quote: "Vi er helt tossede med at cykle. Vi kan bare så gerne lide det.", author: "Chris Anker Sørensen" },
  { quote: "Han behandler cyklen som en gammel led kælling der fortjener det.", author: "Jørn Mader" },
  { quote: "Magen til selvtillid skal man lede i Scientology efter.", author: "Jørgen Mader" },
  { quote: "Der sidder han, med et underbid der kunne klare et tordenskyl...", author: "Jørn Mader" },
  { quote: "Se Mauris grin. Ja, den mand kan grine en vaskebjørn ned fra et træ...", author: "Jørn Mader" },
  { quote: "Jakob Piil hamrer mod målstregen, færgerne tuder i havnen, de ved at han er fra Svendborg!!!", author: "Jørgen Leth" },
  { quote: "Riis hænger... Riis i vanskeligheder... Riis er sat... eller er han kørt... ja, Riis er kørt... Riis er kørt fra gruppen med Indurain... Riis i udbrud..", author: "Jørgen Leth" },
  { quote: "Hvis jeg var en spåkone, ville jeg tage min spåkugle, male den gul, skrive Bjarne Riis på den, og trille den ind af Champs Elysees..", author: "Jørgen Leth" },
  { quote: "Er det ikke herligt at se så mange mænd i cykelshorts?", author: "Jørgen Mader" },
  { quote: "Den brune muskel dunker.", author: "Jørgen Leth" },
  { quote: "Livingston vil gerne give den til Armstrong, men Armstrong vil hellere have den bagfra af Hamilton.", author: "Jørgen Mader" },
  { quote: "Hans blanke isse lyner som Athenes sværd i den nedgående franske aftensol.", author: "Jørn Mader" },
  { quote: "Vi har skrevet historie. For det er simpelthen umuligt at dumme sig mere på 150 meter. Det er vi nødt til at fejre.", author: "Brian Holm" },
  { quote: "Man må håbe, at sportsdirektøren har slået ham med en cykelpumpe, da de kom til hotellet; en af de tunge, gammeldags fodpumper. Der skulle han have nogen over nakken, så han kan lære det.", author: "Brian Holm" }
];

// Hold data - Team Vester er 2025 mester! 🏆
const TEAMS = {
  "Team Døssing": ["EVENEPOEL Remco", "PHILIPSEN Jasper", "ROGLIČ Primož", "GIRMAY Biniam", "HIRSCHI Marc", "SEIXAS Paul", "MAS Enric", "O'CONNOR Ben", "UIJTDEBROEKS Cian", "KÜNG Stefan", "WITHEN PHILIPSEN Albert", "VAN GILS Maxim", "GAUDU David", "MOHORIČ Matej", "RODRÍGUEZ Carlos", "LAPORTE Christophe", "MARTÍNEZ Daniel Felipe", "VLASOV Aleksandr", "ASGREEN Kasper", "VALTER Attila"],
  "Team Vester": ["EVENEPOEL Remco", "VAUQUELIN Kévin", "PHILIPSEN Jasper", "BRENNAN Matthew", "HIRSCHI Marc", "SEIXAS Paul", "TIBERI Antonio", "RICCITELLO Matthew", "LAPEIRA Paul", "LECERF Junior", "WIDAR Jarno", "GAUDU David", "VAN EETVELT Lennert", "RODRÍGUEZ Carlos", "Benoît Cosnefroy", "LAPORTE Christophe", "OMRZEL Jakob", "BISIAUX Léo", "AGOSTINACCHIO Mattia", "KRON Andreas"],
  "Team Peter": ["VINGEGAARD Jonas", "ONLEY Oscar", "BRENNAN Matthew", "ANDRESEN Tobias Lund", "KUBIŠ Lukáš", "SEIXAS Paul", "UIJTDEBROEKS Cian", "CORT Magnus", "LECERF Junior", "WIDAR Jarno", "DE BONDT Dries", "VAN EETVELT Lennert", "POOLE Max David", "NORDHAGEN Jørgen", "LAMPERTI Luke", "TEUTENBERG Tim Torn", "ASGREEN Kasper", "MOLARD Rudy", "LEMMEN Bart", "HELLEMOSE Asbjørn"],
  "Kasper Krabber": ["VAN AERT Wout", "MAGNIER Paul", "GANNA Filippo", "ARENSMAN Thymen", "BRENNAN Matthew", "SIMMONS Quinn", "SEIXAS Paul", "MORGADO António", "NYS Thibau", "UIJTDEBROEKS Cian", "DEL GROSSO Tibor", "VACEK Mathias", "VAN GILS Maxim", "WIDAR Jarno", "SÖDERQVIST Jakob", "VAN EETVELT Lennert", "POOLE Max David", "OMRZEL Jakob", "VAN BAARLE Dylan", "ZINGLE Axel"],
  "T-Dawgs Dogs": ["DEL TORO Isaac", "MAGNIER Paul", "BRENNAN Matthew", "PELLIZZARI Giulio", "SEIXAS Paul", "RICCITELLO Matthew", "MORGADO António", "NYS Thibau", "DEL GROSSO Tibor", "WITHEN PHILIPSEN Albert", "VACEK Mathias", "DAINESE Alberto", "WIDAR Jarno", "LAMPERTI Luke", "BLACKMORE Joseph", "OMRZEL Jakob", "VLASOV Aleksandr", "PERICAS Adrià", "TORRES Pablo", "AGOSTINACCHIO Mattia"],
  "Gewiss Allan": ["VINGEGAARD Jonas", "MAGNIER Paul", "KOOIJ Olav", "MERLIER Tim", "BRENNAN Matthew", "SEIXAS Paul", "RICCITELLO Matthew", "LANDA Mikel", "RONDEL Mathys", "POOLE Max David", "SEGAERT Alec", "LAMPERTI Luke", "BLACKMORE Joseph", "TEUTENBERG Tim Torn", "FOLDAGER Anders", "VAN BAARLE Dylan", "ZINGLE Axel", "BJERG Mikkel", "ØXENBERG Peter", "KRON Andreas"],
  "Don Karnage": ["EVENEPOEL Remco", "DE LIE Arnaud", "MAGNIER Paul", "GIRMAY Biniam", "SEIXAS Paul", "BITTNER Pavel", "VAN WILDER Ilan", "O'CONNOR Ben", "DEL GROSSO Tibor", "WITHEN PHILIPSEN Albert", "GROENEWEGEN Dylan", "MOHORIČ Matej", "VAN EETVELT Lennert", "POOLE Max David", "LAMPERTI Luke", "LAPORTE Christophe", "KRAGH ANDERSEN Søren", "ZINGLE Axel", "Fernando Gaviria", "KRON Andreas"],
  "Team Anders M": ["VAN AERT Wout", "GALL Felix", "KOOIJ Olav", "BRENNAN Matthew", "CHRISTEN Jan", "HIRSCHI Marc", "SEIXAS Paul", "PLAPP Luke", "ABRAHAMSEN Jonas", "CORT Magnus", "DEL GROSSO Tibor", "WITHEN PHILIPSEN Albert", "VACEK Mathias", "FISHER-BLACK Finn", "LEKNESSUND Andreas", "NORDHAGEN Jørgen", "GEOGHEGAN HART Tao", "KRAGH ANDERSEN Søren", "VALGREN Michael", "VAN BAARLE Dylan"]
};

// Funktion til at normalisere navn (fjern accenter) for fil-lookup
const normalizeForFile = (name) => {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Fjern accenter (\u00e9, \u00fc, \u010d osv.)
    .replace(/\u00f8/g, 'o').replace(/\u00d8/g, 'O') // Nordiske bogstaver som NFD ikke r\u00f8rer
    .replace(/\u00e5/g, 'a').replace(/\u00c5/g, 'A')
    .replace(/\u00e6/g, 'ae').replace(/\u00c6/g, 'AE')
    .replace(/['\u2018\u2019]/g, ''); // Fjern apostroffer (lige og kr\u00f8llede)
};

// Funktion til at konvertere rytter navn til foto URL
const getRiderPhotoUrl = (riderName) => {
  // Normaliser navnet for fil-lookup (fjern accenter)
  // "VAUQUELIN Kévin" -> "VAUQUELIN Kevin.webp"
  // "KÜNG Stefan" -> "KUNG Stefan.webp"
  const normalized = normalizeForFile(riderName);
  // encodeURI sikrer at mellemrum/specialtegn altid kodes ens i URL'en
  // Add version to bust cache
  return encodeURI(`/images/riders/${normalized}.webp`) + '?v=3';
};

function CyclingFantasyManager() {
  const [teams] = useState(TEAMS);
  const [selectedTeam, setSelectedTeam] = useState(Object.keys(TEAMS)[0]);
  const [riderPoints, setRiderPoints] = useState({});
  const [tdfRiders, setTdfRiders] = useState({});
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTeams, setExpandedTeams] = useState({});
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState(null);
  const [upcomingRaces, setUpcomingRaces] = useState([]);
  const [showAllRaces, setShowAllRaces] = useState(false);
  const [dailyQuote] = useState(() => {
    // Vælg dagens citat baseret på datoen
    const today = new Date();
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000);
    return DANISH_CYCLING_QUOTES[dayOfYear % DANISH_CYCLING_QUOTES.length];
  });

  const fetchPointsFromSheets = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const url = `https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/export?format=csv&gid=0`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP fejl! Status: ${response.status}`);
      }
      
      const csvText = await response.text();
      const lines = csvText.split('\n');
      const points = {};
      const tdf = {};

      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const parts = line.split(',');
        if (parts.length >= 2) {
          const rider = parts[0].trim().replace(/"/g, '');
          const pts = parseInt(parts[1]) || 0;
          if (rider) {
            points[rider] = pts;
            // Kolonne D: "TDF" hvis rytteren er udtaget til Tour de France
            const tdfFlag = (parts[3] || '').trim().replace(/"/g, '');
            if (tdfFlag) tdf[rider] = true;
          }
        }
      }

      setTdfRiders(tdf);

      if (Object.keys(points).length === 0) {
        throw new Error('Ingen data fundet i sheetet');
      }
      
      setRiderPoints(points);
      setLastUpdate(new Date().toLocaleString('da-DK'));
      localStorage.setItem('cycling-points', JSON.stringify(points));
      localStorage.setItem('cycling-last-update', new Date().toISOString());
      
    } catch (err) {
      setError(`Kunne ikke hente data: ${err.message}`);
      const cached = localStorage.getItem('cycling-points');
      if (cached) {
        setRiderPoints(JSON.parse(cached));
        const cachedUpdate = localStorage.getItem('cycling-last-update');
        if (cachedUpdate) {
          setLastUpdate(new Date(cachedUpdate).toLocaleString('da-DK') + ' (cached)');
        }
      }
    }
    
    setIsLoading(false);
  };

  const fetchUpcomingRaces = async () => {
    try {
      // Hent "Kommende Løb" sheet
      const url = `https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/export?format=csv&gid=732785664`;
      const response = await fetch(url);
      
      if (!response.ok) return;
      
      const csvText = await response.text();
      const lines = csvText.split('\n');
      const races = [];
      
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const parts = line.split(',');
        if (parts.length >= 3) {
          const date = parts[0].trim().replace(/"/g, '');
          const name = parts[1].trim().replace(/"/g, '');
          const riders = parts[2].trim().replace(/"/g, '');
          
          // Parse dato (format: "28.01" eller "27-31.01")
          const today = new Date();
          const dateMatch = date.match(/(\d+)\.(\d+)/);
          if (dateMatch) {
            const day = parseInt(dateMatch[1]);
            const month = parseInt(dateMatch[2]);
            const raceDate = new Date(today.getFullYear(), month - 1, day);
            
            races.push({
              date: date,
              name: name,
              riders: riders,
              isToday: raceDate.toDateString() === today.toDateString()
            });
          }
        }
      }
      
      setUpcomingRaces(races);
      
    } catch (err) {
      console.error('Kunne ikke hente kommende løb:', err);
    }
  };

  useEffect(() => {
    fetchPointsFromSheets();
    fetchUpcomingRaces();
    const interval = setInterval(() => {
      fetchPointsFromSheets();
      fetchUpcomingRaces();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateTeamPoints = (teamName) => {
    const riders = teams[teamName] || [];
    return riders.reduce((sum, rider) => sum + getRiderPoints(rider, riderPoints), 0);
  };

  const getLeaderboard = () => {
    return Object.keys(teams)
      .map(teamName => ({
        name: teamName,
        points: calculateTeamPoints(teamName),
        riderCount: teams[teamName].length
      }))
      .sort((a, b) => b.points - a.points);
  };

  const toggleTeamExpand = (teamName) => {
    setExpandedTeams(prev => ({ ...prev, [teamName]: !prev[teamName] }));
  };

  const openGoogleSheet = () => {
    window.open(`https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/edit`, '_blank');
  };

  const leaderboard = getLeaderboard();
  const selectedTeamData = selectedTeam ? teams[selectedTeam] : [];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&display=swap');
        
        body {
          margin: 0;
          padding: 0;
          font-family: 'Rajdhani', sans-serif;
        }
        
        * {
          box-sizing: border-box;
        }
        
        .title-font {
          font-family: 'Bebas Neue', sans-serif;
          letter-spacing: 2px;
        }
        
        .card {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          transition: all 0.3s ease;
        }
        
        .card:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: rgba(250, 204, 21, 0.3);
          transform: translateY(-2px);
        }
        
        .btn {
          transition: all 0.2s ease;
          cursor: pointer;
          border: none;
          font-family: 'Rajdhani', sans-serif;
        }
        
        .btn:hover {
          transform: scale(1.05);
        }
        
        .btn:active {
          transform: scale(0.98);
        }
        
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .rider-row {
          animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .podium-1 {
          background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        }
        
        .podium-2 {
          background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%);
        }
        
        .podium-3 {
          background: linear-gradient(135deg, #CD7F32 0%, #B87333 100%);
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
      
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom right, #0f172a, #1e3a8a, #0f172a)',
        color: 'white',
        padding: '1rem'
      }}>
        {/* Header */}
        <div style={{ maxWidth: '80rem', margin: '0 auto 2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <h1 className="title-font" style={{ fontSize: 'clamp(2rem, 8vw, 4.5rem)', color: '#facc15', margin: 0 }}>
              CYCLING FANTASY
            </h1>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="btn"
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                padding: '0.5rem 1rem',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                color: 'white'
              }}
            >
              ⚙️ Indstillinger
            </button>
          </div>
          
          {/* Dagens Citat */}
          <div className="card" style={{
            padding: '1rem',
            borderRadius: '0.75rem',
            marginBottom: '1.5rem',
            borderLeft: '3px solid #facc15',
            background: 'linear-gradient(135deg, rgba(250, 204, 21, 0.08) 0%, rgba(250, 204, 21, 0.03) 100%)'
          }}>
            <div style={{ display: 'flex', alignItems: 'start', gap: '0.75rem' }}>
              <div style={{ fontSize: '2rem', color: '#facc15', lineHeight: 1 }}>💬</div>
              <div style={{ flex: 1 }}>
                <p style={{ 
                  fontSize: '1rem', 
                  fontStyle: 'italic', 
                  margin: '0 0 0.25rem 0',
                  color: '#fff',
                  lineHeight: 1.5
                }}>
                  "{dailyQuote.quote}"
                </p>
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: '#facc15',
                  margin: 0,
                  fontWeight: 600
                }}>
                  — {dailyQuote.author}
                </p>
              </div>
            </div>
          </div>
          
          {/* Kommende Løb */}
          {upcomingRaces.length > 0 && (
            <div className="card" style={{
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              marginBottom: '1.5rem',
              borderLeft: '3px solid #3b82f6',
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.03) 100%)',
              cursor: 'pointer'
            }}
            onClick={() => setShowAllRaces(!showAllRaces)}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                  <Calendar style={{ width: '1.25rem', height: '1.25rem', color: '#3b82f6' }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#3b82f6', marginBottom: '0.25rem' }}>
                      Kommende Løb
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                      {showAllRaces ? 'Vis kun i dag' : 'Klik for at se hele ugen'}
                    </div>
                  </div>
                </div>
                {showAllRaces ? <ChevronUp style={{ width: '1rem', height: '1rem', color: '#3b82f6' }} /> : <ChevronDown style={{ width: '1rem', height: '1rem', color: '#3b82f6' }} />}
              </div>
              
              <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {upcomingRaces
                  .filter(race => showAllRaces || race.isToday)
                  .map((race, idx) => (
                    <div key={idx} style={{
                      padding: '0.5rem',
                      borderRadius: '0.5rem',
                      background: race.isToday ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                      border: race.isToday ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <div style={{ fontSize: '0.813rem', fontWeight: 600, color: race.isToday ? '#60a5fa' : '#fff' }}>
                          {race.name}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#9ca3af', whiteSpace: 'nowrap' }}>
                          {race.date}
                        </div>
                      </div>
                      {race.riders && race.riders !== 'Ingen danske' && (
                        <div style={{ fontSize: '0.75rem', color: '#d1d5db', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <span>🇩🇰</span>
                          <span>{race.riders}</span>
                        </div>
                      )}
                      {(!race.riders || race.riders === 'Ingen danske') && (
                        <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                          Ingen danske ryttere
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.875rem', color: '#d1d5db', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Calendar style={{ width: '1rem', height: '1rem' }} />
              <span>Sæson 2026</span>
            </div>
            {lastUpdate && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <RefreshCw style={{ width: '1rem', height: '1rem' }} />
                <span>Opdateret: {lastUpdate}</span>
              </div>
            )}
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="card" style={{ maxWidth: '80rem', margin: '0 auto 2rem', borderRadius: '0.75rem', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Google Sheets Integration</h3>
            
            {error && (
              <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
                <p style={{ color: '#fecaca', margin: 0, fontSize: '0.875rem' }}>{error}</p>
              </div>
            )}
            
            {!error && Object.keys(riderPoints).length > 0 && (
              <div style={{ background: 'rgba(34, 197, 94, 0.2)', border: '1px solid #22c55e', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
                <p style={{ color: '#bbf7d0', margin: 0 }}>✅ Forbindelse OK! Point hentet for {Object.keys(riderPoints).length} ryttere</p>
              </div>
            )}
            
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={fetchPointsFromSheets}
                className="btn"
                disabled={isLoading}
                style={{
                  background: isLoading ? '#059669' : '#10b981',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  color: 'white'
                }}
              >
                <RefreshCw style={{ width: '1rem', height: '1rem' }} className={isLoading ? 'animate-spin' : ''} />
                {isLoading ? 'Opdaterer...' : 'Opdater Nu'}
              </button>
              
              <button
                onClick={openGoogleSheet}
                className="btn"
                style={{
                  background: '#2563eb',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  color: 'white'
                }}
              >
                <ExternalLink style={{ width: '1rem', height: '1rem' }} />
                Åbn Google Sheet
              </button>
            </div>
          </div>
        )}

        <div style={{ maxWidth: '80rem', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {/* Leaderboard */}
          <div style={{ gridColumn: window.innerWidth > 1024 ? 'span 1' : 'span 1' }}>
            <div className="card" style={{ borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <Trophy style={{ width: '1.5rem', height: '1.5rem', color: '#facc15' }} />
                <h2 className="title-font" style={{ fontSize: '1.875rem', margin: 0 }}>LIGA STILLING</h2>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {leaderboard.map((team, index) => {
                  const isSelected = team.name === selectedTeam;
                  const podiumClass = index === 0 ? 'podium-1' : index === 1 ? 'podium-2' : index === 2 ? 'podium-3' : '';
                  
                  return (
                    <div
                      key={team.name}
                      onClick={() => setSelectedTeam(team.name)}
                      className={podiumClass}
                      style={{
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        cursor: 'pointer',
                        transition: 'all 0.3s',
                        background: isSelected 
                          ? 'rgba(250, 204, 21, 0.2)' 
                          : index < 3 ? undefined : 'rgba(255, 255, 255, 0.05)',
                        border: isSelected 
                          ? '2px solid #facc15' 
                          : index < 3 ? 'none' : '1px solid rgba(255, 255, 255, 0.1)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{
                            width: '2rem',
                            height: '2rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 'bold',
                            fontSize: '0.875rem',
                            background: index >= 3 ? '#334155' : undefined,
                            color: index < 3 ? 'black' : 'white'
                          }}>
                            {index + 1}
                          </div>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <p style={{ fontWeight: '600', margin: 0, fontSize: '0.875rem', color: index < 3 ? 'black' : 'white' }}>{team.name}</p>
                              {team.name === 'Team Vester' && (
                                <span style={{
                                  background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                                  color: 'black',
                                  fontSize: '0.65rem',
                                  fontWeight: 'bold',
                                  padding: '0.15rem 0.4rem',
                                  borderRadius: '0.25rem',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '0.25rem'
                                }}>
                                  🏆 2025
                                </span>
                              )}
                            </div>
                            <p style={{ fontSize: '0.75rem', color: index < 3 ? 'rgba(0,0,0,0.6)' : '#9ca3af', margin: 0 }}>{team.riderCount} ryttere</p>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: index < 3 ? 'black' : '#facc15', margin: 0 }}>{team.points}</p>
                          <p style={{ fontSize: '0.75rem', color: index < 3 ? 'rgba(0,0,0,0.6)' : '#9ca3af', margin: 0 }}>point</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Team Details */}
          <div style={{ gridColumn: window.innerWidth > 1024 ? 'span 2' : 'span 1' }}>
            <div className="card" style={{ borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
                <Users style={{ width: '1.5rem', height: '1.5rem', color: '#60a5fa' }} />
                <h2 className="title-font" style={{ fontSize: '1.875rem', margin: 0 }}>{selectedTeam}</h2>
              </div>

              {/* Forklaring til investerings-måleren */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '0.4rem 0.9rem',
                fontSize: '0.7rem',
                color: '#9ca3af',
                marginBottom: '1rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(255,255,255,0.04)',
                borderRadius: '0.5rem'
              }}>
                <span style={{ color: '#e5e7eb', fontWeight: 600 }}>💰 Investering 2026:</span>
                <span>hvor stor del af kostprisen rytteren har tjent ind</span>
                <span><span style={{ color: '#ef4444', fontWeight: 700 }}>●</span> Pacco</span>
                <span><span style={{ color: '#f97316', fontWeight: 700 }}>●</span> Brocco</span>
                <span><span style={{ color: '#facc15', fontWeight: 700 }}>●</span> Gregario</span>
                <span><span style={{ color: '#a3e635', fontWeight: 700 }}>●</span> Capitano</span>
                <span><span style={{ color: '#4ade80', fontWeight: 700 }}>●</span> Campionissimo</span>
                <span><span style={{ color: '#22c55e', fontWeight: 700 }}>●</span> Cannibale</span>
                <span style={{ fontStyle: 'italic' }}>▲ = halvvejs-pace (sæsonen er kun halvvejs)</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {selectedTeamData.map((rider, index) => (
                  <div
                    key={index}
                    className="rider-row"
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      padding: '1rem',
                      borderRadius: '0.5rem',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'stretch',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{
                        width: '2.5rem',
                        height: '2.5rem',
                        borderRadius: '50%',
                        overflow: 'hidden',
                        background: 'linear-gradient(135deg, #3b82f6, #9333ea)',
                        flexShrink: 0,
                        position: 'relative',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <img
                          src={getRiderPhotoUrl(rider)}
                          alt={rider}
                          loading="lazy"
                          decoding="async"
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            position: 'absolute'
                          }}
                          onError={(e) => {
                            // Prøv igen et par gange ved midlertidig load-fejl, før vi viser initialer
                            const img = e.target;
                            const tries = Number(img.dataset.retry || 0);
                            if (tries < 2) {
                              img.dataset.retry = tries + 1;
                              setTimeout(() => { img.src = getRiderPhotoUrl(rider) + '&r=' + Date.now(); }, 700);
                              return;
                            }
                            img.style.display = 'none';
                            if (img.nextElementSibling) img.nextElementSibling.style.display = 'flex';
                          }}
                        />
                        <div style={{
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          color: 'white',
                          display: 'none',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: '100%',
                          height: '100%'
                        }}>
                          {rider.split(' ')[0]?.[0]}{rider.split(' ')[1]?.[0]}
                        </div>
                      </div>
                      <p style={{ fontWeight: '600', fontSize: '1.125rem', margin: 0 }}>{rider}</p>
                      {isTdfPeriod() && tdfRiders[rider] && <TdfBadge />}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <TrendingUp style={{ width: '1rem', height: '1rem', color: '#4ade80' }} />
                        <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#facc15' }}>
                          {getRiderPoints(rider, riderPoints)}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0 }}>UCI point</p>
                    </div>
                    </div>
                    <InvestmentMeter riderName={rider} pointsData={riderPoints} />
                  </div>
                ))}
              </div>
            </div>

            {/* All Teams Overview */}
            <div className="card" style={{ borderRadius: '0.75rem', padding: '1.5rem', marginTop: '1.5rem' }}>
              <h3 className="title-font" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>ALLE HOLD</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(teams).map(([teamName, riders]) => (
                  <div key={teamName} style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '0.5rem' }}>
                    <div
                      onClick={() => toggleTeamExpand(teamName)}
                      style={{
                        padding: '1rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Award style={{ width: '1.25rem', height: '1.25rem', color: '#facc15' }} />
                        <span style={{ fontWeight: '600', fontSize: '0.875rem' }}>{teamName}</span>
                        <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>({riders.length} ryttere)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#facc15' }}>
                          {calculateTeamPoints(teamName)} point
                        </span>
                        {expandedTeams[teamName] ? (
                          <ChevronUp style={{ width: '1.25rem', height: '1.25rem' }} />
                        ) : (
                          <ChevronDown style={{ width: '1.25rem', height: '1.25rem' }} />
                        )}
                      </div>
                    </div>
                    {expandedTeams[teamName] && (
                      <div style={{ padding: '0 1rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {riders.map((rider, index) => (
                          <div key={index} style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '0.5rem 0.75rem',
                            background: 'rgba(0, 0, 0, 0.2)',
                            borderRadius: '0.25rem',
                            fontSize: '0.875rem',
                            gap: '0.75rem'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <div style={{
                                width: '2rem',
                                height: '2rem',
                                borderRadius: '50%',
                                overflow: 'hidden',
                                background: 'linear-gradient(135deg, #3b82f6, #9333ea)',
                                flexShrink: 0,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                position: 'relative'
                              }}>
                                <img
                                  src={getRiderPhotoUrl(rider)}
                                  alt={rider}
                                  loading="lazy"
                                  decoding="async"
                                  style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    position: 'absolute'
                                  }}
                                  onError={(e) => {
                                    const img = e.target;
                                    const tries = Number(img.dataset.retry || 0);
                                    if (tries < 2) {
                                      img.dataset.retry = tries + 1;
                                      setTimeout(() => { img.src = getRiderPhotoUrl(rider) + '&r=' + Date.now(); }, 700);
                                      return;
                                    }
                                    img.style.display = 'none';
                                  }}
                                />
                                <div style={{
                                  fontSize: '0.75rem',
                                  fontWeight: 'bold',
                                  color: 'white',
                                  zIndex: 0
                                }}>
                                  {index + 1}
                                </div>
                              </div>
                              <span>{rider}</span>
                              {isTdfPeriod() && tdfRiders[rider] && <TdfBadge />}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <InvestmentMeter riderName={rider} pointsData={riderPoints} compact />
                              <span style={{ color: '#facc15', fontWeight: '600', whiteSpace: 'nowrap' }}>
                                {getRiderPoints(rider, riderPoints)} point
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default CyclingFantasyManager;
