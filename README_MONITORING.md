# GAA Fixture Monitoring System

## 🎯 Purpose
Automatically monitor the GAA website for fixture changes and regenerate the CSV file when changes are detected.

## 📁 Files Created
- `monitor_fixtures.py` - Basic monitoring script
- `enhanced_monitor.py` - Advanced monitoring with logging and notifications
- `setup_monitoring.bat` - Windows Task Scheduler setup
- `README_MONITORING.md` - This documentation

## 🚀 Quick Start

### Option 1: Manual Monitoring
```bash
# Run the basic monitor
python monitor_fixtures.py

# Run the enhanced monitor
python enhanced_monitor.py
```

### Option 2: Automated Monitoring
```bash
# Set up automated hourly monitoring
setup_monitoring.bat

# Or manually create task:
schtasks /create /tn "GAA Fixture Monitor" /tr "python monitor_fixtures.py" /sc hourly /f
```

## 📊 How It Works

1. **Hash Comparison**: Creates MD5 hash of fixture content
2. **Change Detection**: Compares current hash with previous hash
3. **CSV Regeneration**: Updates CSV when changes detected
4. **Logging**: Records all monitoring activity
5. **Notifications**: Optional email alerts for changes

## ⚙️ Configuration

### Enhanced Monitor Features
- **Logging**: All activity logged to `monitoring_log.txt`
- **Email Notifications**: Configure in `enhanced_monitor.py`
- **Change Analysis**: Shows added/removed fixtures
- **Hash Storage**: Tracks fixture history in `fixture_hashes.json`

### Email Setup (Optional)
Edit `enhanced_monitor.py` to enable notifications:
```python
email_config = {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',  # Use app password
    'recipient_email': 'recipient@gmail.com'
}
```

## 📅 Scheduling Options

### Windows Task Scheduler
```bash
# Hourly monitoring
schtasks /create /tn "GAA Fixture Monitor" /tr "python monitor_fixtures.py" /sc hourly /f

# Every 30 minutes
schtasks /create /tn "GAA Fixture Monitor" /tr "python monitor_fixtures.py" /sc minute /mo 30 /f

# Daily at 9 AM
schtasks /create /tn "GAA Fixture Monitor" /tr "python monitor_fixtures.py" /sc daily /st 09:00 /f
```

### View/Manage Tasks
```bash
# View task details
schtasks /query /tn "GAA Fixture Monitor"

# Run task manually
schtasks /run /tn "GAA Fixture Monitor"

# Delete task
schtasks /delete /tn "GAA Fixture Monitor"
```

## 📁 Output Files

- `Ballincollig_Fixtures_Final.csv` - Updated fixture data
- `fixture_hashes.json` - Hash history for change detection
- `monitoring_log.txt` - Detailed monitoring log

## 🔧 Troubleshooting

### Common Issues
1. **Python not found**: Use `py monitor_fixtures.py` instead of `python`
2. **Permissions**: Run as administrator for task creation
3. **Path issues**: Use full paths in scheduled tasks

### Debug Mode
Add debug output to monitor_fixtures.py:
```python
print(f"Current hash: {current_hash}")
print(f"Previous hash: {previous_hash}")
```

## 📈 Monitoring Frequency

Recommended frequencies:
- **High season**: Every 30 minutes
- **Off season**: Every 2-4 hours
- **Pre-match day**: Every 15 minutes

## 🎯 Customization

### Monitor Different Clubs
Edit the club parameters:
```python
club_data = scraper.scrape_club_profile(
    club_id=YOUR_CLUB_ID, 
    competition_id=YOUR_COMPETITION_ID, 
    team_id=YOUR_TEAM_ID
)
```

### Custom Output
Change the output filename:
```python
self.output_file = "YourClub_Fixtures_Final.csv"
```

## 🔔 Notification Examples

### Change Detected
```
🚨 FIXTURE CHANGES DETECTED!
📊 Previous: 9 fixtures
📊 Current: 10 fixtures
➕ Added: 1 fixtures
➖ Removed: 0 fixtures
✅ Changes processed successfully
```

### No Changes
```
✅ No changes - 9 fixtures
```

## 📞 Support
For issues or questions:
1. Check the monitoring log file
2. Run the script manually to debug
3. Verify internet connection to gaacork.ie
4. Check file permissions
