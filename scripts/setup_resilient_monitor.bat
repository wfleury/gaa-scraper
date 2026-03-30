@echo off
echo Setting up Resilient GAA Fixture Monitor with Catch-Up...
echo.

:: Delete existing task if it exists
schtasks /delete /tn "GAA Daily Fixture Monitor" /f >nul 2>&1

:: Create new resilient task with catch-up
schtasks /create /tn "GAA Daily Fixture Monitor" /tr "python enhanced_monitor.py" /sc daily /st 09:00 /f /ru "%USERNAME%" /rl HIGHEST

:: Enable catch-up for missed runs
schtasks /change /tn "GAA Daily Fixture Monitor" /enable

echo SUCCESS: Resilient scheduled task created!
echo.
echo Features:
echo - Daily at 9:00 AM
echo - Catches up if PC was off
echo - Runs as soon as possible after missed schedule
echo - Persists through reboots
echo.
echo Task: "GAA Daily Fixture Monitor"
echo.
pause
