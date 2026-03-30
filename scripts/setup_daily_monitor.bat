@echo off
echo Setting up Daily GAA Fixture Monitor...

REM Get the full path to this script's directory
set SCRIPT_DIR=%~dp0

REM Create scheduled task to run daily at 10:00 AM
schtasks /create /tn "GAA Fixture Monitor" /tr "py \"%SCRIPT_DIR%enhanced_monitor.py\"" /sc daily /st 10:00 /f

echo.
echo Daily monitoring task created successfully!
echo.
echo Schedule: Every day at 10:00 AM
echo Windows notifications: Enabled
echo Output: Ballincollig_Fixtures_Final.csv
echo ClubZap diff: Auto-runs on changes
echo.
echo Commands:
echo   Run manually:  py enhanced_monitor.py
echo   ClubZap diff:  py clubzap_sync.py diff
echo   Mark uploaded: py clubzap_sync.py uploaded
echo   View task:     schtasks /query /tn "GAA Fixture Monitor"
echo   Delete task:   schtasks /delete /tn "GAA Fixture Monitor"
echo.
pause
