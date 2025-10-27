@echo off
cd /d "%~dp0..\docker"

echo Stopping Docker container...
docker-compose down
echo Done!