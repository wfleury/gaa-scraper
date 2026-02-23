"""
Scan a range of competition IDs to find Ballincollig fixtures
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompetitionRangeScanner:
    def __init__(self):
        self.base_url = "https://gaacork.ie"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False  # Disable SSL verification
        
    def scan_competition(self, comp_id):
        """Scan a single competition by ID"""
        competition_url = f"https://gaacork.ie/league/{comp_id}/"
        
        try:
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
            
            return ballincollig_fixtures
            
        except Exception as e:
            return []
    
    def scan_range(self, start_id, end_id):
        """Scan a range of competition IDs"""
        print(f"=== Scanning Competition IDs {start_id} to {end_id} ===")
        print()
        
        all_fixtures = []
        competitions_with_fixtures = []
        
        for comp_id in range(start_id, end_id + 1):
            print(f"Scanning ID {comp_id}... ", end="")
            
            fixtures = self.scan_competition(comp_id)
            
            if fixtures:
                print(f"FOUND {len(fixtures)} fixtures!")
                all_fixtures.extend(fixtures)
                competitions_with_fixtures.append(comp_id)
                
                for fixture in fixtures:
                    print(f"  {fixture['date']}: {fixture['home']} vs {fixture['away']} ({fixture['competition']})")
            else:
                print("no fixtures")
            
            # Be respectful to the server
            time.sleep(0.3)
        
        print()
        print("=== SUMMARY ===")
        print(f"Competitions with Ballincollig fixtures: {len(competitions_with_fixtures)}")
        print(f"Total Ballincollig fixtures found: {len(all_fixtures)}")
        print()
        
        if competitions_with_fixtures:
            print("Competition IDs with Ballincollig fixtures:")
            for comp_id in competitions_with_fixtures:
                print(f"  {comp_id}")
        
        return all_fixtures, competitions_with_fixtures

if __name__ == "__main__":
    scanner = CompetitionRangeScanner()
    
    # Scan around the known competition IDs and look for newer ones
    # Known IDs: 211611, 211620, 211648, 211656, 211662, 211714
    print("Scanning around known competition IDs and looking for new ones...")
    
    # Scan a wider range to find newer competitions
    fixtures, competitions = scanner.scan_range(211600, 212000)
