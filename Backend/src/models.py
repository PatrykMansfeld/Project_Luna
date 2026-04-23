from pydantic import BaseModel, Field
from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=3, max_length=64)
    user_message: str = Field(..., min_length=1, max_length=8000)
    persona_id: str | None = Field(default=None, min_length=1, max_length=64)


class ChatResponse(BaseModel):
    session_id: str
    bot_name: str
    reply: str


class OllamaResponse(BaseModel):
    status: str
    model: str
    base_url: str


class PersonaInfo(BaseModel):
    id: str
    name: str
    blurb: str


class PersonasResponse(BaseModel):
    personas: list[PersonaInfo]


class SessionInfo(BaseModel):
    id: str
    persona_id: str
    message_count: int
    updated_at: str


class SessionsResponse(BaseModel):
    sessions: list[SessionInfo]


class SessionMessagesResponse(BaseModel):
    session_id: str
    persona_id: str
    messages: list[ChatMessage]
