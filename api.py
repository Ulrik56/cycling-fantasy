"""
CyclingFlash API
================

Provides tools to access CyclingFlash data via web scraping.
"""

import requests
from urllib.parse import urljoin

class CyclingFlashAPI:
    """Wrapper for CyclingFlash website scraping"""
    
    BASE_URL = "https://cyclingflash.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def _get(self, path: str) -> bytes:
        """Make a GET request to cyclingflash.com"""
        url = urljoin(self.BASE_URL, path)
        response = self.session.get(url)
        response.raise_for_status()
        return response.content
    
    def get_rider(self, slug: str) -> bytes:
        """
        Get rider profile page.
        
        Parameters
        ----------
        slug : str
            The rider's URL slug (e.g., 'tadej-pogacar')
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        return self._get(f"/profile/{slug}")
    
    def get_rider_results(self, slug: str, year: int = None) -> bytes:
        """Get rider results page for a specific year."""
        if year:
            return self._get(f"/profile/{slug}/results/{year}")
        return self._get(f"/profile/{slug}/results")
    
    def get_rider_wins(self, slug: str) -> bytes:
        """Get rider victories page."""
        return self._get(f"/profile/{slug}/wins")
    
    def get_rider_stats(self, slug: str) -> bytes:
        """Get rider statistics page."""
        return self._get(f"/profile/{slug}/stats")
    
    def get_rider_teams(self, slug: str) -> bytes:
        """Get rider team history page."""
        return self._get(f"/profile/{slug}/teams")
    
    def get_team(self, slug: str) -> bytes:
        """
        Get team profile page.
        
        Parameters
        ----------
        slug : str
            The team's URL slug (e.g., 'uae-emirates-xrg-2026')
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        return self._get(f"/team/{slug}")
    
    def get_race(self, slug: str) -> bytes:
        """
        Get race page.
        
        Parameters
        ----------
        slug : str
            The race URL slug (e.g., 'tour-de-france-2026')
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        return self._get(f"/race/{slug}")
    
    def get_race_result(self, slug: str, stage: str = None, classification: str = None) -> bytes:
        """
        Get race results.
        
        Parameters
        ----------
        slug : str
            The race URL slug
        stage : str, optional
            Stage identifier (e.g., 'stage-1')
        classification : str, optional
            Classification type (e.g., 'SIC' for stage, 'GC' for general)
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        if stage and classification:
            return self._get(f"/race/{slug}/result/{stage}/{classification}")
        return self._get(f"/race/{slug}/result")
    
    def get_race_startlist(self, slug: str) -> bytes:
        """Get race startlist."""
        return self._get(f"/race/{slug}/startlist")
    
    def get_ranking(self, ranking_type: str, category: str, gender: str = 'men-elite') -> bytes:
        """
        Get ranking page.
        
        Parameters
        ----------
        ranking_type : str
            Type of ranking: 'overall', 'gc', 'hill', 'mountain', 'timetrial', 'sprint', 'cyclocross'
        category : str
            Category prefix: 'cyclingflash-ranking', 'cyclingflash-365-ranking', 
            'road-victory-ranking', 'team-ranking', 'team-365-ranking'
        gender : str
            Gender category: 'men-elite', 'women-elite', etc.
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        return self._get(f"/{category}/{ranking_type}/{gender}")
    
    def get_calendar(self, discipline: str, year: int, category: str = 'Men Elite') -> bytes:
        """
        Get race calendar.
        
        Parameters
        ----------
        discipline : str
            Discipline: 'road', 'cyclocross', 'mountainbike', 'gravel', 'track'
        year : int
            Calendar year
        category : str
            Race category
        
        Returns
        -------
        bytes
            Raw HTML content
        """
        return self._get(f"/calendar/{discipline}/{year}/{category}")
    
    def get_latest_results(self) -> bytes:
        """Get latest race results."""
        return self._get("/latest-results")
    
    def get_transfers(self) -> bytes:
        """Get transfer news."""
        return self._get("/transfers")
    
    def get_tv_guide(self) -> bytes:
        """Get TV broadcast guide."""
        return self._get("/tv-guide")


# Global instance for convenience
cf = CyclingFlashAPI()
