"""
JavaScript-enabled scraper to get dynamically loaded fixtures
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class JavaScriptScraper:
    def __init__(self):
        self.base_url = "https://gaacork.ie"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.session.verify = False
        
    def extract_json_from_scripts(self, soup):
        """Extract JSON data from JavaScript scripts"""
        
        # Look for script tags that might contain fixture data
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                script_content = script.string
                
                # Look for JSON patterns that might contain fixtures
                json_patterns = [
                    r'var\s+fixtures\s*=\s*(\[.*?\]);',
                    r'window\.fixtures\s*=\s*(\[.*?\]);',
                    r'data\s*:\s*(\[.*?\])',
                    r'"fixtures"\s*:\s*(\[.*?\])',
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            # Try to parse as JSON
                            fixtures_data = json.loads(match)
                            print(f"Found JSON data with {len(fixtures_data)} items")
                            return fixtures_data
                        except json.JSONDecodeError:
                            # Try to clean up the JSON
                            try:
                                # Remove trailing semicolons and clean up
                                cleaned = match.rstrip(';').strip()
                                fixtures_data = json.loads(cleaned)
                                print(f"Found cleaned JSON data with {len(fixtures_data)} items")
                                return fixtures_data
                            except:
                                continue
        
        return None
    
    def look_for_ajax_endpoints(self, soup):
        """Look for AJAX endpoints that might load fixtures"""
        
        scripts = soup.find_all('script')
        
        ajax_patterns = [
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'\.get\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'ajax\s*\(\s*{\s*url\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'load\s*\(\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        endpoints = []
        
        for script in scripts:
            if script.string:
                script_content = script.string
                
                for pattern in ajax_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if 'fixture' in match.lower() or 'league' in match.lower():
                            endpoints.append(match)
        
        return list(set(endpoints))
    
    def try_ajax_endpoints(self, endpoints):
        """Try to fetch data from AJAX endpoints"""
        
        for endpoint in endpoints:
            try:
                if endpoint.startswith('/'):
                    url = f"https://gaacork.ie{endpoint}"
                else:
                    url = endpoint
                
                print(f"Trying endpoint: {url}")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"Got JSON response from {endpoint}")
                    return data
                except:
                    # Look for JSON in the response text
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                            print(f"Found JSON in response from {endpoint}")
                            return data
                        except:
                            pass
                
            except Exception as e:
                print(f"Failed to fetch {endpoint}: {e}")
                continue
        
        return None
    
    def scrape_club_profile(self, club_id, team_id):
        """Scrape club profile with JavaScript analysis"""
        
        url = f"https://gaacork.ie/clubprofile/{club_id}/?team_id={team_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("=== JavaScript Scraper Analysis ===")
            print(f"URL: {url}")
            print()
            
            # Method 1: Look for JSON data in scripts
            print("1. Looking for JSON data in scripts...")
            json_data = self.extract_json_from_scripts(soup)
            
            if json_data:
                print(f"Found JSON data: {json_data}")
                return self.process_json_fixtures(json_data)
            
            # Method 2: Look for AJAX endpoints
            print("2. Looking for AJAX endpoints...")
            endpoints = self.look_for_ajax_endpoints(soup)
            
            if endpoints:
                print(f"Found potential endpoints: {endpoints}")
                ajax_data = self.try_ajax_endpoints(endpoints)
                
                if ajax_data:
                    return self.process_json_fixtures(ajax_data)
            
            # Method 3: Look for data attributes in HTML (might be populated by JS)
            print("3. Looking for data attributes...")
            fixture_elements = soup.find_all('ul', attrs={'data-date': True})
            
            if fixture_elements:
                print(f"Found {len(fixture_elements)} elements with data-date")
                return self.process_html_fixtures(fixture_elements)
            
            print("No fixture data found")
            return []
            
        except Exception as e:
            print(f"Error scraping club profile: {e}")
            return []
    
    def process_json_fixtures(self, data):
        """Process JSON fixture data"""
        
        fixtures = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Look for Ballincollig in the fixture
                    home_team = item.get('home_team', item.get('hometeam', item.get('home', '')))
                    away_team = item.get('away_team', item.get('awayteam', item.get('away', '')))
                    
                    if 'Ballincollig' in home_team or 'Ballincollig' in away_team:
                        fixtures.append({
                            'home': home_team,
                            'away': away_team,
                            'date': item.get('date', item.get('fixture_date', '')),
                            'time': item.get('time', item.get('fixture_time', '')),
                            'venue': item.get('venue', item.get('location', '')),
                            'competition': item.get('competition', item.get('comp_name', ''))
                        })
        
        print(f"Processed {len(fixtures)} Ballincollig fixtures from JSON")
        return fixtures
    
    def process_html_fixtures(self, elements):
        """Process HTML fixture elements"""
        
        fixtures = []
        
        for element in elements:
            home_team = element.get('data-hometeam', '')
            away_team = element.get('data-awayteam', '')
            
            if 'Ballincollig' in home_team or 'Ballincollig' in away_team:
                fixtures.append({
                    'home': home_team,
                    'away': away_team,
                    'date': element.get('data-date', ''),
                    'time': element.get('data-time', ''),
                    'venue': element.get('data-venue', ''),
                    'competition': element.get('data-compname', '')
                })
        
        print(f"Processed {len(fixtures)} Ballincollig fixtures from HTML")
        return fixtures

if __name__ == "__main__":
    scraper = JavaScriptScraper()
    fixtures = scraper.scrape_club_profile(1986, 327535)
    
    print("\n=== Fixtures Found ===")
    for fixture in fixtures:
        print(f"{fixture['date']}: {fixture['home']} vs {fixture['away']} ({fixture['competition']})")
