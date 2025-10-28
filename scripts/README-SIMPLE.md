# Order Automation Manager

## 🚀 Instalacja (tylko pierwszy raz)

### Opcja 1: Aplikacja (POLECANE) - po prostu klikaj

1. **Otwórz Terminal** (Cmd + Spacja → wpisz "Terminal")
2. **Przeciągnij folder aplikacji** na okno Terminal i naciśnij Enter
3. chmod +x scripts/*.sh

{
  "chrome_path": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "chrome_user_data_dir": "/Users/mikolajolesinski/chrome-debug-profile",
  ...
}

4. rm -rf ~/.wdm/drivers/chromedriver
5. **Wpisz:**
   ```bash
   chmod +x create-app.sh && ./create-app.sh
   ```
6. **Gotowe!** Teraz masz aplikację **"Order Automation Manager.app"**


### Jak używać aplikacji?

Po prostu **kliknij dwukrotnie** na **"Order Automation Manager.app"**

- Przy pierwszym uruchomieniu zainstaluje się automatycznie
- Otworzy się Terminal z aplikacją
- Automatycznie otworzy się przeglądarka na http://127.0.0.1:5000

### Opcja 2: Przez Terminal (jeśli wolisz)

1. **Otwórz Terminal**
2. **Przejdź do folderu:**
   ```bash
   cd ścieżka/do/folderu
   ```
3. **Instalacja (tylko raz):**
   ```bash
   chmod +x install-mac.sh && ./install-mac.sh
   ```
4. **Uruchomienie (za każdym razem):**
   ```bash
   ./start.sh
   ```

---

## 📖 Pierwsze użycie

1. **Uruchom aplikację** (kliknij dwukrotnie lub przez Terminal)
2. **W przeglądarce** otwórz: http://127.0.0.1:5000
3. **Kliknij "Launch Chrome"** - otworzy się Chrome z dwiema zakładkami
4. **Zaloguj się** na BaseLinker i B2B Hendi
5. **Gotowe!** Teraz możesz używać "Extract & Import to B2B"

---

## 🎯 Codzienne użycie

1. **Kliknij dwukrotnie** na "Order Automation Manager.app"
2. **Poczekaj** aż otworzy się przeglądarka
3. **Kliknij "Launch Chrome"** (jeśli Chrome nie jest jeszcze uruchomiony)
4. **Użyj "Extract & Import to B2B"**

---

## ⚠️ Ważne

- **Zawsze uruchamiaj Chrome przez aplikację** (przycisk "Launch Chrome")
- **Nie zamykaj okna Terminal** gdy aplikacja działa
- Aby zatrzymać aplikację: naciśnij **Ctrl+C** w oknie Terminal

---

## 🆘 Problemy?

### "Cannot be opened because it is from an unidentified developer"

1. Prawy klik na aplikację → "Open"
2. Kliknij "Open" w oknie dialogowym
3. Lub: System Preferences → Security → "Open Anyway"

### Aplikacja nie uruchamia się

W Terminal:
```bash
chmod +x create-app.sh && ./create-app.sh
```

### Chrome się nie łączy

- Zamknij **wszystkie** okna Chrome
- Kliknij "Launch Chrome" w aplikacji ponownie

---

## 📝 Uwagi

- Pierwsza instalacja może potrwać kilka minut
- Potrzebujesz połączenia z internetem przy instalacji
- Google Chrome musi być zainstalowany