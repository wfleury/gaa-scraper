# Email Notification Setup Guide

## 📧 Configure Email Notifications

### Step 1: Update Email Settings
Edit `enhanced_monitor.py` and update these lines:

```python
email_config = {
    'enabled': True,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',      # YOUR EMAIL
    'sender_password': 'your_app_password',      # YOUR APP PASSWORD
    'recipient_email': 'your_email@gmail.com'    # YOUR EMAIL (or different)
}
```

### Step 2: Get Gmail App Password

#### For Gmail Users:
1. Go to: https://myaccount.google.com/
2. Click "Security"
3. Enable "2-Step Verification" (if not already enabled)
4. Click "App passwords"
5. Select "Mail" and your device
6. Copy the 16-character password
7. Use this password in `sender_password`

#### For Other Email Providers:
- **Outlook/Hotmail**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Work email**: Ask your IT department for SMTP settings

### Step 3: Test Email Configuration

```bash
# Test the monitor with current settings
python enhanced_monitor.py
```

Check the output for:
- `📧 Email notification sent` = Success
- `❌ Failed to send email` = Check settings

### Step 4: Set Up Daily Monitoring

```bash
# Run the setup script
setup_daily_monitor.bat

# Or create manually:
schtasks /create /tn "GAA Daily Fixture Monitor" /tr "python enhanced_monitor.py" /sc daily /st 09:00 /f
```

## 📨 Email Examples

### Initial Setup Email:
```
Subject: GAA Fixture Monitor Initialized

Body: Monitoring started with 20 fixtures
```

### Changes Detected Email:
```
Subject: 🚨 GAA Fixture Changes Detected

Body: Fixture changes detected:

Previous count: 20
Current count: 21
Added: 1
Removed: 0

Changes have been saved to: Ballincollig_Fixtures_Final.csv
```

## 🔧 Troubleshooting

### Common Email Issues:

1. **"Authentication failed"**
   - Use App Password (not regular password)
   - Enable 2-Step Verification first
   - Check email/typos

2. **"Connection refused"**
   - Check SMTP server and port
   - Verify firewall settings
   - Try different port (465 for SSL)

3. **"Sender address rejected"**
   - Verify sender email exists
   - Check sending limits
   - Use authenticated email

### Test Email Script:
```python
import smtplib
from email.mime.text import MIMEText

def test_email():
    msg = MIMEText("Test message from GAA Monitor")
    msg['Subject'] = "GAA Monitor Test"
    msg['From'] = "your_email@gmail.com"
    msg['To'] = "your_email@gmail.com"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
    server.quit()
    print("✅ Test email sent")

test_email()
```

## 📅 Schedule Options

### Change Monitoring Time:
```bash
# Different times (24-hour format):
schtasks /delete /tn "GAA Daily Fixture Monitor" /f
schtasks /create /tn "GAA Daily Fixture Monitor" /tr "python enhanced_monitor.py" /sc daily /st 08:00 /f  # 8 AM
schtasks /create /tn "GAA Daily Fixture Monitor" /tr "python enhanced_monitor.py" /sc daily /st 18:00 /f  # 6 PM
```

### Multiple Daily Checks:
```bash
# Every 12 hours (8 AM and 8 PM)
schtasks /create /tn "GAA Monitor AM" /tr "python enhanced_monitor.py" /sc daily /st 08:00 /f
schtasks /create /tn "GAA Monitor PM" /tr "python enhanced_monitor.py" /sc daily /st 20:00 /f
```

## 📊 Monitoring Files Created

- `monitoring_log.txt` - All monitoring activity
- `fixture_hashes.json` - Change detection history
- `Ballincollig_Fixtures_Final.csv` - Updated fixture data

## 🎯 Next Steps

1. ✅ Update email settings in `enhanced_monitor.py`
2. ✅ Run `python enhanced_monitor.py` to test
3. ✅ Run `setup_daily_monitor.bat` to schedule
4. ✅ Check email receives test notification
5. ✅ Monitor `monitoring_log.txt` for activity

Need help? Check the log file or run the script manually for debugging!
