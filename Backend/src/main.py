from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from.config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_TURNS_MEMORY
from.models import ChatRequest, ChatResponse, OllamaResponse, ChatMessage, PersonaInfo, PersonasResponse
from.client import OllamaClient
from.personality import load_persona, build_system_prompt
from.memory import MemoryStore

app = FastAPI(title="Ollama Persona Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # na dev ok, potem możesz zawęzić
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend_root = Path(__file__).resolve().parents[1]
personas_dir = backend_root / "personas"

personas_map: Dict[str, dict] = {}
personas_list = []
for persona_path in sorted(personas_dir.glob("*.json")):
    try:
        data = load_persona(str(persona_path))
    except Exception:
        continue
    persona_id = persona_path.stem
    name = data.get("name", persona_id)
    backstory = data.get("backstory", "")
    blurb = backstory.split(".")[0].strip() if backstory else ""
    personas_map[persona_id] = data
    personas_list.append(PersonaInfo(id=persona_id, name=name, blurb=blurb))

default_persona_id: Optional[str] = personas_list[0].id if personas_list else None
session_persona: Dict[str, str] = {}

memory = MemoryStore(max_turns=MAX_TURNS_MEMORY)
ollama = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

@app.get("/ollama", response_model=OllamaResponse)
def ollama_status():
    """Zwraca status usługi i aktualne ustawienia Ollamy."""
    return OllamaResponse(status="ok", model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

@app.get("/personas", response_model=PersonasResponse)
def personas():
    """Zwraca listę dostępnych person do wyboru."""
    return PersonasResponse(personas=personas_list)

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Obsługuje turę rozmowy, aktualizuje pamięć i zwraca odpowiedź."""
    persona_id = req.persona_id or session_persona.get(req.session_id) or default_persona_id
    if not persona_id or persona_id not in personas_map:
        raise HTTPException(status_code=400, detail="Nieprawidlowy persona_id")

    if session_persona.get(req.session_id) != persona_id:
        memory.reset(req.session_id)
        session_persona[req.session_id] = persona_id

    persona = personas_map[persona_id]
    bot_name = persona.get("name", "Bot")
    system_prompt = build_system_prompt(persona)

    # upewnij się, że sesja ma system prompt
    if not memory.get(req.session_id) or memory.get(req.session_id)[0].role != "system":
        memory.set_system(req.session_id, ChatMessage(role="system", content=system_prompt))

    # dodaj wiadomość usera
    memory.append(req.session_id, ChatMessage(role="user", content=req.user_message))

    # wyślij do ollamy
    try:
        reply = await ollama.chat(memory.get(req.session_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd rozmowy z Ollama: {str(e)}")

    # zapisz odpowiedź
    memory.append(req.session_id, ChatMessage(role="assistant", content=reply))

    return ChatResponse(session_id=req.session_id, bot_name=bot_name, reply=reply)

# Endpoint do resetowania sesji, np. po zmianie persony
@app.post("/reset/{session_id}")
def reset(session_id: str):
    """Resetuje sesję danej rozmowy."""
    memory.reset(session_id)
    return {"status": "ok", "session_id": session_id}
