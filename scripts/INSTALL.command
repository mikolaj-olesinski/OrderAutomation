#!/bin/bash

# Ten plik można kliknąć dwukrotnie aby zainstalować wszystko

# Przejdź do folderu ze skryptem
cd "$(dirname "$0")"

echo "=========================================="
echo "Order Automation Manager"
echo "Automatyczna instalacja"
echo "=========================================="
echo ""

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo ""
    echo "Instalacja Python przez Homebrew..."
    echo ""
    
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
    echo ""
    echo "Otwierając stronę do pobrania Chrome..."
    open "https://www.google.com/chrome/"
    echo ""
    echo "Po zainstalowaniu Chrome, uruchom ten skrypt ponownie."
    echo ""
    read -p "Naciśnij Enter aby zakończyć..."
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
echo "✅ Instalacja zakończona!"
echo "=========================================="
echo ""
echo "Tworzenie aplikacji..."
echo ""

# Utwórz aplikację
chmod +x create-app.sh
./create-app.sh

echo ""
echo "=========================================="
echo "🎉 GOTOWE!"
echo "=========================================="
echo ""
echo "Aplikacja 'Order Automation Manager.app' jest gotowa!"
echo ""
echo "Teraz możesz:"
echo "1. Kliknąć dwukrotnie na 'Order Automation Manager.app'"
echo "2. Opcjonalnie: przeciągnąć ją do folderu Applications"
echo ""
echo "Przy pierwszym uruchomieniu może pojawić się"
echo "ostrzeżenie bezpieczeństwa - kliknij 'Open'"
echo ""
read -p "Naciśnij Enter aby zakończyć..."