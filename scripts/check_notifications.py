"""
Check Windows notification settings and provide guidance
"""

import subprocess
import sys

def check_notification_settings():
    """Check if Windows notifications are properly configured"""
    
    print("=== Windows Notification Check ===")
    print()
    
    # Test 1: Check if PowerShell can create notifications
    print("1. Testing PowerShell notification capability...")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("Test notification", "GAA Monitor Test", "OK", "Information")'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   SUCCESS: PowerShell notifications work")
        else:
            print("   ISSUE: PowerShell notifications failed")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test 2: Simple toast notification
    print("2. Testing toast notification...")
    try:
        result = subprocess.run([
            'powershell', '-Command', 
            'Add-Type -AssemblyName System.Windows.Forms; $notify = New-Object System.Windows.Forms.NotifyIcon; $notify.Icon = [System.Drawing.SystemIcons]::Information; $notify.BalloonTipTitle = "GAA Test"; $notify.BalloonTipText = "Test message"; $notify.Visible = $true; $notify.ShowBalloonTip(3000); Start-Sleep 1; $notify.Dispose()'
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            print("   SUCCESS: Toast notification sent")
            print("   Look in your system tray (bottom-right) for the notification!")
        else:
            print("   ISSUE: Toast notification failed")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    print("=== Where to Look for Notifications ===")
    print("1. System Tray (bottom-right corner, near clock)")
    print("2. Action Center (click speech bubble icon 🗨️ or Windows Key + A)")
    print("3. Check if 'Focus Assist' is OFF (moon icon in system tray)")
    print()
    
    print("=== Windows Settings to Check ===")
    print("1. Press Windows Key + I")
    print("2. Go to System > Notifications & actions")
    print("3. Ensure 'Get notifications from apps and other senders' is ON")
    print("4. Check 'Show notifications in action center' is ON")
    print("5. Make sure Focus Assist is OFF or set to 'Priority only'")
    print()
    
    print("=== Manual Test ===")
    print("Try this manual PowerShell command:")
    print('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'Test\', \'GAA Monitor\', \'OK\', \'Information\')"')
    print()
    
    print("If you see a popup dialog, notifications are working.")
    print("If not, check your Windows notification settings above.")

if __name__ == "__main__":
    check_notification_settings()
