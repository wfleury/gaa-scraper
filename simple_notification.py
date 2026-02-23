"""
Simple Windows notification test
"""

import subprocess

def simple_notification():
    """Send a simple Windows notification"""
    
    title = "GAA Fixture Monitor"
    message = "Test notification - Ballincollig fixtures updated!"
    
    # Simple PowerShell toast notification
    ps_script = f'''
New-BurntToastNotification -Text "GAA Fixture Monitor", "{message}" -AppId "Microsoft.Windows.Shell.RunDialog"
'''
    
    try:
        result = subprocess.run([
            'powershell', '-Command', ps_script
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("SUCCESS: Simple notification sent!")
            print("Check your system tray (bottom-right corner)")
        else:
            print("Notification failed, trying alternative...")
            # Fallback to message box
            fallback_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show("{message}", "{title}", "OK", "Information")
'''
            
            subprocess.run([
                'powershell', '-Command', fallback_script
            ], timeout=3)
            
            print("SUCCESS: Message box shown!")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Fallback notification:")
        print(f"Title: {title}")
        print(f"Message: {message}")

if __name__ == "__main__":
    simple_notification()
