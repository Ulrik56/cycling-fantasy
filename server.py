#!/usr/bin/env python3
"""
CyclingFlash API Server
=======================

Flask backend server that provides cycling data for the Fantasy Cycling Manager app.

Endpoints:
    GET /api/rider/<slug>           - Get rider profile, results, and stats
    GET /api/rider/<slug>/results   - Get rider results for current year
    GET /api/rider/<slug>/live      - Check if rider is racing today
    GET /api/race/<slug>            - Get race info and results
    GET /api/race/<slug>/startlist  - Get race startlist
    GET /api/today                  - Get today's races and startlists
    GET /api/live                   - Get all riders racing today
    GET /api/results/latest         - Get latest race results

Usage:
    python server.py

    # Or with gunicorn for production:
    gunicorn -w 4 -b 0.0.0.0:5000 server:app
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date
import re
import sys
import os

# Tilføj current directory til path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Prøv relative imports først (når kørt som modul)
    from .api import cf
    from .parser import (
        parse_rider_profile, 
        parse_rider_results, 
        parse_race_result,
        parse_latest_results,
        extract_rider_slug
    )
    from .rider import Rider
    from .race import Race
    from .ranking import Ranking
except ImportError:
    # Fallback til direkte imports (når kørt som script)
    from api import cf
    from parser import (
        parse_rider_profile, 
        parse_rider_results, 
        parse_race_result,
        parse_latest_results,
        extract_rider_slug
    )
    from rider import Rider
    from race import Race
    from ranking import Ranking

app = Flask(__name__)
CORS(app)  # Tillad requests fra React app

# Cache til at reducere requests til CyclingFlash
_cache = {}
_cache_ttl = 300  # 5 minutter

def get_cached(key, fetch_func):
    """Simple cache med TTL."""
    now = datetime.now().timestamp()
    if key in _cache:
        data, timestamp = _cache[key]
        if now - timestamp < _cache_ttl:
            return data
    
    data = fetch_func()
    _cache[key] = (data, now)
    return data


# =============================================================================
# RIDER ENDPOINTS
# =============================================================================

@app.route('/api/rider/<slug>')
def get_rider(slug):
    """
    Get complete rider profile with recent results.
    
    Returns:
        {
            "slug": "tadej-pogacar",
            "name": "Tadej Pogačar",
            "nationality": "Slovenia",
            "age": 27,
            "team": "UAE Emirates XRG",
            "dateOfBirth": "21-09-1998",
            "social": {...},
            "results": [...],
            "wins": 119,
            "isLive": false,
            "currentRace": null
        }
    """
    try:
        rider = Rider(slug)
        profile = rider.profile()
        
        # Hent resultater
        try:
            results_df = rider.results()
            results = results_df.head(20).to_dict('records') if not results_df.empty else []
        except:
            results = []
        
        # Tæl sejre
        wins_count = len([r for r in results if r.get('rank') == '1'])
        
        # Check om rytteren kører i dag
        is_live, current_race = check_rider_live(slug)
        
        return jsonify({
            "slug": slug,
            "name": profile.get('name', slug),
            "firstName": profile.get('first_name', ''),
            "lastName": profile.get('last_name', ''),
            "nationality": profile.get('nationality', ''),
            "age": profile.get('age', ''),
            "dateOfBirth": profile.get('date_of_birth', ''),
            "team": rider.current_team,
            "social": profile.get('social', {}),
            "results": results,
            "winsThisYear": wins_count,
            "isLive": is_live,
            "currentRace": current_race
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rider/<slug>/results')
def get_rider_results(slug):
    """Get rider results, optionally filtered by year."""
    try:
        year = request.args.get('year', type=int)
        rider = Rider(slug)
        results_df = rider.results(year)
        
        if results_df.empty:
            return jsonify({"results": []})
        
        return jsonify({
            "slug": slug,
            "year": year,
            "results": results_df.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rider/<slug>/live')
def get_rider_live_status(slug):
    """Check if rider is racing today."""
    try:
        is_live, current_race = check_rider_live(slug)
        return jsonify({
            "slug": slug,
            "isLive": is_live,
            "currentRace": current_race
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def check_rider_live(slug):
    """
    Check if a rider is on a startlist for today's races.
    Returns (is_live: bool, race_info: dict or None)
    """
    try:
        today_races = get_cached('today_races', fetch_today_races)
        
        rider_name_lower = slug.lower().replace('-', ' ')
        
        for race in today_races:
            startlist = race.get('startlist', [])
            for rider in startlist:
                rider_slug = rider.get('rider_slug', '').lower()
                if rider_slug == slug or slug in rider_slug:
                    return True, {
                        "race": race.get('name'),
                        "raceSlug": race.get('slug'),
                        "date": race.get('date')
                    }
        
        return False, None
        
    except:
        return False, None


# =============================================================================
# RACE ENDPOINTS
# =============================================================================

@app.route('/api/race/<slug>')
def get_race(slug):
    """Get race info and results."""
    try:
        race = Race(slug)
        info = race.info()
        
        try:
            results_df = race.result()
            results = results_df.head(20).to_dict('records') if not results_df.empty else []
        except:
            results = []
        
        return jsonify({
            "slug": slug,
            "name": info.get('name', slug),
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/race/<slug>/startlist')
def get_race_startlist(slug):
    """Get race startlist."""
    try:
        race = Race(slug)
        startlist_df = race.startlist()
        
        if startlist_df.empty:
            return jsonify({"startlist": []})
        
        return jsonify({
            "slug": slug,
            "startlist": startlist_df.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# TODAY / LIVE ENDPOINTS
# =============================================================================

def fetch_today_races():
    """Fetch today's races with startlists."""
    races = []
    
    try:
        # Hent latest results page som indeholder dagens løb
        html = cf.get_latest_results()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        today = date.today()
        today_str = today.strftime("%d.%m")
        
        # Find links til dagens løb
        for link in soup.find_all('a', href=re.compile(r'/race/.*-2026')):
            race_slug = link['href'].replace('/race/', '').split('/')[0]
            race_name = link.get_text(strip=True).replace('flag', '').strip()
            
            # Hent startliste for løbet
            try:
                race = Race(race_slug)
                startlist_df = race.startlist()
                startlist = startlist_df.to_dict('records') if not startlist_df.empty else []
            except:
                startlist = []
            
            races.append({
                "slug": race_slug,
                "name": race_name,
                "date": today_str,
                "startlist": startlist
            })
            
            # Begræns til 5 løb for performance
            if len(races) >= 5:
                break
                
    except Exception as e:
        print(f"Error fetching today's races: {e}")
    
    return races


@app.route('/api/today')
def get_today():
    """Get today's races with startlists."""
    try:
        races = get_cached('today_races', fetch_today_races)
        return jsonify({
            "date": date.today().isoformat(),
            "races": races
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/live')
def get_live_riders():
    """
    Get all riders that are racing today.
    Useful for marking riders as "LIVE" in the fantasy app.
    """
    try:
        races = get_cached('today_races', fetch_today_races)
        
        live_riders = {}
        
        for race in races:
            race_info = {
                "race": race.get('name'),
                "raceSlug": race.get('slug')
            }
            
            for rider in race.get('startlist', []):
                slug = rider.get('rider_slug', '')
                if slug and slug not in live_riders:
                    live_riders[slug] = {
                        "slug": slug,
                        "name": rider.get('rider', ''),
                        "team": rider.get('team', ''),
                        "race": race_info
                    }
        
        return jsonify({
            "date": date.today().isoformat(),
            "count": len(live_riders),
            "riders": list(live_riders.values())
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/live/check', methods=['POST'])
def check_live_riders():
    """
    Check which riders from a list are racing today.
    
    Request body:
        {"riders": ["EVENEPOEL Remco", "POGAČAR Tadej", ...]}
    
    Returns:
        {"live": {"EVENEPOEL Remco": {...}, ...}}
    """
    try:
        data = request.get_json()
        rider_names = data.get('riders', [])
        
        races = get_cached('today_races', fetch_today_races)
        
        # Byg lookup af alle live ryttere
        live_lookup = {}
        for race in races:
            race_info = {
                "race": race.get('name'),
                "raceSlug": race.get('slug')
            }
            for rider in race.get('startlist', []):
                name = rider.get('rider', '').upper()
                slug = rider.get('rider_slug', '')
                live_lookup[name] = {
                    "slug": slug,
                    "team": rider.get('team', ''),
                    "race": race_info
                }
        
        # Check hver rytter fra input
        result = {}
        for name in rider_names:
            name_upper = name.upper()
            if name_upper in live_lookup:
                result[name] = live_lookup[name_upper]
            else:
                # Prøv fuzzy match (efternavn match)
                last_name = name_upper.split()[0] if name_upper else ''
                for live_name, info in live_lookup.items():
                    if last_name and last_name in live_name:
                        result[name] = info
                        break
        
        return jsonify({
            "date": date.today().isoformat(),
            "live": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# RESULTS ENDPOINTS
# =============================================================================

@app.route('/api/results/latest')
def get_latest_results():
    """Get latest race results."""
    try:
        html = cf.get_latest_results()
        results = parse_latest_results(html)
        
        return jsonify({
            "results": results[:20]  # Begræns til 20
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# RANKINGS ENDPOINTS
# =============================================================================

@app.route('/api/rankings/<ranking_type>')
def get_rankings(ranking_type):
    """Get rankings (overall, gc, sprint, mountain, etc.)"""
    try:
        gender = request.args.get('gender', 'men-elite')
        limit = request.args.get('limit', 50, type=int)
        
        ranking_df = Ranking.get(ranking_type, 'cyclingflash-365-ranking', gender)
        
        if ranking_df.empty:
            return jsonify({"rankings": []})
        
        return jsonify({
            "type": ranking_type,
            "gender": gender,
            "rankings": ranking_df.head(limit).to_dict('records')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.route('/api/search')
def search():
    """Search for riders by name."""
    query = request.args.get('q', '').lower()
    
    if len(query) < 2:
        return jsonify({"results": []})
    
    try:
        # Søg i overall ranking
        ranking_df = Ranking.overall('men-elite')
        
        results = []
        for _, row in ranking_df.iterrows():
            name = row.get('rider', '')
            if query in name.lower():
                results.append({
                    "name": name,
                    "slug": row.get('rider_slug', ''),
                    "team": row.get('team', ''),
                    "position": row.get('position', '')
                })
            
            if len(results) >= 10:
                break
        
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("🚴 CyclingFlash API Server starting...")
    print("📡 Endpoints available:")
    print("   GET /api/rider/<slug>         - Rider profile")
    print("   GET /api/rider/<slug>/live    - Check if racing today")
    print("   GET /api/race/<slug>          - Race results")
    print("   GET /api/today                - Today's races")
    print("   GET /api/live                 - All riders racing today")
    print("   POST /api/live/check          - Check specific riders")
    print("   GET /api/results/latest       - Latest results")
    print("   GET /api/health               - Health check")
    print("")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
else:
    # Når kørt via gunicorn, log startup
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("🚴 CyclingFlash API Server starting via WSGI...")
