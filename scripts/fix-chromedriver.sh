#!/bin/bash

echo "======================================"
echo "🔧 Naprawa ChromeDriver"
echo "======================================"
echo ""

# Przejdź do głównego katalogu projektu
cd "$(dirname "$0")"

echo "📍 Lokalizacja: $(pwd)"
echo ""

# Sprawdź wersję Chrome
echo "1️⃣ Sprawdzanie wersji Chrome..."
if [ -d "/Applications/Google Chrome.app" ]; then
    CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version)
    echo "   Chrome: $CHROME_VERSION"
else
    echo "   ❌ Chrome nie znaleziony"
    exit 1
fi
echo ""

# Sprawdź czy istnieje stary ChromeDriver
echo "2️⃣ Sprawdzanie starego ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    OLD_DRIVER=$(which chromedriver)
    OLD_VERSION=$(chromedriver --version 2>/dev/null || echo "Nieznana")
    echo "   Znaleziono: $OLD_DRIVER"
    echo "   Wersja: $OLD_VERSION"
    
    read -p "   Usunąć stary ChromeDriver? (t/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Tt]$ ]]; then
        echo "   Usuwanie starego ChromeDriver..."
        sudo rm "$OLD_DRIVER"
        echo "   ✅ Usunięto"
    fi
else
    echo "   Brak starego ChromeDriver w systemie"
fi
echo ""

# Aktywuj venv i zainstaluj zależności
echo "3️⃣ Aktualizacja zależności..."
if [ ! -d "venv" ]; then
    echo "   Tworzenie środowiska wirtualnego..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "   Instalacja webdriver-manager..."
pip install --quiet webdriver-manager==4.0.1

echo "   Aktualizacja wszystkich zależności..."
pip install --quiet -r requirements.txt

echo "   ✅ Zależności zaktualizowane"
echo ""

# Zastąp base_extractor.py
echo "4️⃣ Aktualizacja base_extractor.py..."
if [ -f "base_extractor.py" ]; then
    cp base_extractor.py src/extractors/base_extractor.py
    echo "   ✅ Plik zaktualizowany"
else
    echo "   ⚠️  Nowy base_extractor.py nie znaleziony - pomiń ten krok"
fi
echo ""

# Test połączenia
echo "5️⃣ Test automatycznego pobierania ChromeDriver..."
python3 -c "
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

print('   Pobieranie odpowiedniej wersji ChromeDriver...')
driver_path = ChromeDriverManager().install()
print(f'   ✅ ChromeDriver zainstalowany: {driver_path}')

# Sprawdź wersję
import subprocess
result = subprocess.run([driver_path, '--version'], capture_output=True, text=True)
print(f'   Wersja: {result.stdout.strip()}')
" 2>&1 | grep -v "WARNING"

echo ""
echo "======================================"
echo "✅ Naprawa zakończona!"
echo "======================================"
echo ""
echo "Możesz teraz uruchomić aplikację:"
echo "  cd scripts && ./start.sh"
echo ""
echo "Lub kliknij dwukrotnie na:"
echo "  Order Automation Manager.app"
echo ""