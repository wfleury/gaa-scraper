@echo off
cd /d "%~dp0"
echo Checking GAA Fixtures...
py enhanced_monitor.py
echo.
echo Running ClubZap sync diff...
py clubzap_sync.py diff
pause
