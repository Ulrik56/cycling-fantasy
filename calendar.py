"""
Calendar & Results
==================

Access race calendars and latest results.

Examples
--------
>>> from cyclingflash_api import Calendar, LatestResults

>>> # Get 2026 World Tour calendar
>>> calendar = Calendar.road(2026, 'UCI World Tour')

>>> # Get latest results
>>> results = LatestResults.get()
"""

try:
    from .api import cf
    from .parser import parse_calendar, parse_latest_results, parse_transfers
except ImportError:
    from api import cf
    from parser import parse_calendar, parse_latest_results, parse_transfers

import pandas as pd
from typing import List, Dict, Any


class Calendar:
    """
    Access race calendars from CyclingFlash.
    
    Examples
    --------
    >>> # Men Elite road calendar
    >>> df = Calendar.road(2026)
    
    >>> # Women cyclocross calendar  
    >>> df = Calendar.cyclocross('2025-2026', 'Women Elite')
    """
    
    @classmethod
    def road(cls, year: int, category: str = 'Men Elite') -> pd.DataFrame:
        """
        Get road cycling calendar.
        
        Parameters
        ----------
        year : int
            Calendar year
        category : str
            Race category: 'Men Elite', 'Women Elite', 
            'UCI World Tour', 'UCI ProSeries', "UCI Women's World Tour"
        
        Returns
        -------
        pd.DataFrame
            Calendar with race dates and names
        """
        html = cf.get_calendar('road', year, category)
        return parse_calendar(html)
    
    @classmethod
    def cyclocross(cls, season: str, category: str = 'Men Elite') -> pd.DataFrame:
        """
        Get cyclocross calendar.
        
        Parameters
        ----------
        season : str
            Season (e.g., '2025-2026')
        category : str
            Race category
        
        Returns
        -------
        pd.DataFrame
            Cyclocross calendar
        """
        html = cf.get_calendar('cyclocross', season, category)
        return parse_calendar(html)
    
    @classmethod
    def mountainbike(cls, year: int) -> pd.DataFrame:
        """Get mountain bike calendar."""
        html = cf.get_calendar('mountainbike', year, '')
        return parse_calendar(html)
    
    @classmethod
    def gravel(cls, year: int) -> pd.DataFrame:
        """Get gravel calendar."""
        html = cf.get_calendar('gravel', year, '')
        return parse_calendar(html)
    
    @classmethod
    def track(cls, year: int) -> pd.DataFrame:
        """Get track cycling calendar."""
        html = cf.get_calendar('track', year, '')
        return parse_calendar(html)


class LatestResults:
    """
    Access latest race results.
    
    Examples
    --------
    >>> results = LatestResults.get()
    >>> for r in results[:5]:
    ...     print(f"{r['race']}: {r['podium'][0]['rider']}")
    """
    
    @classmethod
    def get(cls) -> List[Dict[str, Any]]:
        """
        Get latest race results.
        
        Returns
        -------
        list
            List of recent results with race info and podium
        """
        html = cf.get_latest_results()
        return parse_latest_results(html)
    
    @classmethod
    def as_dataframe(cls) -> pd.DataFrame:
        """
        Get latest results as a DataFrame.
        
        Returns
        -------
        pd.DataFrame
            Latest results with winner info
        """
        results = cls.get()
        rows = []
        for r in results:
            if r.get('podium'):
                rows.append({
                    'race': r.get('race', ''),
                    'race_slug': r.get('race_slug', ''),
                    'winner': r['podium'][0]['rider'],
                    'winner_slug': r['podium'][0]['rider_slug'],
                    'second': r['podium'][1]['rider'] if len(r['podium']) > 1 else '',
                    'third': r['podium'][2]['rider'] if len(r['podium']) > 2 else ''
                })
        return pd.DataFrame(rows)


class Transfers:
    """
    Access transfer news.
    
    Examples
    --------
    >>> transfers = Transfers.get()
    >>> df = Transfers.as_dataframe()
    """
    
    @classmethod
    def get(cls) -> List[Dict[str, str]]:
        """
        Get latest transfers.
        
        Returns
        -------
        list
            List of transfers with rider and team info
        """
        html = cf.get_transfers()
        return parse_transfers(html)
    
    @classmethod
    def as_dataframe(cls) -> pd.DataFrame:
        """
        Get transfers as a DataFrame.
        
        Returns
        -------
        pd.DataFrame
            Transfer list
        """
        transfers = cls.get()
        return pd.DataFrame(transfers)
