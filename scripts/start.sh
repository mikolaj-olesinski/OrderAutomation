#!/bin/bash

echo "=========================================="
echo "Order Automation Manager"
echo "=========================================="
echo ""

# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom aplikację
cd src
python app.py