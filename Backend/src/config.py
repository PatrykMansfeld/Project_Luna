import os
from dotenv import load_dotenv

load_dotenv()  # Wczytaj zmienne środowiskowe z pliku .env


def _get_int(name: str, default: int) -> int:
	"""Czyta zmienną środowiskową typu int z bezpieczną wartością domyślną."""
	value = os.getenv(name)
	if value is None or value == "":
		return default
	try:
		return int(value)
	except ValueError:
		return default


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
MAX_TURNS_MEMORY = _get_int("MAX_TURNS_MEMORY", 18)

# Nazwy kompatybilne wstecz, jeśli są używane w innych miejscach
AI_MODEL_URL = os.getenv("AI_MODEL_URL", OLLAMA_BASE_URL)
AI_MODEL = os.getenv("AI_MODEL", OLLAMA_MODEL)
MAX_TURNS = _get_int("MAX_TURNS", MAX_TURNS_MEMORY)
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = _get_int("APP_PORT", 8000)