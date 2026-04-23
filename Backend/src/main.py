import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_TURNS_MEMORY, CORS_ORIGINS
from .database import init_db
from .models import (
    ChatRequest, ChatResponse, OllamaResponse, ChatMessage,
    PersonaInfo, PersonasResponse,
    SessionInfo, SessionsResponse, SessionMessagesResponse,
)
from .client import OllamaClient
from .personality import load_persona, build_system_prompt
from .memory import MemoryStore, UserFactsStore


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
user_facts = UserFactsStore()
ollama = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)


async def _generate_title(session_id: str, user_message: str, reply: str) -> None:
    try:
        prompt = (
            "Generate a short conversation title (3-6 words) based on this exchange.\n"
            f"User: {user_message[:200]}\nAssistant: {reply[:200]}\n"
            "Reply with ONLY the title, no quotes, no explanation."
        )
        title = await ollama.chat([ChatMessage(role="user", content=prompt)])
        title = title.strip().strip("\"'")[:128]
        if title:
            await memory.set_title(session_id, title)
    except Exception:
        pass


async def _extract_facts(user_message: str, reply: str) -> None:
    try:
        prompt = (
            "Extract personal facts about the user from this exchange. "
            "Reply ONLY with a JSON array like: [{\"key\": \"name\", \"value\": \"Anna\"}]\n"
            "Only include clear, specific facts (name, age, city, job, hobbies, etc). "
            "If nothing to extract, reply with: []\n\n"
            f"User: {user_message[:300]}\nAssistant: {reply[:200]}"
        )
        result = await ollama.chat([ChatMessage(role="user", content=prompt)])
        match = re.search(r"\[.*?\]", result, re.DOTALL)
        if match:
            facts = json.loads(match.group())
            for fact in facts:
                if isinstance(fact, dict) and "key" in fact and "value" in fact:
                    await user_facts.upsert(str(fact["key"])[:128], str(fact["value"]))
    except Exception:
        pass


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


@app.post("/chat")
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
    user_ctx = await user_facts.format_for_prompt()
    if user_ctx:
        system_prompt = system_prompt + "\n\n" + user_ctx

    history = await memory.get(req.session_id)
    if not history or history[0].role != "system":
        await memory.set_system(
            req.session_id,
            ChatMessage(role="system", content=system_prompt),
            persona_id=persona_id,
        )

    await memory.append(
        req.session_id,
        ChatMessage(role="user", content=req.user_message),
        persona_id=persona_id,
    )

    history = await memory.get(req.session_id)
    user_msg_count = sum(1 for m in history if m.role == "user")
    is_first_exchange = user_msg_count == 1

    async def generate():
        parts: list[str] = []

        try:
            async for token in ollama.stream_chat(history):
                parts.append(token)
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"
            return

        full_reply = "".join(parts)
        await memory.append(
            req.session_id,
            ChatMessage(role="assistant", content=full_reply),
            persona_id=persona_id,
        )

        if is_first_exchange:
            asyncio.create_task(_generate_title(req.session_id, req.user_message, full_reply))
        asyncio.create_task(_extract_facts(req.user_message, full_reply))

        yield f"data: {json.dumps({'type': 'done', 'session_id': req.session_id, 'bot_name': bot_name})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/reset/{session_id}")
async def reset(session_id: str):
    await memory.reset(session_id)
    return {"status": "ok", "session_id": session_id}
