/**
 * RiderModal - Modal til at vise rytter detaljer
 * 
 * Viser rytterens profil, seneste resultater, og stats
 * når man klikker på en rytter i fantasy manager.
 */

import React, { useEffect, useState } from 'react';
import { X, Trophy, TrendingUp, Calendar, ExternalLink, Loader } from 'lucide-react';
import { nameToSlug } from './useCyclingFlash';

// API base URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const RiderModal = ({ riderName, onClose, isLive, raceInfo }) => {
  const [rider, setRider] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRider = async () => {
      if (!riderName) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const slug = nameToSlug(riderName);
        const response = await fetch(`${API_BASE}/rider/${slug}`);
        
        if (!response.ok) {
          throw new Error('Kunne ikke hente rytter');
        }
        
        const data = await response.json();
        setRider(data);
      } catch (err) {
        setError(err.message);
        console.error('Failed to fetch rider:', err);
      }
      
      setIsLoading(false);
    };

    fetchRider();
  }, [riderName]);

  // Luk på Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!riderName) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'linear-gradient(to bottom right, #1e293b, #0f172a)',
          borderRadius: '1rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '1.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          alignItems: 'start',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <h2 style={{ 
                margin: 0, 
                fontSize: '1.5rem', 
                fontFamily: "'Bebas Neue', sans-serif",
                letterSpacing: '1px',
                color: 'white'
              }}>
                {riderName}
              </h2>
              
              {isLive && (
                <span style={{
                  background: '#ef4444',
                  color: 'white',
                  fontSize: '0.7rem',
                  fontWeight: 'bold',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  animation: 'pulse 2s infinite'
                }}>
                  <span style={{
                    width: '6px',
                    height: '6px',
                    background: 'white',
                    borderRadius: '50%'
                  }} />
                  LIVE
                </span>
              )}
            </div>
            
            {rider && (
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#9ca3af' }}>
                {rider.team && <span>🚴 {rider.team}</span>}
                {rider.nationality && <span>🌍 {rider.nationality}</span>}
                {rider.age && <span>🎂 {rider.age} år</span>}
              </div>
            )}
            
            {isLive && raceInfo && (
              <div style={{
                marginTop: '0.75rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '0.5rem',
                fontSize: '0.875rem'
              }}>
                <span style={{ color: '#fca5a5' }}>🏁 Kører nu: </span>
                <span style={{ color: 'white', fontWeight: 600 }}>{raceInfo.race}</span>
              </div>
            )}
          </div>
          
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '0.5rem',
              padding: '0.5rem',
              cursor: 'pointer',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X style={{ width: '1.25rem', height: '1.25rem' }} />
          </button>
        </div>
        
        {/* Content */}
        <div style={{ 
          padding: '1.5rem', 
          overflowY: 'auto',
          flex: 1
        }}>
          {isLoading && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              padding: '2rem',
              color: '#9ca3af'
            }}>
              <Loader style={{ width: '1.5rem', height: '1.5rem', animation: 'spin 1s linear infinite' }} />
              <span style={{ marginLeft: '0.5rem' }}>Henter data...</span>
            </div>
          )}
          
          {error && (
            <div style={{
              padding: '1rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '0.5rem',
              color: '#fca5a5',
              textAlign: 'center'
            }}>
              ⚠️ {error}
              <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#9ca3af' }}>
                Data fra CyclingFlash kunne ikke hentes
              </div>
            </div>
          )}
          
          {rider && !isLoading && (
            <>
              {/* Stats */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1rem',
                marginBottom: '1.5rem'
              }}>
                <div style={{
                  background: 'rgba(250, 204, 21, 0.1)',
                  border: '1px solid rgba(250, 204, 21, 0.3)',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  textAlign: 'center'
                }}>
                  <Trophy style={{ width: '1.5rem', height: '1.5rem', color: '#facc15', margin: '0 auto 0.5rem' }} />
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#facc15' }}>
                    {rider.winsThisYear || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Sejre i år</div>
                </div>
                
                <div style={{
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  textAlign: 'center'
                }}>
                  <Calendar style={{ width: '1.5rem', height: '1.5rem', color: '#3b82f6', margin: '0 auto 0.5rem' }} />
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>
                    {rider.results?.length || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Løb kørt</div>
                </div>
                
                <div style={{
                  background: 'rgba(34, 197, 94, 0.1)',
                  border: '1px solid rgba(34, 197, 94, 0.3)',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  textAlign: 'center'
                }}>
                  <TrendingUp style={{ width: '1.5rem', height: '1.5rem', color: '#22c55e', margin: '0 auto 0.5rem' }} />
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#22c55e' }}>
                    {rider.results?.filter(r => ['1', '2', '3'].includes(r.rank)).length || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Podie</div>
                </div>
              </div>
              
              {/* Seneste Resultater */}
              {rider.results && rider.results.length > 0 && (
                <div>
                  <h3 style={{ 
                    fontSize: '1rem', 
                    fontWeight: 600, 
                    marginBottom: '0.75rem',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <TrendingUp style={{ width: '1rem', height: '1rem', color: '#60a5fa' }} />
                    Seneste Resultater
                  </h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {rider.results.slice(0, 10).map((result, idx) => (
                      <div 
                        key={idx}
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          borderRadius: '0.5rem',
                          padding: '0.75rem 1rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          gap: '1rem'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1, minWidth: 0 }}>
                          <div style={{
                            width: '2rem',
                            height: '2rem',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 'bold',
                            fontSize: '0.875rem',
                            flexShrink: 0,
                            background: result.rank === '1' 
                              ? 'linear-gradient(135deg, #FFD700, #FFA500)'
                              : result.rank === '2'
                              ? 'linear-gradient(135deg, #C0C0C0, #A8A8A8)'
                              : result.rank === '3'
                              ? 'linear-gradient(135deg, #CD7F32, #B87333)'
                              : '#334155',
                            color: ['1', '2', '3'].includes(result.rank) ? 'black' : 'white'
                          }}>
                            {result.rank || '-'}
                          </div>
                          
                          <div style={{ minWidth: 0 }}>
                            <div style={{ 
                              fontWeight: 500, 
                              fontSize: '0.875rem',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              color: 'white'
                            }}>
                              {result.race?.replace(/flag/g, '').trim() || 'Ukendt løb'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                              {result.date || ''}
                            </div>
                          </div>
                        </div>
                        
                        {result.distance && (
                          <div style={{ 
                            fontSize: '0.75rem', 
                            color: '#9ca3af',
                            whiteSpace: 'nowrap'
                          }}>
                            {result.distance}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Social links */}
              {rider.social && Object.keys(rider.social).length > 0 && (
                <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  {rider.social.instagram && (
                    <a 
                      href={rider.social.instagram}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        background: 'linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)',
                        color: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        textDecoration: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      📸 Instagram
                      <ExternalLink style={{ width: '0.875rem', height: '0.875rem' }} />
                    </a>
                  )}
                  
                  {rider.social.twitter && (
                    <a 
                      href={rider.social.twitter}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        background: '#1da1f2',
                        color: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        textDecoration: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      𝕏 Twitter
                      <ExternalLink style={{ width: '0.875rem', height: '0.875rem' }} />
                    </a>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default RiderModal;
