import { Trophy, Users, TrendingUp, RefreshCw, Calendar, Award, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

// GOOGLE SHEETS CONFIGURATION
const GOOGLE_SHEET_ID = '1RfoTiYhMI-Yr7123evM4_PeSYn87W20UCBerhqV_Ztg';

// Hold data
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
  "Team Døssing": ["EVENEPOEL Remco", "PHILIPSEN Jasper", "ROGLIČ Primož", "GIRMAY Biniam", "HIRSCHI Marc", "SEIXAS Paul", "MAS NICOLAU Enric", "O'CONNOR Ben", "UIJTDEBROEKS Cian", "KÜNG Stefan", "PHILIPSEN Albert", "VAN GILS Maxim", "GAUDU David", "MOHORIC Matej", "RODRIGUEZ CANO Carlos", "LAPORTE Christophe", "MARTINEZ POVEDA Daniel Felipe", "VLASOV Aleksandr", "ASGREEN Kasper", "VALTER Attila"],
  "Team Vester": ["EVENEPOEL Remco", "VAUQUELIN Kévin", "PHILIPSEN Jasper", "BRENNAN Matthew", "HIRSCHI Marc", "SEIXAS Paul", "TIBERI Antonio", "RICCITELLO Matthew", "LAPEIRA Paul", "LECERF Junior", "WIDAR Jarno", "GAUDU David", "VAN EETVELT Lennert", "RODRIGUEZ CANO Carlos", "COSNEFROY Benoit", "LAPORTE Christophe", "OMRZEL Jakob", "BISIAUX Léo", "AGOSTINACCHIO Mattia", "KRON Andreas Lorentz"],
  "Team Peter": ["VINGEGAARD HANSEN Jonas", "ONLEY Oscar", "BRENNAN Matthew", "LUND ANDRESEN Tobias", "KUBIŠ Lukáš", "SEIXAS Paul", "UIJTDEBROEKS Cian", "NIELSEN Magnus Cort", "LECERF Junior", "WIDAR Jarno", "DE BONDT Dries", "VAN EETVELT Lennert", "POOLE Max David", "NORDHAGEN Jørgen", "LAMPERTI Luke", "TEUTENBERG Tim Torn", "ASGREEN Kasper", "MOLARD Rudy", "LEMMEN Bart", "HELLEMOSE Asbjørn"],
  "Kasper Krabber": ["VAN AERT Wout", "MAGNIER Paul", "GANNA Filippo", "ARENSMAN Thymen", "BRENNAN Matthew", "SIMMONS Quinn", "SEIXAS Paul", "TOMAS MORGADO António", "NYS Thibau", "UIJTDEBROEKS Cian", "DEL GROSSO Tibor", "VACEK Mathias", "VAN GILS Maxim", "WIDAR Jarno", "SÖDERQVIST Jakob", "VAN EETVELT Lennert", "POOLE Max David", "OMRZEL Jakob", "VAN BAARLE Dylan", "ZINGLE Axel"],
  "T-Dawgs Dogs": ["DEL TORO ROMERO Isaac", "MAGNIER Paul", "BRENNAN Matthew", "PELLIZZARI Giulio", "SEIXAS Paul", "RICCITELLO Matthew", "TOMAS MORGADO António", "NYS Thibau", "DEL GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "DAINESE Alberto", "WIDAR Jarno", "LAMPERTI Luke", "BLACKMORE Joseph", "OMRZEL Jakob", "VLASOV Aleksandr", "PERICAS CAPDEVILA Adria", "TORRES ARIAS Pablo", "AGOSTINACCHIO Mattia"],
  "Gewiss Allan": ["VINGEGAARD HANSEN Jonas", "MAGNIER Paul", "KOOIJ Olav", "MERLIER Tim", "BRENNAN Matthew", "SEIXAS Paul", "RICCITELLO Matthew", "LANDA MEANA Mikel", "RONDEL Mathys", "POOLE Max David", "SEGAERT Alec", "LAMPERTI Luke", "BLACKMORE Joseph", "TEUTENBERG Tim Torn", "FOLDAGER Anders", "VAN BAARLE Dylan", "ZINGLE Axel", "BJERG Mikkel Norsgaard", "HANSEN Peter", "KRON Andreas Lorentz"],
  "Don Karnage": ["EVENEPOEL Remco", "DE LIE Arnaud", "MAGNIER Paul", "GIRMAY Biniam", "SEIXAS Paul", "BITTNER Pavel", "VAN WILDER Ilan", "O'CONNOR Ben", "DEL GROSSO Tibor", "PHILIPSEN Albert", "GROENEWEGEN Dylan", "MOHORIC Matej", "VAN EETVELT Lennert", "POOLE Max David", "LAMPERTI Luke", "LAPORTE Christophe", "KRAGH ANDERSEN Søren", "ZINGLE Axel", "GAVIRIA RENDON Fernando", "KRON Andreas Lorentz"],
  "Team Anders M": ["VAN AERT Wout", "GALL Felix", "KOOIJ Olav", "BRENNAN Matthew", "CHRISTEN Jan", "HIRSCHI Marc", "SEIXAS Paul", "PLAPP Lucas", "ABRAHAMSEN Jonas", "NIELSEN Magnus Cort", "DEL GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "FISHER-BLACK Finn Lachlan Fox", "LEKNESSUND Andreas", "NORDHAGEN Jørgen", "GEOGHEGAN HART Tao", "KRAGH ANDERSEN Søren", "VALGREN Michael", "VAN BAARLE Dylan"]
  "Team Døssing": ["EVENEPOEL Remco", "PHILIPSEN Jasper", "ROGLIČ Primož", "GIRMAY Biniam", "HIRSCHI Marc", "SEIXAS Paul", "MAS Enric", "O'CONNOR Ben", "UIJTDEBROEKS Cian", "KÜNG Stefan", "PHILIPSEN Albert", "VAN GILS Maxim", "GAUDU David", "MOHORIC Matej", "RODRIGUEZ Carlos", "LAPORTE Christophe", "MARTINEZ Daniel", "VLASOV Aleksandr", "ASGREEN Kasper", "VALTER Attila"],
  "Team Vester": ["EVENEPOEL Remco", "VAUQUELIN Kévin", "PHILIPSEN Jasper", "BRENNAN Matthew", "HIRSCHI Marc", "SEIXAS Paul", "TIBERI Antonio", "RICCITELLO Matthew", "LAPEIRA Paul", "LECERF Junior", "WIDAR Jarno", "GAUDU David", "VAN EETVELT Lennert", "RODRIGUEZ Carlos", "COSNEFROY Benoit", "LAPORTE Christophe", "OMRZEL Jakob", "BISIAUX Léo", "AGOSTINACCHIO Mattia", "KRON Andreas"],
  "Team Peter": ["VINGEGAARD Jonas", "ONLEY Oscar", "BRENNAN Matthew", "LUND ANDRESEN Tobias", "KUBIŠ Lukáš", "SEIXAS Paul", "UIJTDEBROEKS Cian", "CORT Magnus", "LECERF Junior", "WIDAR Jarno", "DE BONDT Dries", "VAN EETVELT Lennert", "POOLE Max David", "NORDHAGEN Jørgen", "LAMPERTI Luke", "TEUTENBERG Tim Torn", "ASGREEN Kasper", "MOLARD Rudy", "LEMMEN Bart", "HELLEMOSE Asbjørn"],
  "Kasper Krabber": ["VAN AERT Wout", "MAGNIER Paul", "GANNA Filippo", "ARENSMAN Thymen", "BRENNAN Matthew", "SIMMONS Quinn", "SEIXAS Paul", "MORGADO António", "NYS Thibau", "UIJTDEBROEKS Cian", "GROSSO Tibor", "VACEK Mathias", "VAN GILS Maxim", "WIDAR Jarno", "SÖDERQVIST Jakob", "VAN EETVELT Lennert", "POOLE Max David", "OMRZEL Jakob", "VAN BAARLE Dylan", "ZINGLE Axel"],
  "T-Dawgs Dogs": ["DEL TORO Isaac", "MAGNIER Paul", "BRENNAN Matthew", "PELLIZZARI Giulio", "SEIXAS Paul", "RICCITELLO Matthew", "MORGADO António", "NYS Thibau", "GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "DAINESE Alberto", "WIDAR Jarno", "LAMPERTI Luke", "BLACKMORE Joseph", "OMRZEL Jakob", "VLASOV Aleksandr", "PERICAS Adrià", "TORRES Pablo", "AGOSTINACCHIO Mattia"],
  "Gewiss Allan": ["VINGEGAARD Jonas", "MAGNIER Paul", "KOOIJ Olav", "MERLIER Tim", "BRENNAN Matthew", "SEIXAS Paul", "RICCITELLO Matthew", "LANDA Mikel", "RONDEL Mathys", "POOLE Max David", "SEGAERT Alec", "LAMPERTI Luke", "BLACKMORE Joseph", "TEUTENBERG Tim Torn", "FOLDAGER Anders", "VAN BAARLE Dylan", "ZINGLE Axel", "BJERG Mikkel", "HANSEN Peter", "KRON Andreas"],
  "Don Karnage": ["EVENEPOEL Remco", "DE LIE Arnaud", "MAGNIER Paul", "GIRMAY Biniam", "SEIXAS Paul", "BITTNER Pavel", "VAN WILDER Ilan", "O'CONNOR Ben", "GROSSO Tibor", "PHILIPSEN Albert", "GROENEWEGEN Dylan", "MOHORIC Matej", "VAN EETVELT Lennert", "POOLE Max David", "LAMPERTI Luke", "LAPORTE Christophe", "KRAGH ANDERSEN Søren", "ZINGLE Axel", "Fernando Gaviria", "KRON Andreas"],
  "Team Anders M": ["VAN AERT Wout", "GALL Felix", "KOOIJ Olav", "BRENNAN Matthew", "CHRISTEN Jan", "HIRSCHI Marc", "SEIXAS Paul", "PLAPP Lucas", "ABRAHAMSEN Jonas", "CORT Magnus", "GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "FISHER-BLACK Finn", "LEKNESSUND Andreas", "NORDHAGEN Jørgen", "GEOGHEGAN HART Tao", "KRAGH ANDERSEN Søren", "VALGREN Michael", "VAN BAARLE Dylan"]
};

function CyclingFantasyManager() {
@@ -25,6 +47,14 @@ function CyclingFantasyManager() {
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
@@ -78,9 +108,60 @@ function CyclingFantasyManager() {
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
    const interval = setInterval(fetchPointsFromSheets, 5 * 60 * 1000);
    fetchUpcomingRaces();
    const interval = setInterval(() => {
      fetchPointsFromSheets();
      fetchUpcomingRaces();
    }, 5 * 60 * 1000);
return () => clearInterval(interval);
}, []);

@@ -223,9 +304,102 @@ function CyclingFantasyManager() {
color: 'white'
}}
>
              Indstillinger
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
@@ -345,7 +519,24 @@ function CyclingFantasyManager() {
{index + 1}
</div>
<div>
                            <p style={{ fontWeight: '600', margin: 0, fontSize: '0.875rem', color: index < 3 ? 'black' : 'white' }}>{team.name}</p>
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
