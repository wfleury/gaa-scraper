"""
Enhanced GAA Fixture Monitor with notifications and logging
"""

import os
import json
from datetime import datetime, timedelta
from scraper import GAAClubScraper
from selenium_scraper import SeleniumScraper
import hashlib
import subprocess
import sys
import requests

class EnhancedFixtureMonitor:
    def __init__(self):
        self.scraper = GAAClubScraper()
        self.selenium_scraper = SeleniumScraper()
        self.hash_file = "fixture_hashes.json"
        self.log_file = "monitoring_log.txt"
        self.output_file = "Ballincollig_Fixtures_Final.csv"
        self.ntfy_topic = "ballincollig-gaa-fixtures"
        
    def log_message(self, message):
        """Log message to file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(message)
    
    def get_fixtures_data(self):
        """Get current fixtures data using Selenium for complete coverage"""
        try:
            # Use Selenium scraper for complete fixture coverage
            fixtures = self.selenium_scraper.scrape_club_profile(club_id=1986, team_id=327535)
            
            if fixtures:
                # Convert to CSV format
                csv_lines = ["Date,Time,Venue,Ground,Referee,Team,Competition Name,Your Club Name,Opponent,Event Type"]
                
                for fixture in fixtures:
                    # Process fixture data
                    home_team = fixture.get('home', '')
                    away_team = fixture.get('away', '')
                    date = fixture.get('date', '')
                    time = fixture.get('time', '')
                    venue = fixture.get('venue', '')
                    competition = fixture.get('competition', '')
                    
                    # Determine if Ballincollig is home or away
                    if 'Ballincollig' in home_team:
                        ground = 'Home'
                        opponent = away_team
                    elif 'Ballincollig' in away_team:
                        ground = 'Away'
                        opponent = home_team
                    else:
                        continue  # Skip if no Ballincollig team
                    
                    # Map team name and event type
                    team = self.map_team_name(competition)
                    event_type = self.determine_event_type(competition)
                    
                    # Format date
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(date, '%d %b %Y')
                        formatted_date = dt.strftime('%d/%m/%Y')
                    except:
                        formatted_date = date
                    
                    # Format time (add leading 0 if needed)
                    # 00:00 means fixture is cancelled/postponed
                    if time == '00:00' or time == '0:00':
                        time = 'Postponed'
                        event_type = 'Postponed'
                    elif time and len(time) == 4:
                        time = f'0{time}'
                    
                    referee = fixture.get('referee', '').strip()
                    if not referee:
                        referee = 'TBC (Pending)'
                    
                    csv_line = f"{formatted_date},{time},{venue},{ground},{referee},{team},{competition},Ballincollig,{opponent},{event_type}"
                    csv_lines.append(csv_line)
                
                fixtures_text = '\n'.join(csv_lines)
                fixtures_hash = hashlib.md5(fixtures_text.encode()).hexdigest()
                fixture_count = len(csv_lines) - 1  # Subtract header
                
                return {
                    'hash': fixtures_hash,
                    'text': fixtures_text,
                    'count': fixture_count,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.log_message("No fixtures found with Selenium")
                return None
                
        except Exception as e:
            self.log_message(f"Error with Selenium scraper: {e}")
            # Fallback to original scraper
            self.log_message("Falling back to original scraper...")
            club_data = self.scraper.scrape_club_profile(club_id=1986, competition_id=211620, team_id=327535)
            
            if club_data and club_data.get('fixtures'):
                fixtures_text = club_data['fixtures']
                fixtures_hash = hashlib.md5(fixtures_text.encode()).hexdigest()
                fixture_count = len(fixtures_text.split('\n')) - 1  # Subtract header
                
                return {
                    'hash': fixtures_hash,
                    'text': fixtures_text,
                    'count': fixture_count,
                    'timestamp': datetime.now().isoformat()
                }
            return None
    
    def load_previous_data(self):
        """Load previous fixture data"""
        if os.path.exists(self.hash_file):
            with open(self.hash_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_current_data(self, data):
        """Save current fixture data"""
        with open(self.hash_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def map_team_name(self, competition_name):
        """Map competition name to Ballincollig ClubZap team name.
        
        ClubZap team names:
        Senior Football, Premier Inter Hurling,
        Junior A Football, Junior A Hurling, Junior B Football, Junior B Hurling, Junior C Football,
        Minor Football GAA, Minor Hurling GAA,
        U14 GAA, U16 GAA,
        GAA U21 "A" Football, GAA U21 "A" Hurling, GAA U21 "B" Football, GAA U21 "B" Hurling
        """
        comp_lower = competition_name.lower()
        
        # Determine code (football or hurling)
        is_football = any(x in comp_lower for x in ['football', ' fl'])
        is_hurling = any(x in comp_lower for x in ['hurling', ' hl'])
        
        # --- Underage (Fe14 / Fe16 use single "GAA" team name for both codes) ---
        if 'fe14' in comp_lower:
            return 'U14 GAA'
        if 'fe16' in comp_lower:
            return 'U16 GAA'
        
        # --- Minor (Fe18 splits by code) ---
        if 'fe18' in comp_lower:
            if is_hurling:
                return 'Minor Hurling GAA'
            return 'Minor Football GAA'
        
        # --- County Senior Leagues ---
        if 'mccarthy insurance' in comp_lower or 'mccarthy' in comp_lower:
            return 'Senior Football'
        if 'red fm' in comp_lower:
            return 'Premier Inter Hurling'
        
        # --- County Championships ---
        if 'psfc' in comp_lower or ('premier senior' in comp_lower and is_football):
            return 'Senior Football'
        if 'pihc' in comp_lower or ('premier intermediate' in comp_lower and is_hurling):
            return 'Premier Inter Hurling'
        
        # --- Divisional Junior Leagues (AOS Security = Muskerry division) ---
        if 'aos security' in comp_lower or 'aos ' in comp_lower:
            if 'div 4' in comp_lower or 'div 5' in comp_lower:
                if is_hurling:
                    return 'Junior B Hurling'
                return 'Junior B Football'
            elif 'div 3' in comp_lower:
                if is_hurling:
                    return 'Junior B Hurling'
                return 'Junior A Football'
            else:
                if is_hurling:
                    return 'Junior A Hurling'
                return 'Junior A Football'
        
        # --- Muskerry Divisional Junior Leagues (Cumnor, EPH, Erneside Eng sponsors) ---
        if 'cumnor' in comp_lower:
            return 'Junior A Hurling'
        if 'eph ' in comp_lower:
            if 'division 2' in comp_lower or 'division 3' in comp_lower:
                return 'Junior B Football'
            return 'Junior A Football'
        if 'erneside' in comp_lower:
            return 'Junior B Hurling'
        
        # --- Other Junior/Divisional competitions ---
        if 'junior' in comp_lower:
            if is_hurling:
                return 'Junior A Hurling'
            return 'Junior A Football'
        
        # --- U21 ---
        if 'u21' in comp_lower or 'u-21' in comp_lower:
            if is_hurling:
                return 'GAA U21 "A" Hurling'
            return 'GAA U21 "A" Football'
        
        return 'Unknown'
    
    def determine_event_type(self, competition_name):
        """Determine event type from competition name"""
        comp_lower = competition_name.lower()
        
        if 'championship' in comp_lower:
            return 'Championship'
        elif any(x in comp_lower for x in ['cup', 'shield', 'trophy']):
            return 'Cup'
        elif any(x in comp_lower for x in ['league', 'division', ' fl', ' hl']):
            return 'League'
        else:
            return 'Other'
    
    def regenerate_csv(self, fixtures_text):
        """Regenerate the fixtures CSV"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(fixtures_text)
            return True
        except Exception as e:
            self.log_message(f"Error saving CSV: {e}")
            return False
    
    def send_notification(self, title, message):
        """Send Windows toast + ntfy.sh mobile push notification"""
        # --- Windows toast notification ---
        try:
            ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml('<toast><visual><binding template="ToastGeneric"><text>{title}</text><text>{message}</text></binding></visual></toast>')

$toast = New-Object Windows.UI.Notifications.ToastNotification($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("GAA Monitor").Show($toast)
'''
            
            result = subprocess.run([
                'powershell', '-Command', ps_script
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.log_message("Windows toast notification sent")
            else:
                msg_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show("{message}", "{title}", "OK", "Information")
'''
                subprocess.run([
                    'powershell', '-Command', msg_script
                ], timeout=10)
                self.log_message("Message box notification sent")
                
        except Exception as e:
            self.log_message(f"Failed to send Windows notification: {e}")
            print(f"\nNOTIFICATION: {title}")
            print(f"Message: {message}\n")
        
        # --- ntfy.sh mobile push notification ---
        self.send_ntfy(title, message)
    
    def send_ntfy(self, title, message):
        """Send push notification to phone via ntfy.sh with Ballincollig crest"""
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            resp = requests.post(
                f"https://ntfy.sh/{self.ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    "Title": title,
                    "Priority": "high",
                    "Icon": "https://sportlomo-userupload.s3.amazonaws.com/clubLogos/1986/ballincollig.gif"
                },
                timeout=10,
                verify=False
            )
            if resp.status_code == 200:
                self.log_message("ntfy.sh mobile notification sent")
            else:
                self.log_message(f"ntfy.sh returned status {resp.status_code}")
        except Exception as e:
            self.log_message(f"Failed to send ntfy.sh notification: {e}")
    
    def send_ntfy_quiet(self, title, message):
        """Send low-priority (silent) push notification via ntfy.sh"""
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            resp = requests.post(
                f"https://ntfy.sh/{self.ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    "Title": title,
                    "Priority": "low",
                    "Icon": "https://sportlomo-userupload.s3.amazonaws.com/clubLogos/1986/ballincollig.gif"
                },
                timeout=10,
                verify=False
            )
            if resp.status_code == 200:
                self.log_message("ntfy.sh quiet notification sent")
            else:
                self.log_message(f"ntfy.sh returned status {resp.status_code}")
        except Exception as e:
            self.log_message(f"Failed to send ntfy.sh notification: {e}")
    
    def analyze_changes(self, old_text, new_text):
        """Analyze what changed between old and new fixtures"""
        old_lines = set(old_text.split('\n')) if old_text else set()
        new_lines = set(new_text.split('\n')) if new_text else set()
        
        added = new_lines - old_lines
        removed = old_lines - new_lines
        
        return {
            'added': list(added),
            'removed': list(removed),
            'added_count': len(added),
            'removed_count': len(removed)
        }
    
    def check_for_changes(self):
        """Main monitoring function"""
        self.log_message("Starting fixture check...")
        
        current_data = self.get_fixtures_data()
        if not current_data:
            self.log_message("ERROR: Could not retrieve current fixtures")
            return False
        
        previous_data = self.load_previous_data()
        
        if not previous_data:
            self.log_message("INFO: First run - initializing monitoring")
            self.regenerate_csv(current_data['text'])
            self.save_current_data(current_data)
            self.send_notification(
                "GAA Fixture Monitor Initialized",
                f"Monitoring started with {current_data['count']} fixtures"
            )
            return True
        
        if current_data['hash'] != previous_data['hash']:
            self.log_message("ALERT: FIXTURE CHANGES DETECTED!")
            
            # Analyze changes
            changes = self.analyze_changes(previous_data.get('text'), current_data['text'])
            
            self.log_message(f"INFO: Previous: {previous_data['count']} fixtures")
            self.log_message(f"INFO: Current: {current_data['count']} fixtures")
            self.log_message(f"INFO: Added: {changes['added_count']} fixtures")
            self.log_message(f"INFO: Removed: {changes['removed_count']} fixtures")
            
            # Regenerate CSV
            if self.regenerate_csv(current_data['text']):
                self.save_current_data(current_data)
                
                # Run ClubZap sync diff and build detailed notification
                diff_summary = ""
                try:
                    from clubzap_sync import read_csv_fixtures, fixture_key, FULL_CSV, BASELINE_CSV, CHANGE_COLS
                    current = read_csv_fixtures(FULL_CSV)
                    baseline = read_csv_fixtures(BASELINE_CSV)
                    
                    new_items = []
                    changed_items = []
                    postponed_items = []
                    removed_items = []
                    
                    for key, row in current.items():
                        if row.get('Time', '') == 'Postponed':
                            postponed_items.append(row)
                        elif key not in baseline:
                            new_items.append(row)
                        else:
                            old_row = baseline[key]
                            row_changes = []
                            for col in CHANGE_COLS:
                                if old_row.get(col, '').strip() != row.get(col, '').strip():
                                    row_changes.append(f"  {col}: {row.get(col, '')}")
                            if row_changes:
                                changed_items.append((row, row_changes))
                    
                    for key, row in baseline.items():
                        if key not in current:
                            removed_items.append(row)
                    
                    parts = []
                    if new_items:
                        parts.append(f"NEW ({len(new_items)}):")
                        for r in new_items[:5]:
                            parts.append(f"  {r['Date']} {r['Team']} vs {r['Opponent']}")
                        if len(new_items) > 5:
                            parts.append(f"  ...and {len(new_items)-5} more")
                    
                    if changed_items:
                        parts.append(f"CHANGED ({len(changed_items)}):")
                        for r, ch in changed_items[:5]:
                            parts.append(f"  {r['Date']} {r['Team']} vs {r['Opponent']}")
                            for c in ch:
                                parts.append(f"    {c}")
                        if len(changed_items) > 5:
                            parts.append(f"  ...and {len(changed_items)-5} more")
                    
                    if postponed_items:
                        parts.append(f"POSTPONED ({len(postponed_items)}):")
                        for r in postponed_items:
                            parts.append(f"  {r['Date']} {r['Team']} vs {r['Opponent']}")
                    
                    if removed_items:
                        parts.append(f"REMOVED ({len(removed_items)}):")
                        for r in removed_items:
                            parts.append(f"  {r['Date']} {r['Team']} vs {r['Opponent']}")
                    
                    diff_summary = "\n".join(parts) if parts else "No ClubZap action needed"
                    
                    # Also run the full diff to generate CSV files
                    from clubzap_sync import diff_fixtures
                    self.log_message("Running ClubZap sync diff...")
                    diff_fixtures()
                except Exception as e:
                    self.log_message(f"ClubZap sync diff failed: {e}")
                    diff_summary = f"Fixtures: {previous_data['count']} -> {current_data['count']}"
                
                notification_msg = f"Ballincollig GAA Fixtures Update\n\n{diff_summary}"
                
                self.send_notification("Ballincollig GAA - Fixture Changes", notification_msg)
                
                self.log_message("SUCCESS: Changes processed successfully")
                return True
            else:
                self.log_message("ERROR: Failed to process changes")
                return False
        else:
            self.log_message(f"INFO: No changes - {current_data['count']} fixtures")
            # Always regenerate CSV so it's available for artifacts and sync
            self.regenerate_csv(current_data['text'])
            # Send low-priority "all clear" notification so user knows monitor ran
            self.send_ntfy_quiet(
                "Ballincollig GAA - All Clear",
                f"No fixture changes detected.\n{current_data['count']} fixtures monitored."
            )
            return True

def main():
    monitor = EnhancedFixtureMonitor()
    try:
        monitor.check_for_changes()
    finally:
        monitor.selenium_scraper.close()

if __name__ == "__main__":
    main()
