"""
Rider
=====

Access rider details, including results and statistics.

Examples
--------
>>> rider = Rider('tadej-pogacar')
>>> rider.profile()
{'name': 'Tadej Pogačar', 'nationality': 'Slovenia', ...}

>>> rider.results(2025).head()
   date rank  gc                    race  distance
0  27-04    1      Liège-Bastogne-Liège    252.0km
1  23-04    1           La Flèche Wallonne    205.0km
...
"""

from .api import cf
from .parser import parse_rider_profile, parse_rider_results, extract_rider_slug
import pandas as pd
from typing import Dict, Any, Optional


class Rider:
    """
    Wrapper to load information on riders from CyclingFlash.
    
    Parameters
    ----------
    slug : str
        The rider's URL slug (e.g., 'tadej-pogacar') or full name.
    
    Attributes
    ----------
    slug : str
        The normalized URL slug for the rider.
    
    Examples
    --------
    >>> rider = Rider('tadej-pogacar')
    >>> rider.profile()['name']
    'Tadej Pogačar'
    
    >>> rider = Rider('Mathieu van der Poel')  # Name also works
    >>> rider.results(2024)
    """
    
    def __init__(self, slug: str):
        self.slug = extract_rider_slug(slug)
        self._profile_cache = None
    
    def __repr__(self):
        return f"Rider('{self.slug}')"
    
    def profile(self) -> Dict[str, Any]:
        """
        Get rider profile information.
        
        Returns
        -------
        dict
            Rider details including name, nationality, date of birth, 
            current team, social links, etc.
        
        Examples
        --------
        >>> rider = Rider('remco-evenepoel')
        >>> profile = rider.profile()
        >>> print(profile['name'])
        'Remco Evenepoel'
        """
        if self._profile_cache is None:
            html = cf.get_rider(self.slug)
            self._profile_cache = parse_rider_profile(html)
        return self._profile_cache
    
    def results(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Get rider results for a specific year.
        
        Parameters
        ----------
        year : int, optional
            Year for which to collect results.
            If None, returns current season results.
        
        Returns
        -------
        pd.DataFrame
            Table of rider's race results with columns:
            - date: Race date
            - rank: Finishing position
            - gc: GC position (for stage races)
            - race: Race name
            - race_slug: URL slug for race
            - distance: Stage/race distance
        
        Examples
        --------
        >>> rider = Rider('jonas-vingegaard')
        >>> results_2024 = rider.results(2024)
        >>> results_2024[results_2024['rank'] == '1']  # Victories only
        """
        html = cf.get_rider_results(self.slug, year)
        return parse_rider_results(html)
    
    def wins(self) -> pd.DataFrame:
        """
        Get rider's career victories.
        
        Returns
        -------
        pd.DataFrame
            Table of all victories
        """
        html = cf.get_rider_wins(self.slug)
        return parse_rider_results(html)
    
    def stats(self) -> Dict[str, Any]:
        """
        Get rider statistics.
        
        Returns
        -------
        dict
            Rider statistics including monuments, grand tours, etc.
        """
        html = cf.get_rider_stats(self.slug)
        return parse_rider_profile(html)  # Uses same parser structure
    
    def teams(self) -> pd.DataFrame:
        """
        Get rider's team history.
        
        Returns
        -------
        pd.DataFrame
            Historical teams by year
        """
        html = cf.get_rider_teams(self.slug)
        # Parse team history
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        teams = []
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    year = cells[0].get_text(strip=True)
                    team_link = cells[1].find('a', href=lambda x: x and '/team/' in x)
                    if team_link and year.isdigit():
                        teams.append({
                            'year': int(year),
                            'team': team_link.get_text(strip=True).replace('flag', '').strip(),
                            'team_slug': team_link['href'].replace('/team/', '')
                        })
        
        return pd.DataFrame(teams)
    
    @property
    def name(self) -> str:
        """Get rider's full name."""
        return self.profile().get('name', self.slug)
    
    @property 
    def nationality(self) -> str:
        """Get rider's nationality."""
        return self.profile().get('nationality', '')
    
    @property
    def age(self) -> int:
        """Get rider's age."""
        age_str = self.profile().get('age', '0')
        return int(age_str) if age_str.isdigit() else 0
    
    @property
    def current_team(self) -> str:
        """Get rider's current team name."""
        teams_df = self.teams()
        if not teams_df.empty:
            return teams_df.iloc[0]['team']
        return ''
