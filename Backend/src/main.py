from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_TURNS_MEMORY, CORS_ORIGINS
from .database import init_db
from .models import (
    ChatRequest, ChatResponse, OllamaResponse, ChatMessage,
    PersonaInfo, PersonasResponse,
    SessionInfo, SessionsResponse, SessionMessagesResponse,
)
from .client import OllamaClient
from .personality import load_persona, build_system_prompt
from .memory import MemoryStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Ollama Persona Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend_root = Path(__file__).resolve().parents[1]
personas_dir = backend_root / "personas"

personas_map: dict[str, dict] = {}
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

memory = MemoryStore(max_turns=MAX_TURNS_MEMORY)
ollama = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "fastapi-backend"}


@app.get("/ollama", response_model=OllamaResponse)
async def ollama_status():
    return OllamaResponse(status="ok", model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)


@app.get("/personas", response_model=PersonasResponse)
async def personas():
    return PersonasResponse(personas=personas_list)


@app.get("/sessions", response_model=SessionsResponse)
async def list_sessions():
    sessions = await memory.list_sessions()
    return SessionsResponse(sessions=[SessionInfo(**s) for s in sessions])


@app.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
async def session_messages(session_id: str):
    persona_id = await memory.get_persona(session_id)
    if persona_id is None:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = await memory.get(session_id)
    return SessionMessagesResponse(
        session_id=session_id,
        persona_id=persona_id,
        messages=[m for m in msgs if m.role != "system"],
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    persona_id = req.persona_id or await memory.get_persona(req.session_id) or default_persona_id
    if not persona_id or persona_id not in personas_map:
        raise HTTPException(status_code=400, detail="Nieprawidlowy persona_id")

    current_persona = await memory.get_persona(req.session_id)
    if current_persona != persona_id:
        await memory.reset(req.session_id)

    persona = personas_map[persona_id]
    bot_name = persona.get("name", "Bot")
    system_prompt = build_system_prompt(persona)

    history = await memory.get(req.session_id)
    if not history or history[0].role != "system":
        await memory.set_system(
            req.session_id,
            ChatMessage(role="system", content=system_prompt),
            persona_id=persona_id,
        )

    await memory.append(req.session_id, ChatMessage(role="user", content=req.user_message), persona_id=persona_id)

    try:
        reply = await ollama.chat(await memory.get(req.session_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd rozmowy z Ollama: {str(e)}")

    await memory.append(req.session_id, ChatMessage(role="assistant", content=reply), persona_id=persona_id)

    return ChatResponse(session_id=req.session_id, bot_name=bot_name, reply=reply)


@app.post("/reset/{session_id}")
async def reset(session_id: str):
    await memory.reset(session_id)
    return {"status": "ok", "session_id": session_id}
