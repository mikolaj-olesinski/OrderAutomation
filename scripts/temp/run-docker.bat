@echo off
cd /d "%~dp0..\docker"

echo Building Docker container...
docker-compose build

echo.
echo Starting application in Docker...
echo Open http://127.0.0.1:5000 in your browser
echo.
echo Hot reload is enabled - your code changes will apply automatically!
echo Press Ctrl+C to stop
echo.

docker-compose up