"""
Ballincollig Fixtures Extractor
Extracts fixtures from gaacork.ie and outputs Ballincollig_Fixtures_Final.csv
"""

from scraper import GAAClubScraper
import os

def main():
    # Initialize scraper
    scraper = GAAClubScraper()
    
    # Scrape Ballincollig fixtures with the specific competition from the example
    print("Scraping Ballincollig fixtures...")
    club_data = scraper.scrape_club_profile(club_id=1986, competition_id=211620, team_id=327535)
    
    if club_data and club_data.get('fixtures'):
        # Output to the specified filename
        output_file = "Ballincollig_Fixtures_Final.csv"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(club_data['fixtures'])
        
        print(f"Fixtures saved to: {output_file}")
        print("\n" + "="*50)
        print("CSV CONTENT:")
        print("="*50)
        print(club_data['fixtures'])
        print("="*50)
    else:
        print("No fixtures found or failed to scrape data")

if __name__ == "__main__":
    main()
