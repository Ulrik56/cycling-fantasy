"""
Fantasy Manager Integration
===========================

Provides tools to integrate CyclingFlash data with fantasy cycling managers.

This module helps:
- Fetch real rider data and convert to fantasy format
- Calculate expected points based on historical results
- Estimate rider values based on rankings
- Track rider form

Examples
--------
>>> from cyclingflash_api.fantasy import FantasyManager

>>> fm = FantasyManager()
>>> riders = fm.get_top_riders(limit=100)
>>> print(riders[0])
{'name': 'Tadej Pogačar', 'team': 'UAE Emirates XRG', 'value': 60, 'expectedPoints': 6500, ...}
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from .api import cf
from .parser import parse_ranking, parse_rider_profile, parse_rider_results
from .rider import Rider
from .ranking import Ranking


class FantasyManager:
    """
    Fantasy cycling manager integration.
    
    Fetches real data from CyclingFlash and converts it to
    a format suitable for fantasy cycling games.
    
    Parameters
    ----------
    total_budget : int
        Total budget in millions (default: 100)
    max_team_size : int
        Maximum riders on a team (default: 20)
    max_per_team : int
        Maximum riders from same pro team (default: 3)
    
    Examples
    --------
    >>> fm = FantasyManager()
    >>> riders = fm.get_top_riders(50)
    >>> gc_specialists = fm.get_specialists('gc', 20)
    """
    
    # Value tiers based on ranking position
    VALUE_TIERS = [
        (1, 5, 55, 65),      # Top 5: 55-65M
        (6, 10, 45, 54),     # 6-10: 45-54M
        (11, 20, 35, 44),    # 11-20: 35-44M
        (21, 35, 25, 34),    # 21-35: 25-34M
        (36, 50, 18, 24),    # 36-50: 18-24M
        (51, 75, 12, 17),    # 51-75: 12-17M
        (76, 100, 8, 11),    # 76-100: 8-11M
        (101, 150, 5, 7),    # 101-150: 5-7M
        (151, 250, 3, 4),    # 151-250: 3-4M
        (251, 500, 1, 2),    # 251+: 1-2M
    ]
    
    # Points multipliers for different ranking types
    SPECIALTY_MULTIPLIERS = {
        'overall': 1.0,
        'gc': 1.2,
        'sprint': 0.9,
        'mountain': 1.0,
        'hill': 1.0,
        'timetrial': 0.8,
    }
    
    def __init__(self, total_budget: int = 100, max_team_size: int = 20, 
                 max_per_team: int = 3):
        self.total_budget = total_budget
        self.max_team_size = max_team_size
        self.max_per_team = max_per_team
        self._ranking_cache = {}
    
    def _estimate_value(self, position: int) -> int:
        """Estimate rider value based on ranking position."""
        for min_pos, max_pos, min_val, max_val in self.VALUE_TIERS:
            if min_pos <= position <= max_pos:
                # Linear interpolation within tier
                range_pos = max_pos - min_pos
                range_val = max_val - min_val
                if range_pos == 0:
                    return max_val
                offset = position - min_pos
                return max_val - int((offset / range_pos) * range_val)
        return 1  # Minimum value
    
    def _estimate_points(self, position: int, ranking_type: str = 'overall') -> int:
        """Estimate expected points based on ranking position."""
        # Base points formula: top rider ~6500, decreasing logarithmically
        if position <= 0:
            return 0
        
        base_points = max(100, int(7000 / (1 + (position - 1) * 0.05)))
        multiplier = self.SPECIALTY_MULTIPLIERS.get(ranking_type, 1.0)
        
        return int(base_points * multiplier)
    
    def get_ranking(self, ranking_type: str = 'overall', 
                    gender: str = 'men-elite',
                    rolling: bool = True) -> pd.DataFrame:
        """
        Get ranking data with caching.
        
        Parameters
        ----------
        ranking_type : str
            Type: 'overall', 'gc', 'sprint', 'mountain', 'hill', 'timetrial'
        gender : str
            Gender category
        rolling : bool
            Use 365-day rolling ranking
        
        Returns
        -------
        pd.DataFrame
            Ranking data
        """
        cache_key = f"{ranking_type}_{gender}_{rolling}"
        
        if cache_key not in self._ranking_cache:
            self._ranking_cache[cache_key] = Ranking.get(
                ranking_type,
                'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking',
                gender
            )
        
        return self._ranking_cache[cache_key]
    
    def get_top_riders(self, limit: int = 50, 
                       gender: str = 'men-elite') -> List[Dict[str, Any]]:
        """
        Get top riders formatted for fantasy manager.
        
        Parameters
        ----------
        limit : int
            Number of riders to return
        gender : str
            Gender category
        
        Returns
        -------
        list
            List of rider dicts with fantasy-relevant fields:
            - id: Unique identifier
            - name: Rider name
            - slug: URL slug
            - team: Team name
            - team_slug: Team URL slug  
            - value: Estimated value in millions
            - expectedPoints: Estimated season points
            - position: Ranking position
            - nationality: Country code (if available)
        
        Examples
        --------
        >>> fm = FantasyManager()
        >>> riders = fm.get_top_riders(50)
        >>> riders[0]
        {'id': 1, 'name': 'Tadej Pogačar', 'value': 60, ...}
        """
        ranking = self.get_ranking('overall', gender)
        
        riders = []
        for idx, row in ranking.head(limit).iterrows():
            position = int(row.get('position', idx + 1))
            
            rider = {
                'id': idx + 1,
                'name': row.get('rider', '').strip(),
                'slug': row.get('rider_slug', ''),
                'team': row.get('team', '').strip(),
                'team_slug': row.get('team_slug', ''),
                'value': self._estimate_value(position),
                'expectedPoints': self._estimate_points(position),
                'position': position,
                'selected': False,
            }
            
            if rider['name']:
                riders.append(rider)
        
        return riders
    
    def get_specialists(self, specialty: str, limit: int = 30,
                        gender: str = 'men-elite') -> List[Dict[str, Any]]:
        """
        Get specialists in a specific discipline.
        
        Parameters
        ----------
        specialty : str
            Specialty type: 'gc', 'sprint', 'mountain', 'hill', 'timetrial'
        limit : int
            Number of riders to return
        gender : str
            Gender category
        
        Returns
        -------
        list
            List of specialist riders
        """
        ranking = self.get_ranking(specialty, gender)
        
        riders = []
        for idx, row in ranking.head(limit).iterrows():
            position = int(row.get('position', idx + 1))
            
            rider = {
                'id': idx + 1,
                'name': row.get('rider', '').strip(),
                'slug': row.get('rider_slug', ''),
                'team': row.get('team', '').strip(),
                'team_slug': row.get('team_slug', ''),
                'value': self._estimate_value(position),
                'expectedPoints': self._estimate_points(position, specialty),
                'position': position,
                'specialty': specialty,
                'selected': False,
            }
            
            if rider['name']:
                riders.append(rider)
        
        return riders
    
    def get_rider_details(self, slug: str) -> Dict[str, Any]:
        """
        Get detailed rider information for fantasy.
        
        Parameters
        ----------
        slug : str
            Rider URL slug
        
        Returns
        -------
        dict
            Detailed rider info including recent results
        """
        rider = Rider(slug)
        profile = rider.profile()
        
        # Get recent results
        try:
            results = rider.results()
            wins_this_year = len(results[results['rank'] == '1'])
            podiums_this_year = len(results[results['rank'].isin(['1', '2', '3'])])
        except:
            wins_this_year = 0
            podiums_this_year = 0
        
        return {
            'slug': slug,
            'name': profile.get('name', slug),
            'nationality': profile.get('nationality', ''),
            'age': profile.get('age', ''),
            'team': rider.current_team,
            'wins_this_year': wins_this_year,
            'podiums_this_year': podiums_this_year,
            'social': profile.get('social', {}),
        }
    
    def calculate_form(self, slug: str, last_n_results: int = 10) -> float:
        """
        Calculate rider form based on recent results.
        
        Parameters
        ----------
        slug : str
            Rider URL slug
        last_n_results : int
            Number of recent results to consider
        
        Returns
        -------
        float
            Form score (0-100, higher is better)
        """
        rider = Rider(slug)
        
        try:
            results = rider.results()
        except:
            return 50.0  # Default form
        
        if results.empty:
            return 50.0
        
        # Take last N results
        recent = results.head(last_n_results)
        
        form_score = 0.0
        for idx, row in recent.iterrows():
            rank = row.get('rank', '')
            try:
                pos = int(rank)
                # Points: 1st=100, 2nd=80, 3rd=65, etc.
                if pos == 1:
                    form_score += 100
                elif pos == 2:
                    form_score += 80
                elif pos == 3:
                    form_score += 65
                elif pos <= 5:
                    form_score += 50
                elif pos <= 10:
                    form_score += 35
                elif pos <= 20:
                    form_score += 20
                else:
                    form_score += 10
            except ValueError:
                form_score += 5  # DNF/DNS
        
        return min(100, form_score / last_n_results)
    
    def suggest_team(self, budget: int = None, 
                     strategy: str = 'balanced') -> List[Dict[str, Any]]:
        """
        Suggest an optimal fantasy team.
        
        Parameters
        ----------
        budget : int
            Available budget (default: total_budget)
        strategy : str
            Team building strategy:
            - 'balanced': Mix of stars and value picks
            - 'stars': Focus on top riders
            - 'value': Focus on value picks
            - 'gc': Focus on GC riders
            - 'classics': Focus on classics specialists
        
        Returns
        -------
        list
            Suggested team of riders
        """
        budget = budget or self.total_budget
        
        # Get riders from different rankings
        overall = self.get_top_riders(100)
        
        team = []
        remaining_budget = budget
        team_counts = {}  # Track riders per pro team
        
        if strategy == 'stars':
            # Pick best riders that fit budget
            for rider in overall:
                if self._can_add_rider(rider, team, remaining_budget, team_counts):
                    team.append(rider)
                    remaining_budget -= rider['value']
                    team_counts[rider['team']] = team_counts.get(rider['team'], 0) + 1
                
                if len(team) >= self.max_team_size:
                    break
        
        elif strategy == 'value':
            # Sort by points per million
            value_sorted = sorted(overall, 
                                  key=lambda r: r['expectedPoints'] / max(1, r['value']),
                                  reverse=True)
            for rider in value_sorted:
                if self._can_add_rider(rider, team, remaining_budget, team_counts):
                    team.append(rider)
                    remaining_budget -= rider['value']
                    team_counts[rider['team']] = team_counts.get(rider['team'], 0) + 1
                
                if len(team) >= self.max_team_size:
                    break
        
        else:  # balanced
            # Pick some stars, then fill with value
            stars = overall[:10]
            value_picks = sorted(overall[10:], 
                                key=lambda r: r['expectedPoints'] / max(1, r['value']),
                                reverse=True)
            
            # Add 3-4 stars
            for rider in stars[:4]:
                if self._can_add_rider(rider, team, remaining_budget, team_counts):
                    team.append(rider)
                    remaining_budget -= rider['value']
                    team_counts[rider['team']] = team_counts.get(rider['team'], 0) + 1
            
            # Fill with value picks
            for rider in value_picks:
                if self._can_add_rider(rider, team, remaining_budget, team_counts):
                    team.append(rider)
                    remaining_budget -= rider['value']
                    team_counts[rider['team']] = team_counts.get(rider['team'], 0) + 1
                
                if len(team) >= self.max_team_size:
                    break
        
        return team
    
    def _can_add_rider(self, rider: Dict, team: List, 
                       budget: int, team_counts: Dict) -> bool:
        """Check if rider can be added to team."""
        if len(team) >= self.max_team_size:
            return False
        if rider['value'] > budget:
            return False
        if team_counts.get(rider['team'], 0) >= self.max_per_team:
            return False
        if any(r['slug'] == rider['slug'] for r in team):
            return False
        return True
    
    def export_to_json(self, riders: List[Dict]) -> str:
        """
        Export riders to JSON format for React app.
        
        Parameters
        ----------
        riders : list
            List of rider dicts
        
        Returns
        -------
        str
            JSON string
        """
        import json
        return json.dumps(riders, indent=2, ensure_ascii=False)
    
    def export_to_tsx(self, riders: List[Dict], 
                      variable_name: str = 'riders') -> str:
        """
        Export riders as TypeScript/JSX array.
        
        Parameters
        ----------
        riders : list
            List of rider dicts
        variable_name : str
            JavaScript variable name
        
        Returns
        -------
        str
            TypeScript code
        """
        lines = [f"const {variable_name} = ["]
        
        for rider in riders:
            lines.append(f"  {{")
            lines.append(f"    id: {rider['id']},")
            lines.append(f'    name: "{rider["name"]}",')
            lines.append(f'    team: "{rider["team"]}",')
            lines.append(f"    value: {rider['value']},")
            lines.append(f"    expectedPoints: {rider['expectedPoints']},")
            lines.append(f"    selected: false,")
            lines.append(f"  }},")
        
        lines.append("];")
        
        return "\n".join(lines)
