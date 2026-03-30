"""
Scan all GAA competitions to find Ballincollig fixtures
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompetitionScanner:
    def __init__(self):
        self.base_url = "https://gaacork.ie"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False  # Disable SSL verification
        
    def get_all_competition_links(self):
        """Get all competition links from the GAA website"""
        try:
            # Try the competitions listing page
            competitions_url = "https://gaacork.ie/competition-listing/"
            response = self.session.get(competitions_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            competition_links = []
            
            # Find all links that look like competitions
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/league/' in href or '/competition/' in href:
                    full_url = urljoin(self.base_url, href)
                    competition_links.append(full_url)
            
            # Remove duplicates
            competition_links = list(set(competition_links))
            print(f"Found {len(competition_links)} competition links")
            return competition_links
            
        except Exception as e:
            print(f"Error getting competition links: {e}")
            return []
    
    def scan_competition_for_ballincollig(self, competition_url):
        """Scan a single competition page for Ballincollig fixtures"""
        try:
            print(f"Scanning: {competition_url}")
            response = self.session.get(competition_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for fixture elements
            fixture_elements = soup.find_all('ul', class_=lambda x: x and 'fixtures' in str(x).lower())
            
            ballincollig_fixtures = []
            
            for fixture_ul in fixture_elements:
                data_hometeam = fixture_ul.get('data-hometeam', '')
                data_awayteam = fixture_ul.get('data-awayteam', '')
                data_date = fixture_ul.get('data-date', '')
                data_compname = fixture_ul.get('data-compname', '')
                
                # Check if Ballincollig is involved
                if "Ballincollig" in data_hometeam or "Ballincollig" in data_awayteam:
                    # Filter out rugby
                    rugby_indicators = ['rfc', 'rugby', 'rugbaí', 'munster bowl', 'boys clubs']
                    comp_lower = data_compname.lower()
                    
                    if not any(indicator in comp_lower for indicator in rugby_indicators):
                        ballincollig_fixtures.append({
                            'home': data_hometeam,
                            'away': data_awayteam,
                            'date': data_date,
                            'competition': data_compname,
                            'url': competition_url
                        })
            
            if ballincollig_fixtures:
                print(f"  Found {len(ballincollig_fixtures)} Ballincollig fixtures")
                for fixture in ballincollig_fixtures:
                    print(f"    {fixture['date']}: {fixture['home']} vs {fixture['away']} ({fixture['competition']})")
            
            return ballincollig_fixtures
            
        except Exception as e:
            print(f"Error scanning {competition_url}: {e}")
            return []
    
    def scan_all_competitions(self):
        """Scan all competitions for Ballincollig fixtures"""
        print("=== Scanning All GAA Competitions for Ballincollig ===")
        print()
        
        competition_links = self.get_all_competition_links()
        
        all_fixtures = []
        competitions_with_fixtures = []
        
        for i, competition_url in enumerate(competition_links, 1):
            print(f"[{i}/{len(competition_links)}] ", end="")
            fixtures = self.scan_competition_for_ballincollig(competition_url)
            
            if fixtures:
                all_fixtures.extend(fixtures)
                competitions_with_fixtures.append(competition_url)
            
            # Be respectful to the server
            time.sleep(0.5)
        
        print()
        print("=== SUMMARY ===")
        print(f"Total competitions scanned: {len(competition_links)}")
        print(f"Competitions with Ballincollig fixtures: {len(competitions_with_fixtures)}")
        print(f"Total Ballincollig fixtures found: {len(all_fixtures)}")
        print()
        
        if competitions_with_fixtures:
            print("Competitions with Ballincollig fixtures:")
            for comp_url in competitions_with_fixtures:
                print(f"  {comp_url}")
        
        print()
        print("All fixtures found:")
        for fixture in all_fixtures:
            print(f"  {fixture['date']}: {fixture['home']} vs {fixture['away']} ({fixture['competition']})")
        
        return all_fixtures, competitions_with_fixtures

if __name__ == "__main__":
    scanner = CompetitionScanner()
    fixtures, competitions = scanner.scan_all_competitions()
