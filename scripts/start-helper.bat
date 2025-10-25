@echo off
cd /d "%~dp0..\helper"

echo ========================================
echo Chrome Launcher Helper Service
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo This service allows Docker to launch Chrome on your Windows machine.
echo.
echo Keep this window open while using the web application!
echo.
echo Service running on: http://127.0.0.1:5001
echo ========================================
echo.

python chrome_launcher_service.py

pause