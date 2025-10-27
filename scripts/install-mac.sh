#!/bin/bash

echo "=========================================="
echo "Order Automation Manager - Instalacja"
echo "=========================================="
echo ""

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo "Instalacja Python przez Homebrew..."
    
    # Sprawdź czy Homebrew jest zainstalowany
    if ! command -v brew &> /dev/null; then
        echo "Instalacja Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    brew install python3
fi

echo "✅ Python 3 zainstalowany"
echo ""

# Sprawdź czy Chrome jest zainstalowany
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo "⚠️  Google Chrome nie jest zainstalowany!"
    echo "Otwierając stronę do pobrania Chrome..."
    open "https://www.google.com/chrome/"
    echo ""
    echo "Po zainstalowaniu Chrome, uruchom ten skrypt ponownie."
    exit 1
fi

echo "✅ Google Chrome zainstalowany"
echo ""

# Utwórz środowisko wirtualne
echo "Tworzenie środowiska wirtualnego..."
python3 -m venv venv

# Aktywuj środowisko
source venv/bin/activate

# Instaluj zależności
echo "Instalacja zależności..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Instalacja zakończona pomyślnie!"
echo "=========================================="
echo ""
echo "Aby uruchomić aplikację, użyj:"
echo "  ./start.sh"
echo ""