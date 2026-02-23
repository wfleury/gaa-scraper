"""
Debug script to find all competition links and check for more fixtures
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
    
    print("=== ALL COMPETITION LINKS ===")
    competition_links = soup.find_all('a', href=re.compile(r'league/\d+'))
    print(f"Found {len(competition_links)} competition links")
    
    all_competition_urls = set()
    for i, link in enumerate(competition_links):
        href = link.get('href', '')
        if href.startswith('/'):
            href = f"https://gaacork.ie{href}"
        all_competition_urls.add(href)
        
        link_text = link.get_text().strip()
        print(f"{i+1}. {href} - {link_text}")
    
    print(f"\n=== CHECKING EACH COMPETITION FOR BALLINCOLLIG FIXTURES ===")
    total_fixtures = 0
    
    for comp_url in sorted(all_competition_urls):
        print(f"\nChecking: {comp_url}")
        comp_soup = scraper.get_page_content(comp_url)
        if not comp_soup:
            print("  Failed to get competition page")
            continue
        
        # Find all fixture elements
        fixture_elements = comp_soup.find_all('ul', attrs={"data-date": True})
        ballincollig_count = 0
        
        for element in fixture_elements:
            data_hometeam = element.get('data-hometeam', '')
            data_awayteam = element.get('data-awayteam', '')
            
            if "Ballincollig" in data_hometeam or "Ballincollig" in data_awayteam:
                ballincollig_count += 1
                data_date = element.get('data-date', '')
                print(f"  Ballincollig fixture: {data_hometeam} vs {data_awayteam} on {data_date}")
        
        print(f"  Found {ballincollig_count} Ballincollig fixtures")
        total_fixtures += ballincollig_count
    
    print(f"\n=== TOTAL BALLINCOLLIG FIXTURES FOUND: {total_fixtures} ===")
    
    # Also try some additional competition IDs that might be missing
    print(f"\n=== TRYING ADDITIONAL COMPETITION IDS ===")
    additional_ids = []
    
    # Try a range of competition IDs
    for comp_id in range(211600, 211800):
        comp_url = f"https://gaacork.ie/league/{comp_id}/"
        if comp_url not in all_competition_urls:
            comp_soup = scraper.get_page_content(comp_url)
            if comp_soup:
                fixture_elements = comp_soup.find_all('ul', attrs={"data-date": True})
                if fixture_elements:
                    ballincollig_count = 0
                    for element in fixture_elements:
                        data_hometeam = element.get('data-hometeam', '')
                        data_awayteam = element.get('data-awayteam', '')
                        if "Ballincollig" in data_hometeam or "Ballincollig" in data_awayteam:
                            ballincollig_count += 1
                    
                    if ballincollig_count > 0:
                        print(f"  Found {ballincollig_count} Ballincollig fixtures in competition {comp_id}")
                        additional_ids.append(comp_id)
                        total_fixtures += ballincollig_count
    
    print(f"\n=== ADDITIONAL COMPETITIONS WITH BALLINCOLLIG FIXTURES ===")
    for comp_id in additional_ids:
        print(f"  Competition {comp_id}")
    
    print(f"\n=== FINAL TOTAL: {total_fixtures} BALLINCOLLIG FIXTURES ===")

if __name__ == "__main__":
    main()
