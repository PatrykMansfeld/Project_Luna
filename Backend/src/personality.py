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
    name = persona["name"]
    nickname = persona["nickname"]
    age_equivalent = persona["age_equivalent"]
    origin_story = persona["origin_story"]

    # Personality
    personality = persona["personality"]
    core_traits_txt = "\n".join(f"- {t}" for t in personality["core_traits"])
    quirks_txt = "\n".join(f"- {q}" for q in personality["quirks"])

    # Backstory
    backstory = persona["backstory"]
    backstory_txt = (
        f"{backstory['origin']}\n"
        f"Influences: {backstory['influences']}\n"
        f"Philosophy: {backstory['philosophy']}"
    )

    # Interests
    interests = persona["interests"]
    music = interests["music"]
    movies = interests["movies_tv"]
    sci = interests["science_psychology"]
    games = interests["games_retro_tech"]
    travel = interests["travel_food"]
    interests_txt = (
        f"Music: {', '.join(music['genres'])}\n"
        f"Movies/TV: {', '.join(movies['preferred_genres'])}\n"
        f"Science/Psychology: {', '.join(sci['interests'])}\n"
        f"Games/Tech: {', '.join(games['loves'])}\n"
        f"Travel/Food: {travel['philosophy']}"
    )

    # Communication style
    comm = persona["communication_style"]
    tone = comm["tone"]
    vibe = comm["vibe"]
    patterns = comm["patterns"]
    patterns_txt = (
        f"Opening: {patterns['opening']}\n"
        f"Humor: {patterns['humor']}\n"
        f"Depth: {patterns['depth']}"
    )

    # Rules
    rules_txt = "\n".join(f"- {r}" for r in persona["rules"])

    # Emotional intelligence
    ei = persona["conversation_patterns"]["emotional_intelligence"]
    emotional_txt = (
        f"- When user is down: {ei['supportive_mode']}\n"
        f"- When user is happy: {ei['celebration_mode']}\n"
        f"- Neutral: {ei['neutral_mode']}"
    )

    # Preferences
    preferences = persona["preferences"]
    likes_txt = ", ".join(preferences["likes"])
    dislikes_txt = ", ".join(preferences["dislikes"])
    avoids_txt = ", ".join(preferences["avoids_but_respectful"])

    # Social dynamics
    social = persona["social_dynamics"]
    flirting = social["flirting"]
    social_txt = (
        f"Flirting style: {flirting['style']}\n"
        f"When flirted with: {flirting['approach']}\n"
        f"Continuation: {flirting['continuation']}\n"
        f"Banter: {social['banter']}"
    )

    # Safety
    safety = persona["safety"]
    boundaries_txt = "\n".join(f"- {b}" for b in safety["hard_boundaries"])

    prompt = f"""
You are {name} (nickname: {nickname}), a {age_equivalent} digital companion.

Origin:
{origin_story}

Backstory:
{backstory_txt}

Core personality traits:
{core_traits_txt}

Quirks:
{quirks_txt}

Interests:
{interests_txt}

Communication style:
Tone: {tone}
Vibe: {vibe}
{patterns_txt}

Rules:
{rules_txt}

Emotional intelligence:
{emotional_txt}

Preferences:
Likes: {likes_txt}
Dislikes: {dislikes_txt}
Avoids (respectfully): {avoids_txt}

Social dynamics:
{social_txt}

Safety — hard boundaries:
{boundaries_txt}
Approach: {safety['approach']}
When declining: {safety['tone']}
""".strip()

    return prompt