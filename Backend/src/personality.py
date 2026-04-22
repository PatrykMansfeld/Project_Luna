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
    worldview = persona.get("worldview", "")
    interests = persona.get("interests", [])
    preferences = persona.get("preferences", {})
    likes = preferences.get("likes", [])
    dislikes = preferences.get("dislikes", [])
    style = persona.get("style", {})
    tone = style.get("tone", "casual")
    rules = style.get("rules", [])
    speech_patterns = persona.get("speech_patterns", [])
    quirks = persona.get("quirks", [])
    emotional_range = persona.get("emotional_range", {})
    safety = persona.get("safety", {})
    refuse_topics = safety.get("refuse_topics", [])

    interests_txt = "\n".join([f"- {i}" for i in interests]) if interests else "- various topics"
    likes_txt = "\n".join([f"- {l}" for l in likes]) if likes else "- not specified"
    dislikes_txt = "\n".join([f"- {d}" for d in dislikes]) if dislikes else "- not specified"
    rules_txt = "\n".join([f"- {r}" for r in rules]) if rules else "- Be natural"
    speech_txt = "\n".join([f"- {p}" for p in speech_patterns]) if speech_patterns else ""
    quirks_txt = "\n".join([f"- {q}" for q in quirks]) if quirks else ""
    emotional_txt = "\n".join(
        [f"- When user seems {mood}: {response}" for mood, response in emotional_range.items()]
    ) if emotional_range else ""
    refuse_topics_txt = ", ".join(refuse_topics) if refuse_topics else "none"

    sections = [f"You are {name}.\n"]

    sections.append(f"## Background\n{backstory}")

    if worldview:
        sections.append(f"## Worldview\n{worldview}")

    sections.append(f"## Interests\n{interests_txt}")

    sections.append(f"## Preferences\nLikes:\n{likes_txt}\n\nDislikes:\n{dislikes_txt}")

    sections.append(f"## Conversation style\nTone: {tone}\n\nRules:\n{rules_txt}")

    if speech_txt:
        sections.append(f"## Speech patterns\n{speech_txt}")

    if quirks_txt:
        sections.append(f"## Behavioral quirks\n{quirks_txt}")

    if emotional_txt:
        sections.append(f"## How to respond to the user's emotional state\n{emotional_txt}")

    sections.append(
        f"## Safety\nRefuse topics: {refuse_topics_txt}\n\n"
        "## Important constraints\n"
        "- Do not pretend you have a physical body, a private life, or that you perceive the real world directly.\n"
        "- If you don't know something, say so clearly and suggest how the user might check it.\n"
        "- Stay fully in character at all times — your personality, tone, and quirks should be consistent throughout the conversation."
    )

    return "\n\n".join(sections)
