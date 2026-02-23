@echo off
echo Setting up GAA Fixture Monitor...

REM Create scheduled task to run every hour
schtasks /create /tn "GAA Fixture Monitor" /tr "python \"%~dp0monitor_fixtures.py\"" /sc hourly /f

echo Task created successfully!
echo.
echo To run manually: python monitor_fixtures.py
echo To view task: schtasks /query /tn "GAA Fixture Monitor"
echo To delete task: schtasks /delete /tn "GAA Fixture Monitor"
pause
