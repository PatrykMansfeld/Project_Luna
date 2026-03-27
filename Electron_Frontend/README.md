# Electron Frontend

Aplikacja desktopowa chatbota Ollama.

## Struktura folderów

```
Electron_Frontend/
├── src/              # Kod główny Electrona (main process)
│   └── main.js       # Główny plik Electrona
├── renderer/         # Interfejs użytkownika (renderer process)
│   ├── index.html    # HTML aplikacji
│   ├── app.js        # Logika frontendu
│   └── styles.css    # Style CSS
├── package.json      # Konfiguracja npm
└── .gitignore        # Pliki ignorowane przez git
```

## Instalacja

```bash
cd Electron_Frontend
npm install
```

## Uruchomienie

```bash
npm start
```

## Wymagania

- Node.js 16+
- Backend uruchomiony na `http://127.0.0.1:8000`
- Ollama z załadowanym modelem

## Konfiguracja

### Content Security Policy (CSP)

CSP w `renderer/index.html` jest skonfigurowane do:
- Łączenia z backendem na `http://127.0.0.1:8000` i `http://localhost:8000`
- Ładowania czcionek z Google Fonts
- Wykonywania inline scripts i styles (dla dynamicznego contentu)

### Połączenie z backendem

API endpoint jest ustawiony w `renderer/app.js`:
```javascript
const API = "http://127.0.0.1:8000";
```

## Funcjonalności

- ✅ Wybór persony z listy
- ✅ Chat z wybraną personą
- ✅ Tryb jasny/ciemny
- ✅ Reset rozmowy
- ✅ Zmiana persony podczas rozmowy
- ✅ Pełne menu aplikacji (Plik, Edycja, Widok)
- ✅ Skróty klawiszowe
