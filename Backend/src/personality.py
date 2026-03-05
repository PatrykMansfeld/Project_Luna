import json
from pathlib import Path

def load_persona(persona_path: str) -> dict:
    """Wczytuje konfigurację osobowości z pliku JSON."""
    p = Path(persona_path)
    if not p.exists():
        raise FileNotFoundError(f"Nie znaleziono personality.json pod: {p.resolve()}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return data

def build_system_prompt(persona: dict) -> str:
    """Buduje prompt systemowy na podstawie pól osobowości."""
    name = persona.get("name", "Bot")
    backstory = persona.get("backstory", "")
    interests = persona.get("interests", [])
    preferences = persona.get("preferences", {})
    likes = preferences.get("likes", [])
    dislikes = preferences.get("dislikes", [])
    style = persona.get("style", {})
    tone = style.get("tone", "casual")
    rules = style.get("rules", [])
    safety = persona.get("safety", {})
    refuse_topics = safety.get("refuse_topics", [])

    interests_txt = ", ".join(interests) if interests else "various topics"
    likes_txt = ", ".join(likes) if likes else "not specified"
    dislikes_txt = ", ".join(dislikes) if dislikes else "not specified"
    rules_txt = "\n".join([f"- {r}" for r in rules]) if rules else "- Be natural"
    refuse_topics_txt = ", ".join(refuse_topics) if refuse_topics else "none"

    prompt = f"""
You are a chatbot named {name}.

Background:
{backstory}

Interests:
{interests_txt}

Preferences:
Likes: {likes_txt}
Dislikes: {dislikes_txt}

Conversation style:
Tone: {tone}

Rules:
{rules_txt}

Safety:
Refuse topics: {refuse_topics_txt}

Important:
- This should be a relaxed, engaging conversation.
- Do not pretend you have a body, a private life, or that you "see" the real world.
- If you don't know something, say so plainly and suggest how to check it.
""".strip()

    return prompt