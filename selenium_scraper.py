"""
Selenium-based scraper to execute JavaScript and get dynamically loaded fixtures
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time

class SeleniumScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            self.driver = None
    
    def scrape_club_profile(self, club_id, team_id):
        """Scrape club profile with JavaScript execution"""
        
        if not self.driver:
            print("No driver available")
            return []
        
        url = f"https://gaacork.ie/clubprofile/{club_id}/?team_id={team_id}"
        
        try:
            print(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for JavaScript to execute and load fixtures
            print("Waiting for JavaScript to load fixtures...")
            
            # Try multiple methods to find fixtures
            
            # Method 1: Wait for fixture elements to appear
            try:
                fixture_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul[data-date]'))
                )
                print(f"Found {len(fixture_elements)} fixture elements via CSS selector")
                return self.process_fixture_elements(fixture_elements)
            except TimeoutException:
                print("No fixture elements found with data-date attribute")
            
            # Method 2: Look for elements with 'fixtures' in class
            try:
                fixture_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul[class*="fixtures"]')
                if fixture_elements:
                    print(f"Found {len(fixture_elements)} fixture elements via class name")
                    return self.process_fixture_elements(fixture_elements)
            except:
                print("No fixture elements found with 'fixtures' in class")
            
            # Method 3: Look for any table-like structures
            try:
                fixture_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul.table-body')
                if fixture_elements:
                    print(f"Found {len(fixture_elements)} table-body elements")
                    return self.process_fixture_elements(fixture_elements)
            except:
                print("No table-body elements found")
            
            # Method 4: Execute JavaScript to find fixtures
            print("Executing JavaScript to find fixtures...")
            js_fixtures = self.execute_javascript_fixture_finder()
            if js_fixtures:
                return js_fixtures
            
            # Method 5: Check page source after JavaScript execution
            print("Checking page source after JavaScript execution...")
            page_source = self.driver.page_source
            
            # Look for Ballincollig in the page source
            if 'Ballincollig' in page_source:
                print("Found 'Ballincollig' in page source, attempting to extract...")
                return self.extract_from_page_source(page_source)
            
            print("No fixtures found after JavaScript execution")
            return []
            
        except Exception as e:
            print(f"Error scraping with Selenium: {e}")
            return []
    
    def process_fixture_elements(self, elements):
        """Process fixture elements found by Selenium"""
        
        fixtures = []
        
        for element in elements:
            try:
                # Get data attributes
                home_team = element.get_attribute('data-hometeam') or ''
                away_team = element.get_attribute('data-awayteam') or ''
                date = element.get_attribute('data-date') or ''
                time = element.get_attribute('data-time') or ''
                venue = element.get_attribute('data-venue') or ''
                competition = element.get_attribute('data-compname') or ''
                
                # Check if Ballincollig is involved
                if 'Ballincollig' in home_team or 'Ballincollig' in away_team:
                    # Filter out rugby and LGFA
                    exclude_indicators = ['rfc', 'rugby', 'rugbaí', 'munster bowl', 'boys clubs', 'lgfa', 'ladies']
                    comp_lower = competition.lower()
                    
                    if not any(indicator in comp_lower for indicator in exclude_indicators):
                        referee = element.get_attribute('data-referee') or ''
                        fixtures.append({
                            'home': home_team,
                            'away': away_team,
                            'date': date,
                            'time': time,
                            'venue': venue,
                            'competition': competition,
                            'referee': referee.strip()
                        })
                        
                        print(f"Found fixture: {date} - {home_team} vs {away_team} ({competition})")
                
            except Exception as e:
                print(f"Error processing element: {e}")
                continue
        
        print(f"Processed {len(fixtures)} Ballincollig fixtures")
        return fixtures
    
    def execute_javascript_fixture_finder(self):
        """Execute JavaScript to find fixtures"""
        
        js_code = """
        // Look for fixture data in various places
        var fixtures = [];
        
        // Check for elements with data attributes
        var elements = document.querySelectorAll('ul[data-date], ul[data-hometeam], ul[data-awayteam]');
        
        for (var i = 0; i < elements.length; i++) {
            var el = elements[i];
            var homeTeam = el.getAttribute('data-hometeam') || '';
            var awayTeam = el.getAttribute('data-awayteam') || '';
            
            if (homeTeam.indexOf('Ballincollig') !== -1 || awayTeam.indexOf('Ballincollig') !== -1) {
                fixtures.push({
                    home: homeTeam,
                    away: awayTeam,
                    date: el.getAttribute('data-date') || '',
                    time: el.getAttribute('data-time') || '',
                    venue: el.getAttribute('data-venue') || '',
                    competition: el.getAttribute('data-compname') || ''
                });
            }
        }
        
        return fixtures;
        """
        
        try:
            result = self.driver.execute_script(js_code)
            print(f"JavaScript found {len(result)} fixtures")
            return result
        except Exception as e:
            print(f"Error executing JavaScript: {e}")
            return []
    
    def extract_from_page_source(self, page_source):
        """Extract fixtures from page source using regex"""
        
        import re
        
        fixtures = []
        
        # Look for data attributes in the HTML
        pattern = r'data-hometeam="([^"]*Ballincollig[^"]*)"|data-awayteam="([^"]*Ballincollig[^"]*)"'
        matches = re.findall(pattern, page_source)
        
        for match in matches:
            home_team = match[0] if match[0] else ''
            away_team = match[1] if match[1] else ''
            
            # Try to extract the full fixture element
            if home_team or away_team:
                # Look for the surrounding ul element
                ul_pattern = fr'<ul[^>]*data-hometeam="({home_team or away_team})"[^>]*>.*?</ul>'
                ul_match = re.search(ul_pattern, page_source, re.DOTALL)
                
                if ul_match:
                    ul_html = ul_match.group()
                    
                    # Extract all data attributes
                    data_pattern = r'data-([^=]+)="([^"]*)"'
                    data_attrs = dict(re.findall(data_pattern, ul_html))
                    
                    fixtures.append({
                        'home': data_attrs.get('hometeam', ''),
                        'away': data_attrs.get('awayteam', ''),
                        'date': data_attrs.get('date', ''),
                        'time': data_attrs.get('time', ''),
                        'venue': data_attrs.get('venue', ''),
                        'competition': data_attrs.get('compname', '')
                    })
        
        print(f"Extracted {len(fixtures)} fixtures from page source")
        return fixtures
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = SeleniumScraper()
    
    if scraper.driver:
        try:
            fixtures = scraper.scrape_club_profile(1986, 327535)
            
            print("\n=== Fixtures Found ===")
            for fixture in fixtures:
                print(f"{fixture['date']}: {fixture['home']} vs {fixture['away']} ({fixture['competition']})")
            
            print(f"\nTotal fixtures: {len(fixtures)}")
            
        finally:
            scraper.close()
    else:
        print("Could not initialize Selenium driver")
        print("You may need to install ChromeDriver:")
        print("1. Download ChromeDriver: https://chromedriver.chromium.org/")
        print("2. Add it to your PATH or place it in the project directory")
