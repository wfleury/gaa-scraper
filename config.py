"""
Configuration for GAA Club Scraper
"""

# Base URL for GAA Cork club profiles
BASE_URL = "https://gaacork.ie/clubprofile/"

# CSV output settings
OUTPUT_DIR = "output"
CSV_FILENAME = "gaa_clubs.csv"

# Request settings
REQUEST_DELAY = 1  # seconds between requests
TIMEOUT = 10  # seconds

# Data fields to extract
FIELDS_TO_EXTRACT = [
    "club_name",
    "address", 
    "website",
    "email",
    "division",
    "colors",
    "coordinates",
    "profile_url",
    "fixtures",
    "competition_name"
]
