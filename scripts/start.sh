#!/bin/bash

echo "=========================================="
echo "Order Automation Manager"
echo "=========================================="
echo ""

# Przejdź do głównego katalogu projektu (jeden poziom wyżej od scripts/)
cd "$(dirname "$0")/.."

# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom aplikację
cd src
python app.py