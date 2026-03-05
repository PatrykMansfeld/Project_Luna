import httpx
from typing import List
from .models import ChatMessage
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """Tworzy klienta dla API rozmów Ollamy."""
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(self, messages: List[ChatMessage]) -> str:
        """Wysyła historię rozmowy do Ollamy i zwraca odpowiedź asystenta."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": False
        }

        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

        # Ollama zwykle zwraca { message: { role, content }, ... }
        msg = data.get("message", {})
        content = msg.get("content", "")
        return content.strip()
