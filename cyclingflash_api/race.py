"""
Race
====

Access race details, including results, startlists, and statistics.

Examples
--------
>>> race = Race('tour-de-france-2025')
>>> race.result().head()
   position                rider              team        time
0         1       Tadej Pogačar    UAE Emirates XRG    82:45:12
1         2    Jonas Vingegaard  Visma | Lease a Bike  + 08:32
...

>>> race.startlist()
"""

from .api import cf
from .parser import parse_race_result
import pandas as pd
from typing import Dict, Any, Optional


class Race:
    """
    Wrapper to access race information from CyclingFlash.
    
    Parameters
    ----------
    slug : str
        The race URL slug (e.g., 'tour-de-france-2025')
    
    Attributes
    ----------
    slug : str
        The URL slug for the race.
    
    Examples
    --------
    >>> tdf = Race('tour-de-france-2025')
    >>> tdf.result()  # GC results
    
    >>> tdf.stage_result(21)  # Stage 21 results
    """
    
    def __init__(self, slug: str):
        self.slug = slug
        self._info_cache = None
    
    def __repr__(self):
        return f"Race('{self.slug}')"
    
    def result(self, classification: str = None) -> pd.DataFrame:
        """
        Get race results.
        
        Parameters
        ----------
        classification : str, optional
            Classification type: 'GC', 'points', 'mountain', 'youth'
            If None, returns GC/final results.
        
        Returns
        -------
        pd.DataFrame
            Race results with columns:
            - position: Finishing position
            - rider: Rider name
            - rider_slug: Rider URL slug
            - team: Team name
            - team_slug: Team URL slug
            - time: Finish time or gap
        
        Examples
        --------
        >>> giro = Race('giro-ditalia-2024')
        >>> giro.result()  # GC results
        """
        html = cf.get_race_result(self.slug)
        return parse_race_result(html)
    
    def stage_result(self, stage: int, classification: str = 'SIC') -> pd.DataFrame:
        """
        Get stage results.
        
        Parameters
        ----------
        stage : int
            Stage number (0 for prologue)
        classification : str
            Result type: 'SIC' for stage result, 'GC' for standings after stage
        
        Returns
        -------
        pd.DataFrame
            Stage results
        
        Examples
        --------
        >>> tdf = Race('tour-de-france-2025')
        >>> tdf.stage_result(12)  # Stage 12 results
        """
        stage_str = f"stage-{stage}"
        html = cf.get_race_result(self.slug, stage=stage_str, classification=classification)
        return parse_race_result(html)
    
    def startlist(self) -> pd.DataFrame:
        """
        Get race startlist.
        
        Returns
        -------
        pd.DataFrame
            Startlist with teams and riders
        """
        html = cf.get_race_startlist(self.slug)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        riders = []
        current_team = None
        current_team_slug = None
        
        # Parse startlist structure
        for element in soup.find_all(['h3', 'a']):
            if element.name == 'h3' or (element.name == 'a' and '/team/' in element.get('href', '')):
                if element.name == 'a':
                    current_team = element.get_text(strip=True).replace('flag', '').strip()
                    current_team_slug = element['href'].replace('/team/', '')
            elif element.name == 'a' and '/profile/' in element.get('href', ''):
                rider_name = element.get_text(strip=True).replace('flag', '').strip()
                rider_slug = element['href'].replace('/profile/', '')
                if rider_name and current_team:
                    riders.append({
                        'rider': rider_name,
                        'rider_slug': rider_slug,
                        'team': current_team,
                        'team_slug': current_team_slug
                    })
        
        return pd.DataFrame(riders)
    
    def info(self) -> Dict[str, Any]:
        """
        Get race information.
        
        Returns
        -------
        dict
            Race details including name, date, distance, category
        """
        if self._info_cache is None:
            html = cf.get_race(self.slug)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            self._info_cache = {
                'slug': self.slug
            }
            
            h1 = soup.find('h1')
            if h1:
                self._info_cache['name'] = h1.get_text(strip=True).replace('flag', '').strip()
        
        return self._info_cache
    
    @property
    def name(self) -> str:
        """Get race name."""
        return self.info().get('name', self.slug)


class RaceEdition:
    """
    Convenience class for accessing a specific edition of a recurring race.
    
    Parameters
    ----------
    race_name : str
        Base race name slug (e.g., 'tour-de-france')
    year : int
        Race year
    
    Examples
    --------
    >>> tdf_2024 = RaceEdition('tour-de-france', 2024)
    >>> tdf_2024.result()
    """
    
    def __init__(self, race_name: str, year: int):
        self.race_name = race_name
        self.year = year
        self._race = Race(f"{race_name}-{year}")
    
    def __repr__(self):
        return f"RaceEdition('{self.race_name}', {self.year})"
    
    def __getattr__(self, name):
        return getattr(self._race, name)
