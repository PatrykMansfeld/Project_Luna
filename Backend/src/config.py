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

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = _get_int("APP_PORT", 8000)

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:5173").split(",")
    if o.strip()
]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://luna:luna_dev@localhost:5432/luna",
)