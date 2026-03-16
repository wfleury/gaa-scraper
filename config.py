"""
Configuration for GAA Club Scraper
"""

import os

# ---- Club identity ----
CLUB_NAME = "Ballincollig"
CLUB_ID = 1986
TEAM_ID = 327535
COMPETITION_ID = 211620
CLUBZAP_CLUB_ID = os.environ.get("CLUBZAP_CLUB_ID", "4975")

# ---- URLs ----
BASE_URL = "https://gaacork.ie/clubprofile/"
CLUBZAP_BASE_URL = "https://dashboard.clubzap.com"
CLUBZAP_FIXTURES_URL = f"{CLUBZAP_BASE_URL}/clubs/{CLUBZAP_CLUB_ID}/fixtures"

# ---- File paths ----
OUTPUT_DIR = "output"
CSV_FILENAME = "gaa_clubs.csv"
FIXTURES_CSV = "Ballincollig_Fixtures_Final.csv"
HASH_FILE = "fixture_hashes.json"
LOG_FILE = "monitoring_log.txt"
BASELINE_CSV = "clubzap_uploaded_baseline.csv"
NEW_CSV = "clubzap_new_fixtures.csv"
CHANGED_CSV = "clubzap_changed_fixtures.csv"
REMOVED_CSV = "clubzap_removed_fixtures.csv"

# ---- Notifications ----
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "ballincollig-gaa-fixtures")
NTFY_ICON = "https://sportlomo-userupload.s3.amazonaws.com/clubLogos/1986/ballincollig.gif"

# ---- CSV schema ----
FIXTURE_HEADER = [
    "Date", "Time", "Venue", "Ground", "Referee",
    "Team", "Competition Name", "Your Club Name", "Opponent", "Event Type",
]

# Columns that form the unique key for a fixture
KEY_COLS = ["Date", "Team", "Opponent", "Competition Name"]

# Columns where changes matter for updates
CHANGE_COLS = ["Time", "Venue", "Ground", "Referee"]

# ---- Request settings ----
REQUEST_DELAY = 1  # seconds between requests
TIMEOUT = 10  # seconds

# ---- Data fields to extract (general club profile scraping) ----
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
    "competition_name",
]

# ---- Filters ----
RUGBY_INDICATORS = ["rfc", "rugby", "rugbai", "munster bowl", "boys clubs"]
