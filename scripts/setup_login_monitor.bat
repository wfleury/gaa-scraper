@echo off
echo Setting up Login-Triggered GAA Fixture Monitor...
echo.

:: Create login-triggered task (runs when you log in)
schtasks /create /tn "GAA Login Monitor" /tr "python enhanced_monitor.py" /sc onlogon /f

echo SUCCESS: Login monitor created!
echo.
echo Features:
echo - Runs when you log into Windows
echo - Catches up if you missed 9:00 AM
echo - Complements daily 9:00 AM schedule
echo - Persists through reboots
echo.
echo Tasks created:
echo - "GAA Daily Fixture Monitor" (daily at 9:00 AM)
echo - "GAA Login Monitor" (runs at login)
echo.
echo You'll get notifications either way!
echo.
pause
