"""
Native Windows notification using Windows Runtime
"""

import subprocess
import sys

def native_notification():
    """Send notification using Windows native methods"""
    
    title = "GAA Fixture Monitor"
    message = "Test notification - Ballincollig fixtures updated!"
    
    try:
        # Use Windows 10/11 toast notification via PowerShell
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
            print("SUCCESS: Windows 10/11 toast notification sent!")
            print("Check your system tray (bottom-right corner)")
        else:
            print("Toast failed, trying message box...")
            
            # Simple message box fallback
            msg_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show("{message}", "{title}", "OK", "Information")
'''
            
            subprocess.run([
                'powershell', '-Command', msg_script
            ], timeout=10)
            
            print("SUCCESS: Message box displayed!")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Try this manual command:")
        print(f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'{message}\', \'{title}\', \'OK\', \'Information\')"')

if __name__ == "__main__":
    native_notification()
