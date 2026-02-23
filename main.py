"""
Main script to run the GAA club scraper
"""

from scraper import GAAClubScraper
from data_formatter import save_to_csv, load_existing_csv
import argparse


def main():
    parser = argparse.ArgumentParser(description='Scrape GAA club profiles')
    parser.add_argument('--club-id', type=int, help='Single club ID to scrape')
    parser.add_argument('--club-ids', nargs='+', type=int, help='Multiple club IDs to scrape')
    parser.add_argument('--competition-id', type=int, help='Competition ID')
    parser.add_argument('--team-id', type=int, help='Team ID')
    parser.add_argument('--output', type=str, help='Output CSV filename')
    parser.add_argument('--append', action='store_true', help='Append to existing CSV file')
    
    args = parser.parse_args()
    
    scraper = GAAClubScraper()
    
    # Determine which clubs to scrape
    if args.club_id:
        club_ids = [args.club_id]
    elif args.club_ids:
        club_ids = args.club_ids
    else:
        # Default to the example club
        club_ids = [1986]
        print("No club ID specified, using example club 1986 (Ballincollig)")
    
    print(f"Scraping {len(club_ids)} club(s)...")
    
    # Scrape the clubs
    club_data_list = scraper.scrape_multiple_clubs(
        club_ids, 
        args.competition_id, 
        args.team_id
    )
    
    if not club_data_list:
        print("No data was scraped")
        return
    
    # Handle appending to existing file
    if args.append:
        existing_data = load_existing_csv(args.output)
        if existing_data is not None:
            # Convert existing data to list of dicts
            existing_list = existing_data.to_dict('records')
            # Combine with new data
            club_data_list = existing_list + club_data_list
            print(f"Appended {len(club_data_list) - len(existing_list)} new records to existing file")
    
    # Save to CSV
    output_file = save_to_csv(club_data_list, args.output)
    
    print(f"\nScraping completed!")
    print(f"Data saved to: {output_file}")


if __name__ == "__main__":
    main()
