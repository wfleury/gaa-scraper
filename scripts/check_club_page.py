"""
Check what's actually on the club profile page
"""

import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_club_page():
    """Check the club profile page content"""
    
    url = "https://gaacork.ie/clubprofile/1986/?team_id=327535"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    session.verify = False
    
    try:
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== Checking Club Profile Page ===")
        print(f"URL: {url}")
        print()
        
        # Look for any elements that might contain fixtures
        fixture_elements = soup.find_all('ul', class_=lambda x: x and 'fixture' in str(x).lower())
        print(f"Found {len(fixture_elements)} elements with 'fixture' in class")
        
        for i, element in enumerate(fixture_elements[:5]):  # Show first 5
            print(f"\nElement {i+1}:")
            print(f"  Class: {element.get('class', [])}")
            print(f"  Data attributes: {[k for k in element.attrs.keys() if k.startswith('data-')]}")
            
            # Check for Ballincollig in data attributes
            data_hometeam = element.get('data-hometeam', '')
            data_awayteam = element.get('data-awayteam', '')
            
            if 'Ballincollig' in data_hometeam or 'Ballincollig' in data_awayteam:
                print(f"  *** BALLINCOLLIG FIXTURE FOUND ***")
                print(f"  Home: {data_hometeam}")
                print(f"  Away: {data_awayteam}")
                print(f"  Date: {element.get('data-date', '')}")
                print(f"  Competition: {element.get('data-compname', '')}")
        
        # Also look for any elements with data-date (might be fixtures)
        date_elements = soup.find_all('ul', attrs={'data-date': True})
        print(f"\nFound {len(date_elements)} elements with data-date attribute")
        
        ballincollig_count = 0
        for element in date_elements:
            data_hometeam = element.get('data-hometeam', '')
            data_awayteam = element.get('data-awayteam', '')
            
            if 'Ballincollig' in data_hometeam or 'Ballincollig' in data_awayteam:
                ballincollig_count += 1
                if ballincollig_count <= 5:  # Show first 5
                    print(f"  Ballincollig fixture: {data_hometeam} vs {data_awayteam} on {element.get('data-date', '')}")
        
        print(f"\nTotal Ballincollig fixtures found on page: {ballincollig_count}")
        
        # Look for competition links
        competition_links = soup.find_all('a', href=lambda x: x and 'league' in str(x))
        print(f"\nFound {len(competition_links)} competition links")
        
        # Show first few competition links
        for i, link in enumerate(competition_links[:5]):
            print(f"  {link.get('href', '')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_club_page()
