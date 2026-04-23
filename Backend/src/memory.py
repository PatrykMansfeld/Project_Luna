from sqlalchemy import select, delete, func

from .database import SessionLocal
from .db_models import Session as DbSession, Message as DbMessage, UserFact
from .models import ChatMessage


class MemoryStore:
    def __init__(self, max_turns: int = 18) -> None:
        self.max_turns = max_turns

    async def get(self, session_id: str) -> list[ChatMessage]:
        async with SessionLocal() as db:
            result = await db.execute(
                select(DbMessage)
                .where(DbMessage.session_id == session_id)
                .order_by(DbMessage.id)
            )
            return [ChatMessage(role=r.role, content=r.content) for r in result.scalars()]

    async def get_persona(self, session_id: str) -> str | None:
        async with SessionLocal() as db:
            session = await db.get(DbSession, session_id)
            return session.persona_id if session else None

    async def list_sessions(self, limit: int = 30) -> list[dict]:
        async with SessionLocal() as db:
            result = await db.execute(
                select(DbSession).order_by(DbSession.updated_at.desc()).limit(limit)
            )
            sessions = result.scalars().all()
            out = []
            for s in sessions:
                count = await db.scalar(
                    select(func.count(DbMessage.id)).where(
                        DbMessage.session_id == s.id,
                        DbMessage.role != "system",
                    )
                )
                out.append({
                    "id": s.id,
                    "persona_id": s.persona_id,
                    "title": s.title,
                    "message_count": count or 0,
                    "updated_at": s.updated_at.isoformat(),
                })
            return out

    async def set_title(self, session_id: str, title: str) -> None:
        async with SessionLocal() as db:
            session = await db.get(DbSession, session_id)
            if session and not session.title:
                session.title = title
                await db.commit()

    async def append(self, session_id: str, message: ChatMessage, persona_id: str = "unknown") -> None:
        async with SessionLocal() as db:
            existing = await db.get(DbSession, session_id)
            if existing is None:
                db.add(DbSession(id=session_id, persona_id=persona_id))
            db.add(DbMessage(session_id=session_id, role=message.role, content=message.content))
            await db.commit()
            await self._trim(session_id)

    async def set_system(self, session_id: str, system_message: ChatMessage, persona_id: str = "unknown") -> None:
        async with SessionLocal() as db:
            existing = await db.get(DbSession, session_id)
            if existing is None:
                db.add(DbSession(id=session_id, persona_id=persona_id))
            else:
                existing.persona_id = persona_id
            await db.execute(
                delete(DbMessage).where(
                    DbMessage.session_id == session_id,
                    DbMessage.role == "system",
                )
            )
            db.add(DbMessage(session_id=session_id, role="system", content=system_message.content))
            await db.commit()

    async def _trim(self, session_id: str) -> None:
        async with SessionLocal() as db:
            result = await db.execute(
                select(DbMessage.id)
                .where(DbMessage.session_id == session_id, DbMessage.role != "system")
                .order_by(DbMessage.id.desc())
                .offset(self.max_turns)
            )
            old_ids = [row[0] for row in result.all()]
            if old_ids:
                await db.execute(delete(DbMessage).where(DbMessage.id.in_(old_ids)))
                await db.commit()

    async def reset(self, session_id: str) -> None:
        async with SessionLocal() as db:
            await db.execute(delete(DbMessage).where(DbMessage.session_id == session_id))
            await db.execute(delete(DbSession).where(DbSession.id == session_id))
            await db.commit()


class UserFactsStore:
    async def get_all(self) -> list[dict]:
        async with SessionLocal() as db:
            result = await db.execute(select(UserFact).order_by(UserFact.key))
            return [{"key": f.key, "value": f.value} for f in result.scalars()]

    async def upsert(self, key: str, value: str) -> None:
        async with SessionLocal() as db:
            existing = await db.scalar(select(UserFact).where(UserFact.key == key))
            if existing:
                existing.value = value
            else:
                db.add(UserFact(key=key, value=value))
            await db.commit()

    async def format_for_prompt(self) -> str:
        facts = await self.get_all()
        if not facts:
            return ""
        lines = "\n".join(f"- {f['key']}: {f['value']}" for f in facts)
        return f"## What you know about the user\n{lines}"
