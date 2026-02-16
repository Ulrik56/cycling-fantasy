"""
Ranking
=======

Access various cycling rankings from CyclingFlash.

Examples
--------
>>> from cyclingflash_api import Ranking

>>> # Overall ranking for men elite
>>> overall = Ranking.overall('men-elite')
>>> overall.head()
   position            rider                       team  points
0         1    Tadej Pogačar           UAE Emirates XRG    4500
1         2  Jonas Vingegaard     Team Visma | Lease a Bike    3800
...

>>> # Sprint ranking for women elite
>>> sprint = Ranking.sprint('women-elite')
"""

from .api import cf
from .parser import parse_ranking
import pandas as pd
from typing import Optional


class Ranking:
    """
    Access CyclingFlash rankings.
    
    CyclingFlash offers several ranking types:
    - cyclingflash-ranking: Current season ranking
    - cyclingflash-365-ranking: Rolling 365-day ranking
    - road-victory-ranking: Victory count ranking
    - team-ranking: Team rankings
    - team-365-ranking: Rolling team rankings
    
    Examples
    --------
    >>> # Get overall ranking
    >>> df = Ranking.overall('men-elite')
    
    >>> # Get custom ranking
    >>> df = Ranking.get('gc', 'cyclingflash-365-ranking', 'women-elite')
    """
    
    RANKING_TYPES = [
        'overall', 'gc', 'hill', 'mountain', 'timetrial', 'sprint', 'cyclocross'
    ]
    
    CATEGORIES = [
        'cyclingflash-ranking',
        'cyclingflash-365-ranking', 
        'road-victory-ranking',
        'team-ranking',
        'team-365-ranking',
        'cyclocross-victory-ranking'
    ]
    
    GENDERS = [
        'men-elite', 'women-elite', 'men-u23', 'women-u23', 
        'men-juniors', 'women-juniors'
    ]
    
    @classmethod
    def get(cls, ranking_type: str, category: str = 'cyclingflash-ranking', 
            gender: str = 'men-elite') -> pd.DataFrame:
        """
        Get a specific ranking.
        
        Parameters
        ----------
        ranking_type : str
            Type of ranking: 'overall', 'gc', 'hill', 'mountain', 
            'timetrial', 'sprint', 'cyclocross'
        category : str
            Ranking category:
            - 'cyclingflash-ranking': Current season
            - 'cyclingflash-365-ranking': Rolling 365 days
            - 'road-victory-ranking': Victories in current year
            - 'team-ranking': Team current season
            - 'team-365-ranking': Team rolling 365 days
        gender : str
            Gender/age category: 'men-elite', 'women-elite', etc.
        
        Returns
        -------
        pd.DataFrame
            Ranking table with position, rider/team, points
        
        Examples
        --------
        >>> gc_ranking = Ranking.get('gc', 'cyclingflash-ranking', 'men-elite')
        """
        html = cf.get_ranking(ranking_type, category, gender)
        return parse_ranking(html)
    
    @classmethod
    def overall(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """
        Get overall ranking.
        
        Parameters
        ----------
        gender : str
            Gender category
        rolling : bool
            If True, use 365-day rolling ranking
        
        Returns
        -------
        pd.DataFrame
            Overall ranking
        """
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('overall', category, gender)
    
    @classmethod
    def gc(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get GC (general classification) specialist ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('gc', category, gender)
    
    @classmethod
    def hill(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get hilly terrain specialist ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('hill', category, gender)
    
    @classmethod
    def mountain(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get mountain specialist ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('mountain', category, gender)
    
    @classmethod
    def timetrial(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get time trial specialist ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('timetrial', category, gender)
    
    @classmethod
    def sprint(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get sprint specialist ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('sprint', category, gender)
    
    @classmethod
    def cyclocross(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get cyclocross ranking."""
        category = 'cyclingflash-365-ranking' if rolling else 'cyclingflash-ranking'
        return cls.get('cyclocross', category, gender)
    
    @classmethod
    def victories(cls, gender: str = 'men-elite', year: int = 2026) -> pd.DataFrame:
        """
        Get victory ranking for a specific year.
        
        Parameters
        ----------
        gender : str
            Gender category
        year : int
            Year for victory count
        
        Returns
        -------
        pd.DataFrame
            Victory ranking
        """
        html = cf.get_ranking(f"{year}", 'road-victory-ranking', gender)
        return parse_ranking(html)
    
    @classmethod
    def team_overall(cls, gender: str = 'men-elite', rolling: bool = False) -> pd.DataFrame:
        """Get team overall ranking."""
        category = 'team-365-ranking' if rolling else 'team-ranking'
        return cls.get('overall', category, gender)
