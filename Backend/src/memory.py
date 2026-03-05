from typing import Dict, List
from .models import ChatMessage

class MemoryStore:
    def __init__(self, max_turns: int = 18):
        """Inicjalizuje magazyn w pamięci i limit historii."""
        self.max_turns = max_turns
        self._sessions: Dict[str, List[ChatMessage]] = {}

    def get(self, session_id: str) -> List[ChatMessage]:
        """Zwraca historię wiadomości dla sesji (lub pustą listę)."""
        return self._sessions.get(session_id, [])

    def append(self, session_id: str, message: ChatMessage) -> None:
        """Dodaje wiadomość do sesji i pilnuje limitu historii."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(message)
        self._trim(session_id)

    def set_system(self, session_id: str, system_message: ChatMessage) -> None:
        """Ustawia lub podmienia wiadomość systemową na początku sesji."""
        history = self._sessions.get(session_id, [])
        history = [m for m in history if m.role != "system"]
        self._sessions[session_id] = [system_message] + history
        self._trim(session_id)

    def _trim(self, session_id: str) -> None:
        """Zostawia tylko najnowsze tury bez wiadomości systemowych."""
        history = self._sessions.get(session_id, [])
        if not history:
            return

        system = [m for m in history if m.role == "system"]
        rest = [m for m in history if m.role != "system"]

        # max_turns dotyczy całej historii bez system, liczymy wiadomości user+assistant
        if len(rest) > self.max_turns:
            rest = rest[-self.max_turns:]

        self._sessions[session_id] = (system[:1] + rest) if system else rest

    def reset(self, session_id: str) -> None:
        """Usuwa całą historię dla danej sesji."""
        if session_id in self._sessions:
            del self._sessions[session_id]
