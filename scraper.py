"""
GAA Club Profile Scraper
Extracts club information from gaacork.ie club profile pages
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import urllib3
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
from config import BASE_URL, REQUEST_DELAY, TIMEOUT, FIELDS_TO_EXTRACT

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GAAClubScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Disable SSL verification for this site
        self.session.verify = False
    
    def get_page_content(self, url):
        """
        Fetch page content with error handling
        
        Args:
            url (str): URL to fetch
            
        Returns:
            BeautifulSoup: Parsed HTML or None if failed
        """
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_fixtures_from_club_page(self, soup, club_id):
        """
        Extract fixtures directly from the club profile page
        This should capture all Ballincollig fixtures across all age grades
        """
        fixtures = []
        
        print(f"Looking for fixtures directly on club profile page...")
        
        # Look for fixture elements directly on the club profile page
        fixture_elements = soup.find_all('ul', class_=lambda x: x and 'fixtures' in str(x).lower())
        
        print(f"Found {len(fixture_elements)} fixture elements on club page")
        
        for element in fixture_elements:
            fixtures.extend(self.parse_fixture_element(element, club_id))
        
        # If no fixtures found on the main page, try the competition approach as fallback
        if not fixtures:
            print("No fixtures found on main page, trying competition links...")
            
            # Find all competition links on the page (both old and new formats)
            competition_links = soup.find_all('a', href=lambda x: x and ('league' in str(x) or 'competition' in str(x)))
            
            print(f"Found {len(competition_links)} competition links")
            
            # Try competitions to find Ballincollig fixtures
            for link in competition_links:
                competition_url = link.get('href', '')
                if competition_url.startswith('/'):
                    competition_url = f"https://gaacork.ie{competition_url}"
                
                print(f"Checking competition: {competition_url}")
                comp_fixtures = self.extract_fixtures_from_competition_page(competition_url, club_id)
                fixtures.extend(comp_fixtures)
        
        print(f"Total fixtures found: {len(fixtures)}")
        return fixtures
    
    def extract_fixtures_from_competition_page(self, competition_url, club_id):
        """
        Extract fixtures from a competition page
        """
        fixtures = []
        today = datetime.now()
        
        soup = self.get_page_content(competition_url)
        if not soup:
            return fixtures
        
        print(f"Looking for fixtures in competition page...")
        
        # Try different ways to find the fixture elements
        fixture_elements = soup.find_all('ul', class_='column-eight table-body fixtures')
        print(f"Found {len(fixture_elements)} fixture elements with exact class")
        
        if not fixture_elements:
            # Try with partial class matching
            fixture_elements = soup.find_all('ul', class_=lambda x: x and 'fixtures' in x.split())
            print(f"Found {len(fixture_elements)} fixture elements with 'fixtures' in class")
        
        if not fixture_elements:
            # Try finding any ul with data-date attribute
            fixture_elements = soup.find_all('ul', attrs={"data-date": True})
            print(f"Found {len(fixture_elements)} ul elements with data-date")
        
        if not fixture_elements:
            # Try any element with data-date
            fixture_elements = soup.find_all(attrs={"data-date": True})
            print(f"Found {len(fixture_elements)} total elements with data-date")
            # Print first few elements for debugging
            for i, elem in enumerate(fixture_elements[:3]):
                print(f"Element {i}: {elem.name}, classes: {elem.get('class', [])}")
        
        for element in fixture_elements:
            try:
                # Extract data attributes from the ul element
                data_date = element.get('data-date', '')
                data_time = element.get('data-time', '')
                data_hometeam = element.get('data-hometeam', '')
                data_awayteam = element.get('data-awayteam', '')
                data_referee = element.get('data-referee', '')
                data_venue = element.get('data-venue', '')
                data_compname = element.get('data-compname', '')
                
                print(f"Processing fixture: {data_hometeam} vs {data_awayteam} on {data_date}")
                
                # Filter: Only process fixtures where either team is "Ballincollig"
                if "Ballincollig" not in data_hometeam and "Ballincollig" not in data_awayteam:
                    print(f"Skipping - no Ballincollig team")
                    continue
                
                # Filter out rugby fixtures (look for rugby indicators)
                rugby_indicators = ['rfc', 'rugby', 'rugbaí', 'munster bowl', 'boys clubs']
                comp_lower = data_compname.lower()
                venue_lower = data_venue.lower()
                
                if any(indicator in comp_lower or indicator in venue_lower for indicator in rugby_indicators):
                    print(f"Skipping rugby fixture: {data_compname}")
                    continue
                
                # Parse and filter future dates
                try:
                    fixture_date = datetime.strptime(data_date, "%d %b %Y")
                    # Date filtering - only include future fixtures
                    if fixture_date.date() < today.date():
                        print(f"Skipping past date: {data_date}")
                        continue
                except ValueError:
                    print(f"Invalid date format: {data_date}")
                    continue
                
                # Process the fixture
                fixture_data = self.process_fixture_data(
                    data_date, data_time, data_hometeam, data_awayteam,
                    data_referee, data_venue, data_compname
                )
                
                if fixture_data:
                    fixtures.append(fixture_data)
                    print(f"Added fixture: {fixture_data}")
                    
            except Exception as e:
                print(f"Error processing fixture element: {e}")
                continue
        
        return fixtures
    
    def extract_from_data_attributes(self, fixture_elements, today):
        """Extract fixtures from HTML data attributes"""
        fixtures = []
        
        for element in fixture_elements:
            try:
                # Extract data attributes
                data_date = element.get('data-date', '')
                data_time = element.get('data-time', '')
                data_hometeam = element.get('data-hometeam', '')
                data_awayteam = element.get('data-awayteam', '')
                data_referee = element.get('data-referee', '')
                data_venue = element.get('data-venue', '')
                data_compname = element.get('data-compname', '')
                
                print(f"Processing fixture: {data_hometeam} vs {data_awayteam} on {data_date}")
                
                # Filter: Only process fixtures where either team is "Ballincollig"
                if "Ballincollig" not in data_hometeam and "Ballincollig" not in data_awayteam:
                    print(f"Skipping - no Ballincollig team")
                    continue
                
                # Filter out rugby fixtures (look for rugby indicators)
                rugby_indicators = ['rfc', 'rugby', 'rugbaí', 'munster bowl', 'boys clubs']
                comp_lower = data_compname.lower()
                venue_lower = data_venue.lower()
                
                if any(indicator in comp_lower or indicator in venue_lower for indicator in rugby_indicators):
                    print(f"Skipping rugby fixture: {data_compname}")
                    continue
                
                # Parse and filter future dates
                try:
                    fixture_date = datetime.strptime(data_date, "%d %b %Y")
                    # Date filtering - only include future fixtures
                    if fixture_date.date() < today.date():
                        print(f"Skipping past date: {data_date}")
                        continue
                except ValueError:
                    print(f"Invalid date format: {data_date}")
                    continue
                
                # Process the fixture
                fixture_data = self.process_fixture_data(
                    data_date, data_time, data_hometeam, data_awayteam,
                    data_referee, data_venue, data_compname
                )
                
                if fixture_data:
                    fixtures.append(fixture_data)
                    print(f"Added fixture: {fixture_data}")
                    
            except Exception as e:
                print(f"Error processing fixture element: {e}")
                continue
        
        return fixtures
    
    def extract_from_text_patterns(self, soup, club_id, today):
        """Extract fixtures from text patterns on the page"""
        fixtures = []
        
        # Look for date patterns like "Saturday 28th February"
        date_pattern = re.compile(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)', re.IGNORECASE)
        
        for element in soup.find_all(['div', 'p', 'li', 'tr', 'span']):
            text = element.get_text().strip()
            
            # Skip navigation elements
            if any(skip_word in text.lower() for skip_word in ['back', 'results', 'table', 'teams', 'form', 'group', 'team', 'p', 'w', 'd', 'l', 'pf', 'pa', 'pd', 'pts']):
                continue
            
            # Look for date patterns
            date_match = date_pattern.search(text)
            if date_match:
                print(f"Found date pattern in text: {text[:100]}...")
                
                # Try to extract fixture information from this text
                fixture_data = self.parse_text_fixture(element, club_id, today)
                if fixture_data:
                    fixtures.append(fixture_data)
        
        return fixtures
    
    def extract_from_tables(self, soup, club_id, today):
        """Extract fixtures from table structures"""
        fixtures = []
        
        # Look for tables that might contain fixture information
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # At least date, teams, time/venue
                    text = ' '.join([cell.get_text().strip() for cell in cells])
                    
                    # Check if Ballincollig is mentioned
                    if "Ballincollig" in text:
                        print(f"Found Ballincollig in table row: {text[:100]}...")
                        fixture_data = self.parse_table_fixture(cells, club_id, today)
                        if fixture_data:
                            fixtures.append(fixture_data)
        
        return fixtures
    
    def parse_text_fixture(self, element, club_id, today):
        """Parse fixture from text element"""
        text = element.get_text().strip()
        
        # This is a simplified version - you'd need to enhance this based on actual text patterns
        # For now, create a placeholder fixture
        
        # Extract date
        date_pattern = re.compile(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)', re.IGNORECASE)
        date_match = date_pattern.search(text)
        
        if not date_match:
            return None
        
        try:
            day_name, day_num, month_name = date_match.groups()
            fixture_date = datetime.strptime(f"{day_num} {month_name} {today.year}", "%d %B %Y")
            
            if fixture_date.date() < today.date():
                return None
            
            formatted_date = fixture_date.strftime("%d/%m/%Y")
        except ValueError:
            return None
        
        # Create a basic fixture (you'd enhance this with actual parsing)
        return {
            'Date': formatted_date,
            'Time': '00:00',
            'Venue': 'Unknown',
            'Ground': 'Unknown',
            'Referee': 'TBC',
            'Team': 'Unknown',
            'Competition Name': 'Unknown Competition',
            'Your Club Name': 'Ballincollig',
            'Opponent': 'Unknown',
            'Event Type': 'League'
        }
    
    def parse_table_fixture(self, cells, club_id, today):
        """Parse fixture from table cells"""
        # Similar to text fixture parsing but for table structure
        # This would need enhancement based on actual table structure
        return None
    
    def process_fixture_data(self, data_date, data_time, data_hometeam, data_awayteam, data_referee, data_venue, data_compname):
        """
        Process fixture data according to the specified rules
        
        Args:
            data_date, data_time, data_hometeam, data_awayteam, data_referee, data_venue, data_compname: Raw data attributes
            
        Returns:
            dict: Processed fixture data
        """
        try:
            # Date: Convert from "DD Mon YYYY" to "DD/MM/YYYY"
            fixture_date = datetime.strptime(data_date, "%d %b %Y")
            formatted_date = fixture_date.strftime("%d/%m/%Y")
            
            # Time: Prepend "0" if 4-character format
            formatted_time = data_time
            if len(data_time) == 4 and ':' in data_time:
                formatted_time = "0" + data_time
            
            # Your Club Name
            your_club_name = "Ballincollig"
            
            # Team mapping based on competition name
            team = self.map_team_name(data_compname)
            
            # Opponent: The team that is not "Ballincollig"
            if data_hometeam == "Ballincollig":
                opponent = data_awayteam
            elif data_awayteam == "Ballincollig":
                opponent = data_hometeam
            else:
                opponent = "Unknown"
            
            # Ground determination
            if data_hometeam == "Ballincollig" and data_venue == "Ballincollig":
                ground = "Home"
            elif data_awayteam == "Ballincollig":
                ground = "Away"
            else:
                ground = "Neutral"
            
            # Referee
            referee = data_referee
            
            # Competition Name
            competition_name = data_compname
            
            # Event Type determination
            event_type = self.determine_event_type(data_compname)
            
            return {
                'Date': formatted_date,
                'Time': formatted_time,
                'Venue': data_venue,
                'Ground': ground,
                'Referee': referee,
                'Team': team,
                'Competition Name': competition_name,
                'Your Club Name': your_club_name,
                'Opponent': opponent,
                'Event Type': event_type
            }
            
        except Exception as e:
            print(f"Error processing fixture data: {e}")
            return None
    
    def map_team_name(self, comp_name):
        """
        Map competition name to team name according to rules
        """
        comp_lower = comp_name.lower()
        
        if "fe12" in comp_lower:
            return "U12 GAA"
        elif "fe13" in comp_lower:
            return "U13 GAA"
        elif "fe14" in comp_lower:
            return "U14 GAA"
        elif "fe15" in comp_lower:
            return "U15 GAA"
        elif "fe16" in comp_lower:
            return "U16 GAA"
        elif "fe18" in comp_lower and "hurling" in comp_lower:
            return "Minor Hurling GAA"
        elif "fe18" in comp_lower and "football" in comp_lower:
            return "Minor Football GAA"
        elif "u21 a football" in comp_lower:
            return 'GAA U21 "A" Football'
        elif "u21 a hurling" in comp_lower:
            return "GAA U21 A Hurling"
        elif "junior a hurling" in comp_lower:
            return "Junior A Hurling"
        elif "junior a football" in comp_lower:
            return "Junior A Football"
        elif "junior b hurling" in comp_lower:
            return "Junior B Hurling"
        elif "senior fc" in comp_lower:
            return "Senior Football"
        elif "premier ihc" in comp_lower or "pihc" in comp_lower:
            return "Premier Inter Hurling"
        elif "division 2 fl" in comp_lower:
            return "Junior A Football"
        elif "division 1 fl" in comp_lower:
            return "Senior Football"
        elif "division 3 fl" in comp_lower:
            return "Junior B Football"
        elif "division 2 hl" in comp_lower:
            return "Junior A Hurling"
        elif "division 1 hl" in comp_lower:
            return "Senior Hurling"
        elif "division 3 hl" in comp_lower:
            return "Junior B Hurling"
        elif "senior football" in comp_lower:
            return "Senior Football"
        elif "premier inter hurling" in comp_lower:
            return "Premier Inter Hurling"
        elif "womens" in comp_lower:
            return "Womens GAA"
        elif "boys clubs" in comp_lower:
            return "Boys GAA"
        elif "u18.5" in comp_lower:
            return "U18.5 GAA"
        elif "red fm" in comp_lower and "hl" in comp_lower:
            return "Junior A Hurling"
        elif "red fm" in comp_lower and "fl" in comp_lower:
            return "Junior A Football"
        elif "mccarthy insurance group" in comp_lower and "fl" in comp_lower:
            return "Junior A Football"
        elif "mccarthy insurance group" in comp_lower and "hl" in comp_lower:
            return "Junior A Hurling"
        else:
            return "Unknown"
    
    def determine_event_type(self, comp_name):
        """
        Determine event type based on competition name
        """
        comp_lower = comp_name.lower()
        
        if "championship" in comp_lower or "final" in comp_lower:
            return "Championship"
        elif "cup" in comp_lower:
            return "Cup"
        else:
            return "League"
    
    def parse_future_fixture_element(self, element, club_id, today):
        """
        Parse future fixture element based on the format you provided
        
        Args:
            element: BeautifulSoup element containing fixture info
            club_id (int): Club ID to identify home/away
            today (datetime): Current date for filtering
            
        Returns:
            dict: Fixture data or None if not valid
        """
        text = element.get_text().strip()
        
        # Extract date
        date_pattern = re.compile(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)', re.IGNORECASE)
        date_match = date_pattern.search(text)
        
        if not date_match:
            return None
        
        # Parse the date
        day_name, day_num, month_name = date_match.groups()
        try:
            # Convert to datetime for comparison
            fixture_date = datetime.strptime(f"{day_num} {month_name} {today.year}", "%d %B %Y")
            
            # If fixture date is in the past, skip it
            if fixture_date.date() < today.date():
                return None
            
            formatted_date = fixture_date.strftime("%d/%m/%Y")
        except ValueError:
            formatted_date = f"{day_num} {month_name}"
        
        # Extract time
        time_pattern = re.compile(r'(\d{1,2}:\d{2})')
        time_match = time_pattern.search(text)
        fixture_time = time_match.group(1) if time_match else ""
        
        # Extract venue
        venue_pattern = re.compile(r'Venue:\s*([^\n\r]+)')
        venue_match = venue_pattern.search(text)
        venue = venue_match.group(1).strip() if venue_match else ""
        
        # Extract teams - look for club profile links
        team_links = element.find_all('a', href=re.compile(r'clubprofile/\d+'))
        teams = [link.get_text().strip() for link in team_links if link.get_text().strip()]
        
        # Find competition name
        competition_pattern = re.compile(r'([A-Za-z\s]+(?:FL|HL|FC|HC|SFC|IHC|JFC|JHC|PIHC))')
        competition_match = competition_pattern.search(text)
        competition = competition_match.group(1).strip() if competition_match else ""
        
        # Determine home/away teams
        home_team = ""
        away_team = ""
        
        if len(teams) >= 2:
            # Look for pattern like "Team1 TIME Team2"
            team_time_pattern = re.compile(r'([A-Za-z\s]+)\s+(\d{1,2}:\d{2})\s+([A-Za-z\s]+)')
            team_time_match = team_time_pattern.search(text)
            
            if team_time_match:
                home_team, time_found, away_team = team_time_match.groups()
                home_team = home_team.strip()
                away_team = away_team.strip()
            else:
                # Fallback: just use the first two teams found
                home_team, away_team = teams[0], teams[1]
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'date': formatted_date,
            'time': fixture_time,
            'venue': venue,
            'competition': competition,
            'day': day_name,
            'status': 'Upcoming'
        }
    
    def parse_fixture_element(self, element, club_id):
        """
        Parse individual fixture element
        
        Args:
            element: BeautifulSoup element containing fixture info
            club_id (int): Club ID to identify home/away
            
        Returns:
            dict: Fixture data or None if not relevant
        """
        text = element.get_text().strip()
        
        # Extract teams and score
        score_pattern = re.compile(r'(\d+-\d+)\s*v\s*(\d+-\d+)')
        score_match = score_pattern.search(text)
        
        if not score_match:
            return None
        
        # Extract date
        date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')
        date_match = date_pattern.search(text)
        
        # Extract time
        time_pattern = re.compile(r'(\d{2}:\d{2})')
        time_match = time_pattern.search(text)
        
        # Extract venue
        venue_links = element.find_all('a', href=re.compile(r'google\.com/maps'))
        venue = venue_links[0].get_text().strip() if venue_links else ""
        
        # Find team names
        team_links = element.find_all('a', href=re.compile(r'clubprofile'))
        teams = [link.get_text().strip() for link in team_links if link.get_text().strip()]
        
        if len(teams) >= 2:
            home_team, away_team = teams[0], teams[1]
            home_score, away_score = score_match.group(1), score_match.group(2)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'date': date_match.group(1) if date_match else "",
                'time': time_match.group(1) if time_match else "",
                'venue': venue,
                'competition': self.get_competition_name(element)
            }
        
        return None
    
    def get_competition_name(self, element):
        """
        Extract competition name from page context
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            str: Competition name
        """
        # Look for h1 or h2 headers near the element
        for header in element.find_all_previous(['h1', 'h2'], limit=3):
            header_text = header.get_text().strip()
            if header_text and not header_text.startswith('Menu'):
                return header_text
        
        return ""
    
    def extract_club_info(self, soup, profile_url, competition_id=None, team_id=None):
        """
        Extract club information from parsed HTML
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            profile_url (str): Original profile URL
            competition_id (int, optional): Competition ID for fixture extraction
            team_id (int, optional): Team ID for fixture extraction
            
        Returns:
            dict: Extracted club data
        """
        club_data = {
            'profile_url': profile_url
        }
        
        # Extract club name (main h1)
        h1_tag = soup.find('h1')
        if h1_tag:
            club_data['club_name'] = h1_tag.get_text().strip()
        
        # Extract address (usually in a p tag after h1)
        if h1_tag:
            next_p = h1_tag.find_next('p')
            if next_p:
                address_text = next_p.get_text().strip()
                club_data['address'] = address_text
        
        # Extract website link
        website_link = soup.find('a', href=re.compile(r'^https?://'))
        if website_link and 'gaacork.ie' not in website_link.get('href', ''):
            club_data['website'] = website_link.get('href').strip()
        
        # Extract email
        email_link = soup.find('a', href=re.compile(r'^mailto:'))
        if email_link:
            email = email_link.get('href').replace('mailto:', '').strip()
            club_data['email'] = email
        
        # Extract division (look for division names)
        divisions = ['Muskerry', 'Seandún', 'Imokilly', 'Carrigdhoun', 'Duhallow', 'Beara', 'Avondhu']
        page_text = soup.get_text().lower()
        for division in divisions:
            if division.lower() in page_text:
                club_data['division'] = division
                break
        
        # Extract colors (look for color patterns)
        color_patterns = [
            r'([A-Z][a-z]+(?:\s+&\s+[A-Z][a-z]+)*)\s*\+\s*([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)\s*/\s*([A-Z][a-z]+)'
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, soup.get_text())
            if match:
                colors = f"{match.group(1)} + {match.group(2)}"
                club_data['colors'] = colors
                break
        
        # Extract coordinates from directions link
        directions_link = soup.find('a', href=re.compile(r'google\.com/maps'))
        if directions_link:
            href = directions_link.get('href', '')
            # Extract coordinates from URL like /dir//51.892,-8.58863
            coord_match = re.search(r'/dir//([-\d.]+),([-\d.]+)', href)
            if coord_match:
                club_data['coordinates'] = f"{coord_match.group(1)},{coord_match.group(2)}"
        
        # Extract fixtures from the club profile page itself
        club_id_from_url = profile_url.split('/')[-2].split('?')[0]
        fixtures = self.extract_fixtures_from_club_page(soup, club_id_from_url)
        
        if fixtures:
            # Create CSV with exact column order as specified
            csv_lines = []
            # Header row
            csv_lines.append("Date,Time,Venue,Ground,Referee,Team,Competition Name,Your Club Name,Opponent,Event Type")
            
            # Data rows
            for fixture in fixtures:
                csv_line = f"{fixture['Date']},{fixture['Time']},{fixture['Venue']},{fixture['Ground']},{fixture['Referee']},{fixture['Team']},{fixture['Competition Name']},{fixture['Your Club Name']},{fixture['Opponent']},{fixture['Event Type']}"
                csv_lines.append(csv_line)
            
            # Join all lines with newlines
            club_data['fixtures'] = '\n'.join(csv_lines)
            club_data['competition_name'] = "Ballincollig Fixtures"
        
        return club_data
    
    def scrape_club_profile(self, club_id, competition_id=None, team_id=None):
        """
        Scrape a single club profile
        
        Args:
            club_id (int): Club ID
            competition_id (int, optional): Competition ID
            team_id (int, optional): Team ID
            
        Returns:
            dict: Club data or None if failed
        """
        # Build URL
        url = f"{BASE_URL}{club_id}/"
        params = []
        
        if competition_id:
            params.append(f"competition_id={competition_id}")
        if team_id:
            params.append(f"team_id={team_id}")
        
        if params:
            url += "?" + "&".join(params)
        
        print(f"Scraping: {url}")
        
        # Get page content
        soup = self.get_page_content(url)
        if not soup:
            return None
        
        # Extract data
        club_data = self.extract_club_info(soup, url, competition_id, team_id)
        
        # Add delay to be respectful
        time.sleep(REQUEST_DELAY)
        
        return club_data
    
    def scrape_multiple_clubs(self, club_ids, competition_id=None, team_id=None):
        """
        Scrape multiple club profiles
        
        Args:
            club_ids (list): List of club IDs
            competition_id (int, optional): Competition ID
            team_id (int, optional): Team ID
            
        Returns:
            list: List of club data dictionaries
        """
        results = []
        
        for club_id in club_ids:
            club_data = self.scrape_club_profile(club_id, competition_id, team_id)
            if club_data:
                results.append(club_data)
            else:
                print(f"Failed to scrape club {club_id}")
        
        return results


# Example usage
if __name__ == "__main__":
    scraper = GAAClubScraper()
    
    # Test with the provided URL
    club_data = scraper.scrape_club_profile(
        club_id=1986, 
        competition_id=206357, 
        team_id=327535
    )
    
    if club_data:
        print("Extracted data:")
        for key, value in club_data.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to extract data")
