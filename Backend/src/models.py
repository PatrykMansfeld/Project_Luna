from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class ChatMessage(BaseModel):
    """Pojedyncza wiadomość z rolą i treścią."""
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    """Dane wysyłane przez klienta dla tury rozmowy."""
    session_id: str = Field(..., min_length=3, max_length=64)
    user_message: str = Field(..., min_length=1, max_length=8000)
    persona_id: Optional[str] = Field(default=None, min_length=1, max_length=64)

class ChatResponse(BaseModel):
    """Dane zwracane do klienta z odpowiedzią."""
    session_id: str
    bot_name: str
    reply: str

class OllamaResponse(BaseModel):
    """Struktura odpowiedzi z endpointu zdrowia."""
    status: str
    model: str
    base_url: str

class PersonaInfo(BaseModel):
    """Publiczne informacje o personie widoczne dla frontu."""
    id: str
    name: str
    blurb: str

class PersonasResponse(BaseModel):
    """Lista dostępnych person."""
    personas: List[PersonaInfo]
