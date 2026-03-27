# Description

Zori is a chatbot designed to entertain users daily with wide range of topics and avaliable personas to choose from.

# Requiremensts

## Backend
- Python 3.10+
- Ollama running
- A downloaded model:
  - llama3.1 or llama3.1:8b

## Frontend
- **Web:** Dowolna przeglądarka (Safari, Opera GX, Chrome, Firefox)
- **Electron:** Node.js 16+

## Backend Setup

Create a venv and install dependencies:

- `python -m venv .venv`
- Windows: `.venv\Scripts\activate`
- mac/linux: `source .venv/bin/activate`
- `pip install -r requirements.txt`

Run:

- Windows:
  `uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload`

- mac/linux:
  `OLLAMA_MODEL=llama3.1 uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload`

### Electron Frontend (Desktop App)

Zainstaluj i uruchom aplikację desktopową:

```bash
cd Electron_Frontend
npm install
npm start
```

**Wymagania:** Node.js 16+

**Struktura:**
- `src/` - główny proces Electrona
- `renderer/` - interfejs użytkownika (HTML/CSS/JS)

**Uwaga:** Backend musi działać przed uruchomieniem frontendu!

## Personalization

`Backend/personality.json` - personality

- After changing the personality reset backend
