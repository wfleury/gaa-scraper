# GAA Club Scraper

A Python web scraper that extracts club information from the Cork GAA website and exports it to CSV format.

## Features

- Scrapes club profiles from gaacork.ie
- Extracts club name, address, website, email, division, colors, and coordinates
- Exports data to clean CSV format
- Supports single or multiple club scraping
- Rate limiting to be respectful to the website
- Error handling and logging

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Scrape a single club (default example)
python main.py

# Scrape specific club
python main.py --club-id 1986

# Scrape multiple clubs
python main.py --club-ids 1986 1987 1988

# Scrape with competition and team IDs
python main.py --club-id 1986 --competition-id 206357 --team-id 327535
```

### Advanced Options
```bash
# Custom output filename
python main.py --club-id 1986 --output my_clubs.csv

# Append to existing CSV file
python main.py --club-ids 1986 1987 --append --output existing_file.csv
```

## Output Fields

The scraper extracts the following fields:

- **club_name**: Name of the GAA club
- **address**: Physical address/location
- **website**: Club website URL
- **email**: Contact email address
- **division**: GAA division (Muskerry, Seandún, etc.)
- **colors**: Club colors
- **coordinates**: GPS coordinates (if available)
- **profile_url**: URL of the scraped profile
- **scraped_at**: Timestamp of when data was collected

## Example Output

```csv
club_name,address,website,email,division,colors,coordinates,profile_url,scraped_at
Ballincollig,The Powdermills, Ballincollig,https://www.ballincolliggaa.ie,secretary.ballincollig.cork@gaa.ie,Muskerry,Green + White,51.892,-8.58863,https://gaacork.ie/clubprofile/1986/?competition_id=206357&team_id=327535,2024-02-03T15:07:00.123456
```

## Project Structure

```
gaa-scraper/
├── main.py              # Main script with CLI interface
├── scraper.py           # Core scraping logic
├── data_formatter.py    # CSV formatting utilities
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── output/              # Directory for CSV files
└── README.md           # This file
```

## Configuration

Edit `config.py` to modify:
- Request delay settings
- Output directory
- CSV filename
- Fields to extract

## Notes

- The scraper includes rate limiting (1 second delay between requests)
- Some clubs may not have all fields available
- Coordinates are extracted from Google Maps links when available
- Email addresses are cleaned to remove "Click here" text

## Testing

Test the scraper with the provided example:
```bash
python main.py --club-id 1986 --competition-id 206357 --team-id 327535
```

This will scrape the Ballincollig GAA club profile and save the data to `output/gaa_clubs.csv`.
