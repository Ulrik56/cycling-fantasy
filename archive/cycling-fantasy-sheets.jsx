import React, { useState, useEffect } from 'react';
import { Trophy, Users, TrendingUp, RefreshCw, Calendar, Award, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

// GOOGLE SHEETS CONFIGURATION
// Erstat med dit eget Sheet ID fra: https://docs.google.com/spreadsheets/d/SHEET_ID_HER/edit
const GOOGLE_SHEET_ID = 'DIT_SHEET_ID_HER';
const GOOGLE_SHEET_NAME = 'Points'; // Navnet på dit sheet tab

// Hold data - importeret fra Excel filer
const TEAMS = {
  "Team Døssing": ["EVENEPOEL Remco", "PHILIPSEN Jasper", "ROGLIČ Primož", "GIRMAY Biniam", "HIRSCHI Marc", "SEIXAS Paul", "MAS NICOLAU Enric", "O'CONNOR Ben", "UIJTDEBROEKS Cian", "KÜNG Stefan", "PHILIPSEN Albert", "VAN GILS Maxim", "GAUDU David", "MOHORIC Matej", "RODRIGUEZ CANO Carlos", "LAPORTE Christophe", "MARTINEZ POVEDA Daniel Felipe", "VLASOV Aleksandr", "ASGREEN Kasper", "VALTER Attila"],
  "Team Vester": ["EVENEPOEL Remco", "VAUQUELIN Kévin", "PHILIPSEN Jasper", "BRENNAN Matthew", "HIRSCHI Marc", "SEIXAS Paul", "TIBERI Antonio", "RICCITELLO Matthew", "LAPEIRA Paul", "LECERF Junior", "WIDAR Jarno", "GAUDU David", "VAN EETVELT Lennert", "RODRIGUEZ CANO Carlos", "COSNEFROY Benoit", "LAPORTE Christophe", "OMRZEL Jakob", "BISIAUX Léo", "AGOSTINACCHIO Mattia", "KRON Andreas Lorentz"],
  "Team Peter": ["VINGEGAARD HANSEN Jonas", "ONLEY Oscar", "BRENNAN Matthew", "LUND ANDRESEN Tobias", "KUBIŠ Lukáš", "SEIXAS Paul", "UIJTDEBROEKS Cian", "NIELSEN Magnus Cort", "LECERF Junior", "WIDAR Jarno", "DE BONDT Dries", "VAN EETVELT Lennert", "POOLE Max David", "NORDHAGEN Jørgen", "LAMPERTI Luke", "TEUTENBERG Tim Torn", "ASGREEN Kasper", "MOLARD Rudy", "LEMMEN Bart", "HELLEMOSE Asbjørn"],
  "Kasper Krabber": ["VAN AERT Wout", "MAGNIER Paul", "GANNA Filippo", "ARENSMAN Thymen", "BRENNAN Matthew", "SIMMONS Quinn", "SEIXAS Paul", "TOMAS MORGADO António", "NYS Thibau", "UIJTDEBROEKS Cian", "DEL GROSSO Tibor", "VACEK Mathias", "VAN GILS Maxim", "WIDAR Jarno", "SÖDERQVIST Jakob", "VAN EETVELT Lennert", "POOLE Max David", "OMRZEL Jakob", "VAN BAARLE Dylan", "ZINGLE Axel"],
  "T-Dawgs Dogs": ["DEL TORO ROMERO Isaac", "MAGNIER Paul", "BRENNAN Matthew", "PELLIZZARI Giulio", "SEIXAS Paul", "RICCITELLO Matthew", "TOMAS MORGADO António", "NYS Thibau", "DEL GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "DAINESE Alberto", "WIDAR Jarno", "LAMPERTI Luke", "BLACKMORE Joseph", "OMRZEL Jakob", "VLASOV Aleksandr", "PERICAS CAPDEVILA Adria", "TORRES ARIAS Pablo", "AGOSTINACCHIO Mattia"],
  "Gewiss Allan": ["VINGEGAARD HANSEN Jonas", "MAGNIER Paul", "KOOIJ Olav", "MERLIER Tim", "BRENNAN Matthew", "SEIXAS Paul", "RICCITELLO Matthew", "LANDA MEANA Mikel", "RONDEL Mathys", "POOLE Max David", "SEGAERT Alec", "LAMPERTI Luke", "BLACKMORE Joseph", "TEUTENBERG Tim Torn", "FOLDAGER Anders", "VAN BAARLE Dylan", "ZINGLE Axel", "BJERG Mikkel Norsgaard", "HANSEN Peter", "KRON Andreas Lorentz"],
  "Don Karnage": ["EVENEPOEL Remco", "DE LIE Arnaud", "MAGNIER Paul", "GIRMAY Biniam", "SEIXAS Paul", "BITTNER Pavel", "VAN WILDER Ilan", "O'CONNOR Ben", "DEL GROSSO Tibor", "PHILIPSEN Albert", "GROENEWEGEN Dylan", "MOHORIC Matej", "VAN EETVELT Lennert", "POOLE Max David", "LAMPERTI Luke", "LAPORTE Christophe", "KRAGH ANDERSEN Søren", "ZINGLE Axel", "GAVIRIA RENDON Fernando", "KRON Andreas Lorentz"]
};

const CyclingFantasyManager = () => {
  const [teams] = useState(TEAMS);
  const [selectedTeam, setSelectedTeam] = useState(Object.keys(TEAMS)[0]);
  const [riderPoints, setRiderPoints] = useState({});
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTeams, setExpandedTeams] = useState({});
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState(null);

  // Fetch points from Google Sheets
  const fetchPointsFromSheets = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const url = `https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/gviz/tq?tqx=out:json&sheet=${GOOGLE_SHEET_NAME}`;
      
      const response = await fetch(url);
      const text = await response.text();
      
      // Google Sheets returnerer JSON med en wrapper - fjern den
      const json = JSON.parse(text.substr(47).slice(0, -2));
      
      const points = {};
      json.table.rows.forEach(row => {
        const rider = row.c[0]?.v; // Kolonne A: Rider name
        const pts = row.c[1]?.v || 0; // Kolonne B: Points
        if (rider && rider !== 'Rider') { // Skip header
          points[rider] = parseInt(pts) || 0;
        }
      });
      
      setRiderPoints(points);
      setLastUpdate(new Date().toLocaleString('da-DK'));
      
      // Gem i localStorage som backup
      localStorage.setItem('cycling-points', JSON.stringify(points));
      localStorage.setItem('cycling-last-update', new Date().toISOString());
      
    } catch (err) {
      console.error('Error fetching from Google Sheets:', err);
      setError('Kunne ikke hente data fra Google Sheets. Check at Sheet ID er korrekt.');
      
      // Forsøg at indlæse fra localStorage
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

  // Load points on mount
  useEffect(() => {
    fetchPointsFromSheets();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchPointsFromSheets, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const calculateTeamPoints = (teamName) => {
    const riders = teams[teamName] || [];
    return riders.reduce((sum, rider) => sum + (riderPoints[rider] || 0), 0);
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
    setExpandedTeams(prev => ({
      ...prev,
      [teamName]: !prev[teamName]
    }));
  };

  const openGoogleSheet = () => {
    window.open(`https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/edit`, '_blank');
  };

  const leaderboard = getLeaderboard();
  const selectedTeamData = selectedTeam ? teams[selectedTeam] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-4 md:p-8">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&display=swap');
        
        * { font-family: 'Rajdhani', sans-serif; }
        .title-font { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; }
        .card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease; }
        .card:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(250, 204, 21, 0.3); transform: translateY(-2px); }
        .btn { transition: all 0.2s ease; }
        .btn:hover { transform: scale(1.05); }
        .btn:active { transform: scale(0.98); }
        .rider-row { animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
        .podium-1 { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
        .podium-2 { background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%); }
        .podium-3 { background: linear-gradient(135deg, #CD7F32 0%, #B87333 100%); }
      `}</style>

      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="title-font text-5xl md:text-7xl text-yellow-400 tracking-wider">
            CYCLING FANTASY
          </h1>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn bg-white/10 px-4 py-2 rounded-lg text-sm"
          >
            Indstillinger
          </button>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-300">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>Sæson 2026</span>
          </div>
          {lastUpdate && (
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4" />
              <span>Opdateret: {lastUpdate}</span>
            </div>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="max-w-7xl mx-auto mb-8 card rounded-xl p-6">
          <h3 className="text-xl font-semibold mb-4">Google Sheets Integration</h3>
          
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 mb-4">
              <p className="text-red-200">{error}</p>
            </div>
          )}
          
          <div className="space-y-4">
            <div className="bg-blue-500/20 border border-blue-500 rounded-lg p-4">
              <p className="text-blue-200 mb-2">
                <strong>Setup Guide:</strong>
              </p>
              <ol className="text-sm text-blue-100 space-y-1 ml-4 list-decimal">
                <li>Opret Google Sheet med ryttere og point</li>
                <li>Publicer sheetet (Fil → Del → Publicer på nettet)</li>
                <li>Kopier Sheet ID fra URL</li>
                <li>Erstat GOOGLE_SHEET_ID i koden</li>
                <li>Opdater point i sheetet - appen henter automatisk!</li>
              </ol>
            </div>

            <div className="flex gap-3">
              <button
                onClick={fetchPointsFromSheets}
                className="btn bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center gap-2"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'Opdaterer...' : 'Opdater Nu'}
              </button>
              
              <button
                onClick={openGoogleSheet}
                className="btn bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Åbn Google Sheet
              </button>
            </div>

            <p className="text-sm text-gray-400">
              Appen henter automatisk nye point hvert 5. minut, eller klik "Opdater Nu"
            </p>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaderboard */}
        <div className="lg:col-span-1">
          <div className="card rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Trophy className="w-6 h-6 text-yellow-400" />
              <h2 className="title-font text-3xl">LIGA STILLING</h2>
            </div>
            
            <div className="space-y-3">
              {leaderboard.map((team, index) => {
                const isSelected = team.name === selectedTeam;
                const podiumClass = index === 0 ? 'podium-1' : index === 1 ? 'podium-2' : index === 2 ? 'podium-3' : '';
                
                return (
                  <div
                    key={team.name}
                    onClick={() => setSelectedTeam(team.name)}
                    className={`p-4 rounded-lg cursor-pointer transition-all ${
                      isSelected 
                        ? 'bg-yellow-500/20 border-2 border-yellow-400' 
                        : 'bg-white/5 border border-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                          podiumClass || 'bg-slate-700'
                        } ${index < 3 ? 'text-black' : 'text-white'}`}>
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-semibold">{team.name}</p>
                          <p className="text-xs text-gray-400">{team.riderCount} ryttere</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-yellow-400">{team.points}</p>
                        <p className="text-xs text-gray-400">point</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Team Details */}
        <div className="lg:col-span-2">
          <div className="card rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Users className="w-6 h-6 text-blue-400" />
                <h2 className="title-font text-3xl">{selectedTeam}</h2>
              </div>
            </div>

            <div className="space-y-2">
              {selectedTeamData.map((rider, index) => (
                <div
                  key={index}
                  className="rider-row bg-white/5 p-4 rounded-lg flex items-center justify-between hover:bg-white/10 transition-all"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-semibold text-lg">{rider}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-green-400" />
                        <span className="text-2xl font-bold text-yellow-400">
                          {riderPoints[rider] || 0}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">UCI point</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* All Teams Overview */}
          <div className="card rounded-xl p-6 mt-6">
            <h3 className="title-font text-2xl mb-4">ALLE HOLD</h3>
            <div className="space-y-2">
              {Object.entries(teams).map(([teamName, riders]) => (
                <div key={teamName} className="bg-white/5 rounded-lg">
                  <div
                    onClick={() => toggleTeamExpand(teamName)}
                    className="p-4 cursor-pointer flex items-center justify-between hover:bg-white/10 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <Award className="w-5 h-5 text-yellow-400" />
                      <span className="font-semibold">{teamName}</span>
                      <span className="text-sm text-gray-400">({riders.length} ryttere)</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xl font-bold text-yellow-400">
                        {calculateTeamPoints(teamName)} point
                      </span>
                      {expandedTeams[teamName] ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </div>
                  </div>
                  {expandedTeams[teamName] && (
                    <div className="px-4 pb-4 space-y-2">
                      {riders.map((rider, index) => (
                        <div key={index} className="flex items-center justify-between py-2 px-3 bg-black/20 rounded">
                          <span>{rider}</span>
                          <span className="text-yellow-400 font-semibold">
                            {riderPoints[rider] || 0} point
                          </span>
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
  );
};

export default CyclingFantasyManager;
