"""
CyclingFlash API
================

An unofficial Python API wrapper for https://cyclingflash.com/.

This package provides easy access to cycling data including:
- Rider profiles and results
- Race results and startlists
- Rankings (overall, GC, sprint, mountain, etc.)
- Team rosters
- Calendar and latest results
- Transfer news
- Fantasy manager integration

Examples
--------
>>> from cyclingflash_api import Rider, Race, Ranking

# Get rider information
>>> pogacar = Rider('tadej-pogacar')
>>> pogacar.profile()
{'name': 'Tadej Pogačar', 'nationality': 'Slovenia', ...}

# Get race results
>>> tdf = Race('tour-de-france-2025')
>>> tdf.result().head()

# Get rankings
>>> overall = Ranking.overall('men-elite')
>>> gc = Ranking.gc('women-elite')

# Fantasy manager integration
>>> from cyclingflash_api import FantasyManager
>>> fm = FantasyManager()
>>> riders = fm.get_top_riders(50)
>>> team = fm.suggest_team(strategy='balanced')
"""

__version__ = '0.1.0'

from .rider import Rider
from .race import Race, RaceEdition
from .ranking import Ranking
from .team import Team
from .calendar import Calendar, LatestResults, Transfers
from .api import CyclingFlashAPI, cf
from .fantasy import FantasyManager

__all__ = [
    'Rider',
    'Race',
    'RaceEdition', 
    'Ranking',
    'Team',
    'Calendar',
    'LatestResults',
    'Transfers',
    'CyclingFlashAPI',
    'cf',
    'FantasyManager',
]
