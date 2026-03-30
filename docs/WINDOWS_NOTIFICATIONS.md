# Windows Notifications for GAA Fixture Monitor

## 🔔 Windows Toast Notifications

Your GAA Fixture Monitor now uses **Windows native notifications** instead of email!

## ✅ What You'll See

### When Changes Are Detected:
- **Toast notification** appears in system tray
- **Title**: "GAA Fixture Changes Detected"
- **Message**: Shows fixture count changes
- **Duration**: 5 seconds auto-dismiss

### Initial Setup:
- **Title**: "GAA Fixture Monitor Initialized"  
- **Message**: Shows starting fixture count

## 🎯 Notification Examples

### Fixture Changes Detected:
```
Title: GAA Fixture Changes Detected
Message: Previous: 19 fixtures
        Current: 20 fixtures  
        Added: 1
        Removed: 0
        CSV updated: Ballincollig_Fixtures_Final.csv
```

### Monitor Initialized:
```
Title: GAA Fixture Monitor Initialized
Message: Monitoring started with 19 fixtures
```

## ⚙️ How It Works

1. **PowerShell Integration**: Uses Windows PowerShell toast notifications
2. **System Tray**: Appears as standard Windows notification
3. **Auto-Dismiss**: 5-second display with manual dismiss option
4. **Fallback**: Console output if notifications fail

## 🔧 Testing Notifications

```bash
# Test the notification system
python test_notification.py

# Test the full monitor
python enhanced_monitor.py
```

## 📱 Notification Settings

### Windows Settings (Optional):
- **Settings** → **System** → **Notifications & actions**
- Ensure "Get notifications from apps and other senders" is ON
- Adjust notification duration and sounds as preferred

### PowerShell Execution Policy:
If notifications don't work, run this once as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Notification Triggers

### You'll get notifications when:
- ✅ **First run**: Monitor initialization
- ✅ **Fixtures added**: New fixtures appear
- ✅ **Fixtures removed**: Fixtures cancelled/changed
- ✅ **Fixture updates**: Time/venue changes detected

### No notifications for:
- ❌ No changes found
- ❌ Network errors (logged only)
- ❌ Rugby fixtures (automatically filtered)

## 🔄 Daily Schedule

- **Runs**: Every day at 9:00 AM
- **Checks**: All Ballincollig GAA fixtures
- **Notifies**: Only when changes detected
- **Logs**: All activity to `monitoring_log.txt`

## 🛠️ Troubleshooting

### If No Notifications Appear:

1. **Check Windows Settings**:
   - Settings → System → Notifications & actions
   - Ensure notifications are enabled

2. **Run Test Script**:
   ```bash
   python test_notification.py
   ```

3. **Check PowerShell Policy**:
   ```powershell
   Get-ExecutionPolicy
   # Should be RemoteSigned or Unrestricted
   ```

4. **Review Log File**:
   ```bash
   type monitoring_log.txt
   ```

### Common Issues:

- **"Notification failed"**: Check PowerShell execution policy
- **"No notification visible":** Check Windows notification settings
- **"PowerShell not found"**: Ensure PowerShell is installed (default on Windows)

## 📁 Related Files

- `enhanced_monitor.py` - Main monitor with notifications
- `test_notification.py` - Test notification system
- `monitoring_log.txt` - Activity log
- `fixture_hashes.json` - Change detection history

## 🎯 Benefits Over Email

✅ **Instant**: No email delay
✅ **Local**: No internet required for notifications  
✅ **Native**: Uses Windows built-in system
✅ **Simple**: No email configuration needed
✅ **Reliable**: Works with Windows notification system

Your monitor is now ready with Windows notifications! 🚀
