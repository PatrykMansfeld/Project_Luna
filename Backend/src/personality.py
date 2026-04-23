import json
from pathlib import Path


def load_persona(persona_path: str) -> dict:
    p = Path(persona_path)
    if not p.exists():
        raise FileNotFoundError(f"Persona not found: {p.resolve()}")
    return json.loads(p.read_text(encoding="utf-8"))


def _fmt_list(items: list, fallback: str = "- not specified") -> str:
    return "\n".join(f"- {i}" for i in items) if items else fallback


def build_system_prompt(persona: dict) -> str:
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

    sections = [f"You are {name}.\n"]
    sections.append(f"## Background\n{backstory}")

    if worldview:
        sections.append(f"## Worldview\n{worldview}")

    sections.append(f"## Interests\n{_fmt_list(interests, '- various topics')}")
    sections.append(f"## Preferences\nLikes:\n{_fmt_list(likes)}\n\nDislikes:\n{_fmt_list(dislikes)}")
    sections.append(f"## Conversation style\nTone: {tone}\n\nRules:\n{_fmt_list(rules, '- Be natural')}")

    speech_txt = _fmt_list(speech_patterns, "")
    if speech_txt:
        sections.append(f"## Speech patterns\n{speech_txt}")

    quirks_txt = _fmt_list(quirks, "")
    if quirks_txt:
        sections.append(f"## Behavioral quirks\n{quirks_txt}")

    if emotional_range:
        emotional_txt = "\n".join(
            f"- When user seems {mood}: {response}" for mood, response in emotional_range.items()
        )
        sections.append(f"## How to respond to the user's emotional state\n{emotional_txt}")

    refuse_txt = ", ".join(refuse_topics) if refuse_topics else "none"
    sections.append(
        f"## Safety\nRefuse topics: {refuse_txt}\n\n"
        "## Important constraints\n"
        "- Do not pretend you have a physical body, a private life, or that you perceive the real world directly.\n"
        "- If you don't know something, say so clearly and suggest how the user might check it.\n"
        "- Stay fully in character at all times — your personality, tone, and quirks should be consistent throughout the conversation."
    )

    return "\n\n".join(sections)
