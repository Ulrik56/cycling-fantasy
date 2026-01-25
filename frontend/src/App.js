import React, { useState, useEffect } from 'react';
import { Trophy, Users, TrendingUp, RefreshCw, Calendar, Award, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

// GOOGLE SHEETS CONFIGURATION
const GOOGLE_SHEET_ID = '1RfoTiYhMI-Yr7123evM4_PeSYn87W20UCBerhqV_Ztg'; // ERSTAT MED DIT SHEET ID

// Hold data
const TEAMS = {
  "Team Døssing": ["EVENEPOEL Remco", "PHILIPSEN Jasper", "ROGLIČ Primož", "GIRMAY Biniam", "HIRSCHI Marc", "SEIXAS Paul", "MAS NICOLAU Enric", "O'CONNOR Ben", "UIJTDEBROEKS Cian", "KÜNG Stefan", "PHILIPSEN Albert", "VAN GILS Maxim", "GAUDU David", "MOHORIC Matej", "RODRIGUEZ CANO Carlos", "LAPORTE Christophe", "MARTINEZ POVEDA Daniel Felipe", "VLASOV Aleksandr", "ASGREEN Kasper", "VALTER Attila"],
  "Team Vester": ["EVENEPOEL Remco", "VAUQUELIN Kévin", "PHILIPSEN Jasper", "BRENNAN Matthew", "HIRSCHI Marc", "SEIXAS Paul", "TIBERI Antonio", "RICCITELLO Matthew", "LAPEIRA Paul", "LECERF Junior", "WIDAR Jarno", "GAUDU David", "VAN EETVELT Lennert", "RODRIGUEZ CANO Carlos", "COSNEFROY Benoit", "LAPORTE Christophe", "OMRZEL Jakob", "BISIAUX Léo", "AGOSTINACCHIO Mattia", "KRON Andreas Lorentz"],
  "Team Peter": ["VINGEGAARD HANSEN Jonas", "ONLEY Oscar", "BRENNAN Matthew", "LUND ANDRESEN Tobias", "KUBIŠ Lukáš", "SEIXAS Paul", "UIJTDEBROEKS Cian", "NIELSEN Magnus Cort", "LECERF Junior", "WIDAR Jarno", "DE BONDT Dries", "VAN EETVELT Lennert", "POOLE Max David", "NORDHAGEN Jørgen", "LAMPERTI Luke", "TEUTENBERG Tim Torn", "ASGREEN Kasper", "MOLARD Rudy", "LEMMEN Bart", "HELLEMOSE Asbjørn"],
  "Kasper Krabber": ["VAN AERT Wout", "MAGNIER Paul", "GANNA Filippo", "ARENSMAN Thymen", "BRENNAN Matthew", "SIMMONS Quinn", "SEIXAS Paul", "TOMAS MORGADO António", "NYS Thibau", "UIJTDEBROEKS Cian", "DEL GROSSO Tibor", "VACEK Mathias", "VAN GILS Maxim", "WIDAR Jarno", "SÖDERQVIST Jakob", "VAN EETVELT Lennert", "POOLE Max David", "OMRZEL Jakob", "VAN BAARLE Dylan", "ZINGLE Axel"],
  "T-Dawgs Dogs": ["DEL TORO ROMERO Isaac", "MAGNIER Paul", "BRENNAN Matthew", "PELLIZZARI Giulio", "SEIXAS Paul", "RICCITELLO Matthew", "TOMAS MORGADO António", "NYS Thibau", "DEL GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "DAINESE Alberto", "WIDAR Jarno", "LAMPERTI Luke", "BLACKMORE Joseph", "OMRZEL Jakob", "VLASOV Aleksandr", "PERICAS CAPDEVILA Adria", "TORRES ARIAS Pablo", "AGOSTINACCHIO Mattia"],
  "Gewiss Allan": ["VINGEGAARD HANSEN Jonas", "MAGNIER Paul", "KOOIJ Olav", "MERLIER Tim", "BRENNAN Matthew", "SEIXAS Paul", "RICCITELLO Matthew", "LANDA MEANA Mikel", "RONDEL Mathys", "POOLE Max David", "SEGAERT Alec", "LAMPERTI Luke", "BLACKMORE Joseph", "TEUTENBERG Tim Torn", "FOLDAGER Anders", "VAN BAARLE Dylan", "ZINGLE Axel", "BJERG Mikkel Norsgaard", "HANSEN Peter", "KRON Andreas Lorentz"],
  "Don Karnage": ["EVENEPOEL Remco", "DE LIE Arnaud", "MAGNIER Paul", "GIRMAY Biniam", "SEIXAS Paul", "BITTNER Pavel", "VAN WILDER Ilan", "O'CONNOR Ben", "DEL GROSSO Tibor", "PHILIPSEN Albert", "GROENEWEGEN Dylan", "MOHORIC Matej", "VAN EETVELT Lennert", "POOLE Max David", "LAMPERTI Luke", "LAPORTE Christophe", "KRAGH ANDERSEN Søren", "ZINGLE Axel", "GAVIRIA RENDON Fernando", "KRON Andreas Lorentz"],
  "Team Anders M": ["VAN AERT Wout", "GALL Felix", "KOOIJ Olav", "BRENNAN Matthew", "CHRISTEN Jan", "HIRSCHI Marc", "SEIXAS Paul", "PLAPP Lucas", "ABRAHAMSEN Jonas", "NIELSEN Magnus Cort", "DEL GROSSO Tibor", "PHILIPSEN Albert", "VACEK Mathias", "FISHER-BLACK Finn Lachlan Fox", "LEKNESSUND Andreas", "NORDHAGEN Jørgen", "GEOGHEGAN HART Tao", "KRAGH ANDERSEN Søren", "VALGREN Michael", "VAN BAARLE Dylan"]
};

function CyclingFantasyManager() {
  const [teams] = useState(TEAMS);
  const [selectedTeam, setSelectedTeam] = useState(Object.keys(TEAMS)[0]);
  const [riderPoints, setRiderPoints] = useState({});
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTeams, setExpandedTeams] = useState({});
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState(null);

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
      
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const parts = line.split(',');
        if (parts.length >= 2) {
          const rider = parts[0].trim().replace(/"/g, '');
          const pts = parseInt(parts[1]) || 0;
          if (rider) points[rider] = pts;
        }
      }
      
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

  useEffect(() => {
    fetchPointsFromSheets();
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
              Indstillinger
            </button>
          </div>
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
                            <p style={{ fontWeight: '600', margin: 0, fontSize: '0.875rem', color: index < 3 ? 'black' : 'white' }}>{team.name}</p>
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
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{
                        width: '2.5rem',
                        height: '2.5rem',
                        background: 'linear-gradient(135deg, #3b82f6, #9333ea)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold'
                      }}>
                        {index + 1}
                      </div>
                      <p style={{ fontWeight: '600', fontSize: '1.125rem', margin: 0 }}>{rider}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <TrendingUp style={{ width: '1rem', height: '1rem', color: '#4ade80' }} />
                        <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#facc15' }}>
                          {riderPoints[rider] || 0}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: 0 }}>UCI point</p>
                    </div>
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
                            fontSize: '0.875rem'
                          }}>
                            <span>{rider}</span>
                            <span style={{ color: '#facc15', fontWeight: '600' }}>
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
    </>
  );
}

export default CyclingFantasyManager;