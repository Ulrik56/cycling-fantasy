/**
 * useCyclingFlash - React Hook for CyclingFlash API
 * 
 * Hooks til at hente rytter-data, live status, og resultater
 * fra CyclingFlash backend API.
 * 
 * Usage:
 *   import { useLiveRiders, useRiderProfile } from './useCyclingFlash';
 * 
 *   // I din komponent:
 *   const { liveRiders, isLoading } = useLiveRiders(allRiderNames);
 *   const { rider, isLoading } = useRiderProfile('tadej-pogacar');
 */

import { useState, useEffect, useCallback } from 'react';

// API base URL - ændr til din server
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Fetch wrapper med error handling
 */
async function apiFetch(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

async function apiPost(endpoint, data) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

// =============================================================================
// HOOKS
// =============================================================================

/**
 * Hook til at checke hvilke ryttere der kører i dag
 * 
 * @param {string[]} riderNames - Liste af rytternavne at checke
 * @returns {{ liveRiders: Object, isLoading: boolean, error: Error|null, refresh: Function }}
 * 
 * @example
 * const allRiders = ["EVENEPOEL Remco", "VINGEGAARD Jonas", ...];
 * const { liveRiders, isLoading } = useLiveRiders(allRiders);
 * 
 * // liveRiders = { "EVENEPOEL Remco": { race: "UAE Tour", ... }, ... }
 */
export function useLiveRiders(riderNames) {
  const [liveRiders, setLiveRiders] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    if (!riderNames || riderNames.length === 0) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiPost('/live/check', { riders: riderNames });
      setLiveRiders(data.live || {});
    } catch (err) {
      setError(err);
      console.error('Failed to fetch live riders:', err);
    }
    
    setIsLoading(false);
  }, [riderNames]);

  useEffect(() => {
    refresh();
    
    // Auto-refresh hver 5. minut
    const interval = setInterval(refresh, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { liveRiders, isLoading, error, refresh };
}

/**
 * Hook til at hente rytter profil og resultater
 * 
 * @param {string} slug - Rytter slug (f.eks. 'tadej-pogacar')
 * @returns {{ rider: Object|null, isLoading: boolean, error: Error|null }}
 * 
 * @example
 * const { rider, isLoading } = useRiderProfile('remco-evenepoel');
 * if (rider) {
 *   console.log(rider.name, rider.results);
 * }
 */
export function useRiderProfile(slug) {
  const [rider, setRider] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!slug) {
      setRider(null);
      return;
    }

    const fetchRider = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await apiFetch(`/rider/${slug}`);
        setRider(data);
      } catch (err) {
        setError(err);
        console.error('Failed to fetch rider:', err);
      }
      
      setIsLoading(false);
    };

    fetchRider();
  }, [slug]);

  return { rider, isLoading, error };
}

/**
 * Hook til at hente dagens løb
 * 
 * @returns {{ races: Array, isLoading: boolean, error: Error|null }}
 */
export function useTodayRaces() {
  const [races, setRaces] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRaces = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await apiFetch('/today');
        setRaces(data.races || []);
      } catch (err) {
        setError(err);
        console.error('Failed to fetch today races:', err);
      }
      
      setIsLoading(false);
    };

    fetchRaces();
    
    // Refresh hver 10. minut
    const interval = setInterval(fetchRaces, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return { races, isLoading, error };
}

/**
 * Hook til at hente seneste resultater
 * 
 * @returns {{ results: Array, isLoading: boolean, error: Error|null }}
 */
export function useLatestResults() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await apiFetch('/results/latest');
        setResults(data.results || []);
      } catch (err) {
        setError(err);
        console.error('Failed to fetch latest results:', err);
      }
      
      setIsLoading(false);
    };

    fetchResults();
  }, []);

  return { results, isLoading, error };
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Konverter rytternavn til slug
 * "EVENEPOEL Remco" -> "remco-evenepoel"
 */
export function nameToSlug(name) {
  if (!name) return '';
  
  // Split navn (EFTERNAVN Fornavn -> fornavn-efternavn)
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    // Antag første del er efternavn i CAPS
    const lastName = parts[0];
    const firstName = parts.slice(1).join(' ');
    name = `${firstName} ${lastName}`;
  }
  
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Fjern accenter
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

/**
 * Check om en rytter er live baseret på liveRiders objekt
 */
export function isRiderLive(riderName, liveRiders) {
  return riderName in liveRiders;
}

/**
 * Hent race info for en live rytter
 */
export function getRiderRaceInfo(riderName, liveRiders) {
  return liveRiders[riderName]?.race || null;
}

// =============================================================================
// DEFAULT EXPORT
// =============================================================================

const CyclingFlashAPI = {
  // Hooks
  useLiveRiders,
  useRiderProfile,
  useTodayRaces,
  useLatestResults,
  
  // Utils
  nameToSlug,
  isRiderLive,
  getRiderRaceInfo,
  
  // Direct API calls
  fetchRider: (slug) => apiFetch(`/rider/${slug}`),
  fetchRace: (slug) => apiFetch(`/race/${slug}`),
  fetchToday: () => apiFetch('/today'),
  fetchLive: () => apiFetch('/live'),
  checkLiveRiders: (riders) => apiPost('/live/check', { riders }),
  fetchLatestResults: () => apiFetch('/results/latest'),
  searchRiders: (query) => apiFetch(`/search?q=${encodeURIComponent(query)}`),
};

export default CyclingFlashAPI;
