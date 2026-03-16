"""
GAA Fixture Monitor
Runs periodically to check for fixture changes and regenerate CSV
"""

import os
import json
from datetime import datetime
from scraper import GAAClubScraper
import hashlib
from config import CLUB_ID, COMPETITION_ID, TEAM_ID, HASH_FILE, FIXTURES_CSV

class FixtureMonitor:
    def __init__(self):
        self.scraper = GAAClubScraper()
        self.hash_file = HASH_FILE
        self.output_file = FIXTURES_CSV
        
    def get_current_fixtures_hash(self):
        """Get hash of current fixtures for comparison"""
        club_data = self.scraper.scrape_club_profile(club_id=CLUB_ID, competition_id=COMPETITION_ID, team_id=TEAM_ID)
        
        if club_data and club_data.get('fixtures'):
            fixtures_text = club_data['fixtures']
            return hashlib.sha256(fixtures_text.encode()).hexdigest()
        return None
    
    def get_previous_hash(self):
        """Load previous hash from file"""
        if os.path.exists(self.hash_file):
            try:
                with open(self.hash_file, 'r') as f:
                    data = json.load(f)
                    return data.get('hash')
            except (json.JSONDecodeError, ValueError):
                print("WARNING: Corrupt hash file, treating as fresh run")
        return None
    
    def save_current_hash(self, current_hash):
        """Save current hash to file"""
        data = {
            'hash': current_hash,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.hash_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def regenerate_csv(self):
        """Regenerate the fixtures CSV"""
        print("Regenerating fixtures CSV...")
        club_data = self.scraper.scrape_club_profile(club_id=CLUB_ID, competition_id=COMPETITION_ID, team_id=TEAM_ID)
        
        if club_data and club_data.get('fixtures'):
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(club_data['fixtures'])
            
            print(f"✅ CSV regenerated: {self.output_file}")
            newline = '\n'
            print(f"📊 Found {len(club_data['fixtures'].split(newline))-1} fixtures")
            return True
        else:
            print("❌ No fixtures found")
            return False
    
    def check_for_changes(self):
        """Check if fixtures have changed"""
        print(f"🔍 Checking for fixture changes at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        current_hash = self.get_current_fixtures_hash()
        if not current_hash:
            print("❌ Could not get current fixtures")
            return False
        
        previous_hash = self.get_previous_hash()
        
        if current_hash != previous_hash:
            print("🚨 FIXTURE CHANGES DETECTED!")
            if self.regenerate_csv():
                self.save_current_hash(current_hash)
                print("✅ Changes processed and saved")
                return True
            else:
                print("❌ Failed to process changes")
                return False
        else:
            print("✅ No changes detected")
            return True

def main():
    monitor = FixtureMonitor()
    
    # Check for changes
    monitor.check_for_changes()

if __name__ == "__main__":
    main()
