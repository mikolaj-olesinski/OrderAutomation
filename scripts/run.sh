#!/bin/bash

cd "$(dirname "$0")/.."

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting application..."
echo "Open http://127.0.0.1:5000 in your browser"
echo ""

cd src
python app.py