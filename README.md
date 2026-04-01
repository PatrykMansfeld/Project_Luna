# Project Luna

A local AI chat assistant with swappable personas, powered by [Ollama](https://ollama.com). Talk to **Luna**, **Zori**, or any persona you define — all running entirely on your machine.

## Architecture

```
Vue 3 + Vite (:5173)  →  Go API gateway (:3000)  →  FastAPI (:8000)  →  Ollama
```

- **Frontend** — Vue 3 + Vite chat UI
- **API gateway** — Go reverse proxy; single entry point for the frontend
- **Backend** — Python FastAPI; handles persona logic, conversation memory, and Ollama calls
- **Ollama** — local LLM inference (runs separately)

## Requirements

- [Ollama](https://ollama.com) installed and running
- A downloaded model, e.g. `ollama pull gemma3:27b`
- Python 3.10+
- Go 1.22+
- Node.js 18+

## Setup

### 1. Environment variables (optional)

Copy the example and adjust as needed:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:27b
MAX_TURNS_MEMORY=18

BACKEND_URL=http://127.0.0.1:8000
API_ADDR=:3000
```

Create a `.env` file in `Backend/` for Python variables and set Go variables in your shell or a startup script.

### 2. Backend (Python / FastAPI)

```bash
cd Backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. API gateway (Go)

```bash
cd API
go run .
```

The gateway listens on `:3000` by default and proxies all requests to the FastAPI backend.

### 4. Frontend (Vue + Vite)

```bash
cd Frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Personas

Personas are defined as JSON files in `Backend/personas/`. Each file is picked up automatically on startup — no code changes needed.

```
Backend/personas/
├── Luna.json   — sociable, curious, laid-back
└── Zori.json   — ...
```

To add a new persona, create a new `.json` file in that folder following the same structure, then restart the backend.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Go gateway health check |
| `GET` | `/ollama` | Ollama connection status and active model |
| `GET` | `/personas` | List available personas |
| `POST` | `/chat` | Send a message and receive a reply |
| `POST` | `/reset/{sessionID}` | Clear conversation history for a session |

> **Note:** CORS is currently set to `allow_origins=["*"]`. This is fine for local development but should be restricted before any public deployment.
