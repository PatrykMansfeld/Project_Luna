import httpx
from .models import ChatMessage


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def chat(self, messages: list[ChatMessage]) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

        msg = data.get("message", {})
        return msg.get("content", "").strip()
