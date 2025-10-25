#!/bin/bash

cd "$(dirname "$0")/../helper"

echo "========================================"
echo "Chrome Launcher Helper Service"
echo "========================================"
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo ""
echo "This service allows Docker to launch Chrome on your Mac/Linux machine."
echo ""
echo "Keep this terminal open while using the web application!"
echo ""
echo "Service running on: http://127.0.0.1:5001"
echo "========================================"
echo ""

python3 chrome_launcher_service.py