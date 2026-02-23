"""
Debug script to find all fixtures on Ballincollig club profile page
"""

from scraper import GAAClubScraper
import re

def main():
    # Initialize scraper
    scraper = GAAClubScraper()
    
    # Get the page content
    url = "https://gaacork.ie/clubprofile/1986/?team_id=327535"
    print(f"Debugging: {url}")
    
    soup = scraper.get_page_content(url)
    if not soup:
        print("Failed to get page content")
        return
    
    print("=== ALL ELEMENTS WITH DATA-DATE ===")
    all_date_elements = soup.find_all(attrs={"data-date": True})
    print(f"Found {len(all_date_elements)} total elements with data-date")
    
    ballincollig_fixtures = []
    for i, element in enumerate(all_date_elements):
        data_date = element.get('data-date', '')
        data_hometeam = element.get('data-hometeam', '')
        data_awayteam = element.get('data-awayteam', '')
        data_compname = element.get('data-compname', '')
        
        print(f"\nElement {i+1}:")
        print(f"  Tag: {element.name}")
        print(f"  Classes: {element.get('class', [])}")
        print(f"  Date: {data_date}")
        print(f"  Home: {data_hometeam}")
        print(f"  Away: {data_awayteam}")
        print(f"  Competition: {data_compname}")
        
        if "Ballincollig" in data_hometeam or "Ballincollig" in data_awayteam:
            ballincollig_fixtures.append(element)
            print(f"  *** BALLINCOLLIG FIXTURE ***")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total elements with data-date: {len(all_date_elements)}")
    print(f"Ballincollig fixtures: {len(ballincollig_fixtures)}")
    
    print(f"\n=== ALL UL ELEMENTS ===")
    all_uls = soup.find_all('ul')
    print(f"Found {len(all_uls)} ul elements")
    
    fixture_uls = []
    for i, ul in enumerate(all_uls):
        classes = ul.get('class', [])
        if 'fixtures' in classes:
            fixture_uls.append(ul)
            print(f"UL {i+1}: {classes}")
            # Check if it has data attributes
            if ul.get('data-date'):
                print(f"  Has data-date: {ul.get('data-date')}")
                print(f"  Home: {ul.get('data-hometeam')}")
                print(f"  Away: {ul.get('data-awayteam')}")
    
    print(f"\nFound {len(fixture_uls)} ul elements with 'fixtures' class")

if __name__ == "__main__":
    main()
