# Description

Luna is a asistant/buddy. The main objective of this project is to create working Ai buddy to help in everyday life

# Features:
- A Desktop aplication created in Electron/Tauri
- Luna can see user screen and coment it or help during a task
-  

# Requiremensts

- Python 3.10+
- Ollama running
- A downloaded model:
  - llama3.1 or llama3.1:8b

## Backend

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

## Frontend

run `Frontend/index.html` in a browser (ctrl + F5)

## Personalization

`Backend/personality.json` - personality

- After changing the personality reset backend
