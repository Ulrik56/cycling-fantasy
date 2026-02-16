"""
Team
====

Access team details including roster and results.

Examples
--------
>>> team = Team('uae-emirates-xrg-2026')
>>> team.roster()
['Tadej Pogačar', 'Adam Yates', ...]
"""

try:
    from .api import cf
    from .parser import parse_team
except ImportError:
    from api import cf
    from parser import parse_team

import pandas as pd
from typing import Dict, Any, List


class Team:
    """
    Wrapper to access team information from CyclingFlash.
    
    Parameters
    ----------
    slug : str
        The team URL slug (e.g., 'uae-emirates-xrg-2026')
    
    Examples
    --------
    >>> uae = Team('uae-emirates-xrg-2026')
    >>> uae.name
    'UAE Emirates XRG'
    >>> uae.roster()
    """
    
    def __init__(self, slug: str):
        self.slug = slug
        self._info_cache = None
    
    def __repr__(self):
        return f"Team('{self.slug}')"
    
    def info(self) -> Dict[str, Any]:
        """
        Get team information.
        
        Returns
        -------
        dict
            Team details including name and rider roster
        """
        if self._info_cache is None:
            html = cf.get_team(self.slug)
            self._info_cache = parse_team(html)
        return self._info_cache
    
    def roster(self) -> pd.DataFrame:
        """
        Get team roster.
        
        Returns
        -------
        pd.DataFrame
            Team riders with name and slug
        """
        info = self.info()
        riders = info.get('riders', [])
        return pd.DataFrame(riders)
    
    def rider_names(self) -> List[str]:
        """
        Get list of rider names on the team.
        
        Returns
        -------
        list
            List of rider names
        """
        roster = self.roster()
        if roster.empty:
            return []
        return roster['name'].tolist()
    
    @property
    def name(self) -> str:
        """Get team name."""
        return self.info().get('name', self.slug)
    
    @property
    def year(self) -> int:
        """Extract year from team slug."""
        parts = self.slug.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])
        return 0
