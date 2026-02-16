"""
Parser
======

Provides useful functions to parse CyclingFlash HTML responses.
"""

import re
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup
import pandas as pd


def parse_rider_profile(html: bytes) -> Dict[str, Any]:
    """
    Parse rider profile page.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from rider profile page
    
    Returns
    -------
    dict
        Rider information including name, nationality, birth date, etc.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    profile = {}
    
    # Name from h1
    h1 = soup.find('h1')
    if h1:
        profile['name'] = h1.get_text(strip=True).replace('flag', '').strip()
    
    # Info table
    info_table = soup.find('table')
    if info_table:
        for row in info_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].get_text(strip=True).lower().replace(' ', '_')
                value = cells[1].get_text(strip=True).replace('flag', '').strip()
                profile[key] = value
    
    # Social links
    social_links = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'facebook.com' in href:
            social_links['facebook'] = href
        elif 'instagram.com' in href:
            social_links['instagram'] = href
        elif 'x.com' in href or 'twitter.com' in href:
            social_links['twitter'] = href
    if social_links:
        profile['social'] = social_links
    
    return profile


def parse_rider_results(html: bytes) -> pd.DataFrame:
    """
    Parse rider results page into a DataFrame.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from rider results page
    
    Returns
    -------
    pd.DataFrame
        Table of rider results
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    results = []
    
    # Find result rows in tables
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 3:
                result = {}
                
                # Extract date
                date_cell = cells[0] if cells else None
                if date_cell:
                    result['date'] = date_cell.get_text(strip=True)
                
                # Extract rank
                if len(cells) > 1:
                    result['rank'] = cells[1].get_text(strip=True)
                
                # Extract GC position if available
                if len(cells) > 2:
                    result['gc'] = cells[2].get_text(strip=True)
                
                # Extract race name and link
                for cell in cells:
                    link = cell.find('a', href=re.compile(r'/race/'))
                    if link:
                        result['race'] = link.get_text(strip=True)
                        result['race_slug'] = link['href'].replace('/race/', '').split('/')[0]
                        break
                
                # Extract distance
                if len(cells) > 4:
                    dist_text = cells[-1].get_text(strip=True)
                    if 'km' in dist_text.lower():
                        result['distance'] = dist_text
                
                if result.get('race'):
                    results.append(result)
    
    return pd.DataFrame(results)


def parse_race_result(html: bytes) -> pd.DataFrame:
    """
    Parse race result page into a DataFrame.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from race result page
    
    Returns
    -------
    pd.DataFrame
        Table of race results with position, rider, team, time
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    results = []
    
    # Find result tables
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                result = {}
                
                # Position
                result['position'] = cells[0].get_text(strip=True)
                
                # Rider info
                rider_cell = cells[1]
                rider_link = rider_cell.find('a', href=re.compile(r'/profile/'))
                if rider_link:
                    result['rider'] = rider_link.get_text(strip=True).replace('flag', '').strip()
                    result['rider_slug'] = rider_link['href'].replace('/profile/', '')
                
                # Team info
                team_cell = cells[2] if len(cells) > 2 else None
                if team_cell:
                    team_link = team_cell.find('a', href=re.compile(r'/team/'))
                    if team_link:
                        result['team'] = team_link.get_text(strip=True).replace('flag', '').strip()
                        result['team_slug'] = team_link['href'].replace('/team/', '')
                
                # Time
                if len(cells) > 3:
                    result['time'] = cells[3].get_text(strip=True)
                
                if result.get('rider'):
                    results.append(result)
    
    return pd.DataFrame(results)


def parse_ranking(html: bytes) -> pd.DataFrame:
    """
    Parse ranking page into a DataFrame.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from ranking page
    
    Returns
    -------
    pd.DataFrame
        Ranking table with position, rider/team, points
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    rankings = []
    
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                entry = {}
                
                # Position
                entry['position'] = cells[0].get_text(strip=True)
                
                # Rider
                rider_link = row.find('a', href=re.compile(r'/profile/'))
                if rider_link:
                    entry['rider'] = rider_link.get_text(strip=True).replace('flag', '').strip()
                    entry['rider_slug'] = rider_link['href'].replace('/profile/', '')
                
                # Team
                team_link = row.find('a', href=re.compile(r'/team/'))
                if team_link:
                    entry['team'] = team_link.get_text(strip=True).replace('flag', '').strip()
                    entry['team_slug'] = team_link['href'].replace('/team/', '')
                
                # Points (usually last cell with numeric value)
                if len(cells) > 2:
                    points_text = cells[-1].get_text(strip=True)
                    if points_text.isdigit():
                        entry['points'] = int(points_text)
                
                if entry.get('rider') or entry.get('team'):
                    rankings.append(entry)
    
    return pd.DataFrame(rankings)


def parse_team(html: bytes) -> Dict[str, Any]:
    """
    Parse team profile page.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from team page
    
    Returns
    -------
    dict
        Team information including name, roster, etc.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    team = {}
    
    # Name from h1
    h1 = soup.find('h1')
    if h1:
        team['name'] = h1.get_text(strip=True).replace('flag', '').strip()
    
    # Roster
    riders = []
    for link in soup.find_all('a', href=re.compile(r'/profile/')):
        rider_name = link.get_text(strip=True).replace('flag', '').strip()
        rider_slug = link['href'].replace('/profile/', '')
        if rider_name and rider_slug and '/profile/' not in rider_slug:
            riders.append({
                'name': rider_name,
                'slug': rider_slug
            })
    
    # Deduplicate
    seen = set()
    unique_riders = []
    for r in riders:
        if r['slug'] not in seen:
            seen.add(r['slug'])
            unique_riders.append(r)
    
    team['riders'] = unique_riders
    
    return team


def parse_calendar(html: bytes) -> pd.DataFrame:
    """
    Parse race calendar page into a DataFrame.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from calendar page
    
    Returns
    -------
    pd.DataFrame
        Calendar with dates, race names, categories
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    races = []
    
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                race = {}
                
                # Date
                race['date'] = cells[0].get_text(strip=True)
                
                # Race link
                race_link = row.find('a', href=re.compile(r'/race/'))
                if race_link:
                    race['name'] = race_link.get_text(strip=True).replace('flag', '').strip()
                    race['slug'] = race_link['href'].replace('/race/', '').split('/')[0]
                
                # Category
                if len(cells) > 2:
                    race['category'] = cells[2].get_text(strip=True)
                
                if race.get('name'):
                    races.append(race)
    
    return pd.DataFrame(races)


def parse_latest_results(html: bytes) -> List[Dict[str, Any]]:
    """
    Parse latest results page.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from latest results page
    
    Returns
    -------
    list
        List of recent race results with winner info
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    results = []
    
    # Each result block
    for table in soup.find_all('table'):
        race_info = {}
        
        # Find race link before table
        prev = table.find_previous(['a', 'h2', 'h3'])
        if prev and prev.name == 'a' and '/race/' in prev.get('href', ''):
            race_info['race'] = prev.get_text(strip=True).replace('flag', '').strip()
            race_info['race_slug'] = prev['href'].replace('/race/', '').split('/')[0]
        
        # Top 3
        podium = []
        for row in table.find_all('tr')[:3]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                rider_link = row.find('a', href=re.compile(r'/profile/'))
                if rider_link:
                    podium.append({
                        'position': cells[0].get_text(strip=True),
                        'rider': rider_link.get_text(strip=True).replace('flag', '').strip(),
                        'rider_slug': rider_link['href'].replace('/profile/', '')
                    })
        
        if podium:
            race_info['podium'] = podium
            results.append(race_info)
    
    return results


def parse_transfers(html: bytes) -> List[Dict[str, str]]:
    """
    Parse transfer news page.
    
    Parameters
    ----------
    html : bytes
        Raw HTML content from transfers page
    
    Returns
    -------
    list
        List of transfers with rider, old team, new team
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    transfers = []
    
    # Each transfer card typically has rider link, from team, to team
    for card in soup.find_all(['div', 'article', 'li']):
        rider_link = card.find('a', href=re.compile(r'/profile/'))
        team_links = card.find_all('a', href=re.compile(r'/team/'))
        
        if rider_link and len(team_links) >= 2:
            transfer = {
                'rider': rider_link.get_text(strip=True).replace('flag', '').strip(),
                'rider_slug': rider_link['href'].replace('/profile/', ''),
                'from_team': team_links[0].get_text(strip=True).replace('flag', '').strip(),
                'from_team_slug': team_links[0]['href'].replace('/team/', ''),
                'to_team': team_links[1].get_text(strip=True).replace('flag', '').strip(),
                'to_team_slug': team_links[1]['href'].replace('/team/', ''),
            }
            transfers.append(transfer)
    
    return transfers


def extract_rider_slug(url_or_name: str) -> str:
    """
    Convert rider name or URL to slug format.
    
    Parameters
    ----------
    url_or_name : str
        Full URL, partial path, or rider name
    
    Returns
    -------
    str
        URL slug (e.g., 'tadej-pogacar')
    """
    # If it's a URL, extract the slug
    if '/profile/' in url_or_name:
        return url_or_name.split('/profile/')[-1].split('/')[0]
    
    # Convert name to slug
    slug = url_or_name.lower()
    
    # Extended character replacements
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'ą': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ę': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'ÿ': 'y',
        'ñ': 'n', 'ń': 'n',
        'ç': 'c', 'ć': 'c', 'č': 'c',
        'š': 's', 'ś': 's',
        'ž': 'z', 'ź': 'z', 'ż': 'z',
        'ł': 'l',
        'đ': 'd',
        'ß': 'ss',
        'æ': 'ae', 'œ': 'oe',
    }
    
    for char, replacement in replacements.items():
        slug = slug.replace(char, replacement)
    
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')
