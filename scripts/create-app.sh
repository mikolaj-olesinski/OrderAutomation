#!/bin/bash

# Skrypt do utworzenia aplikacji macOS (.app)

APP_NAME="Order Automation Manager"
APP_DIR="$APP_NAME.app"

echo "Tworzenie aplikacji macOS: $APP_NAME"
echo ""

# Utwórz strukturę .app
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Utwórz Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.orderautomation.app</string>
    <key>CFBundleName</key>
    <string>Order Automation Manager</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Utwórz główny launcher script
cat > "$APP_DIR/Contents/MacOS/launcher" << 'EOF'
#!/bin/bash

# Pobierz ścieżkę do aplikacji
APP_PATH="$(cd "$(dirname "$0")/../../.."; pwd)"
cd "$APP_PATH"

# Sprawdź czy venv istnieje, jeśli nie - uruchom instalację
if [ ! -d "venv" ]; then
    # Otwórz Terminal z instalacją
    osascript <<APPLESCRIPT
tell application "Terminal"
    do script "cd '$APP_PATH' && chmod +x install-mac.sh && ./install-mac.sh && echo '' && echo 'Instalacja zakończona! Zamknij to okno i uruchom aplikację ponownie.' && read -p 'Naciśnij Enter...'"
    activate
end tell
APPLESCRIPT
    exit 0
fi

# Uruchom aplikację w nowym oknie Terminal
osascript <<APPLESCRIPT
tell application "Terminal"
    do script "cd '$APP_PATH' && source venv/bin/activate && cd src && python app.py"
    activate
end tell
APPLESCRIPT

# Poczekaj chwilę, żeby serwer się uruchomił
sleep 3

# Otwórz przeglądarkę
open "http://127.0.0.1:5000"
EOF

chmod +x "$APP_DIR/Contents/MacOS/launcher"

# Utwórz prostą ikonę (opcjonalnie - możesz dodać własną)
# Dla prostoty, pomijamy ikonę - macOS użyje domyślnej

echo "✅ Aplikacja utworzona: $APP_DIR"
echo ""
echo "Aby użyć:"
echo "1. Przenieś '$APP_DIR' do folderu Applications (opcjonalnie)"
echo "2. Kliknij dwukrotnie aby uruchomić"
echo ""
echo "Przy pierwszym uruchomieniu zostanie przeprowadzona instalacja."
echo ""