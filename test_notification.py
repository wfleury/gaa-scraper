"""
Test Windows notifications for GAA Fixture Monitor
"""

import subprocess
import sys

def test_notification():
    """Test Windows notification system"""
    
    title = "GAA Fixture Monitor Test"
    message = "This is a test notification from your Ballincollig fixture monitor!"
    
    try:
        # Use PowerShell to send Windows toast notification
        ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.BalloonTipTitle = "{title}"
$notification.BalloonTipText = "{message}"
$notification.BalloonTipIcon = "Info"
$notification.Visible = $true
$notification.ShowBalloonTip(10000)
Start-Sleep -Seconds 10
$notification.Dispose()
'''
        
        # Execute PowerShell script
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("SUCCESS: Windows notification sent successfully!")
            print("You should see a toast notification in your system tray.")
        else:
            print(f"ERROR: Notification failed: {result.stderr}")
            
    except Exception as e:
        print(f"ERROR: Failed to send notification: {e}")
        print("FALLBACK NOTIFICATION:")
        print(f"   Title: {title}")
        print(f"   Message: {message}")

if __name__ == "__main__":
    test_notification()
