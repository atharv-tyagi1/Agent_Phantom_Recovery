import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import redis.asyncio as aioredis
from sqlalchemy.orm import Session

from core.config import settings
from db.models.memory import ProjectMemory, ExperienceMemory

logger = logging.getLogger(__name__)

# TTLs for Redis-backed memory tiers
WORKING_MEMORY_TTL = 60 * 60          # 1 hour  — active execution scratchpad
SESSION_MEMORY_TTL = 60 * 60 * 24    # 24 hours — full task session log


class MemoryManager:
    """
    Unified interface for all four memory tiers:

      Working Memory  → Redis  (volatile, per-execution scratchpad)
      Session Memory  → Redis  (ordered event log for an execution session)
      Project Memory  → PostgreSQL (persistent project facts)
      Experience Memory → PostgreSQL (cross-project reusable patterns)
    """

    def __init__(self, redis_url: Optional[str] = None):
        url = redis_url or settings.REDIS_URL
        self._redis: aioredis.Redis = aioredis.from_url(url, decode_responses=True)
        self._local_working: Dict[str, Dict[str, Any]] = {}
        self._local_session: Dict[str, List[Dict[str, Any]]] = {}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _working_key(self, execution_id: str, key: str) -> str:
        return f"wm:{execution_id}:{key}"

    def _session_key(self, execution_id: str) -> str:
        return f"sm:{execution_id}"

    # ── Working Memory ─────────────────────────────────────────────────────────

    async def set_working(self, execution_id: str, key: str, value: Any) -> None:
        """Store a single working-memory entry for the current execution step."""
        try:
            redis_key = self._working_key(execution_id, key)
            await self._redis.set(redis_key, json.dumps(value), ex=WORKING_MEMORY_TTL)
        except Exception as e:
            logger.debug(f"[WorkingMem] Redis fallback for {execution_id}/{key}: {e}")
            if execution_id not in self._local_working:
                self._local_working[execution_id] = {}
            self._local_working[execution_id][key] = value

    async def get_working(self, execution_id: str, key: str) -> Optional[Any]:
        """Retrieve a single working-memory value by key."""
        try:
            redis_key = self._working_key(execution_id, key)
            raw = await self._redis.get(redis_key)
            return json.loads(raw) if raw is not None else None
        except Exception:
            return self._local_working.get(execution_id, {}).get(key)

    async def clear_working(self, execution_id: str) -> None:
        """Clear all working memory for an execution (called at step boundary)."""
        try:
            pattern = f"wm:{execution_id}:*"
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
        except Exception:
            self._local_working.pop(execution_id, None)

    # ── Session Memory ─────────────────────────────────────────────────────────

    async def append_session(self, execution_id: str, event: Dict[str, Any]) -> None:
        """
        Append a timestamped event to the session log for an execution.
        """
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        try:
            redis_key = self._session_key(execution_id)
            await self._redis.rpush(redis_key, json.dumps(event))
            await self._redis.expire(redis_key, SESSION_MEMORY_TTL)
        except Exception as e:
            logger.debug(f"[SessionMem] Redis fallback for {execution_id}: {e}")
            if execution_id not in self._local_session:
                self._local_session[execution_id] = []
            self._local_session[execution_id].append(event)

    async def get_session(self, execution_id: str) -> List[Dict[str, Any]]:
        """Retrieve the full ordered event log for the session."""
        try:
            redis_key = self._session_key(execution_id)
            raw_events = await self._redis.lrange(redis_key, 0, -1)
            return [json.loads(e) for e in raw_events]
        except Exception:
            return self._local_session.get(execution_id, [])

    async def get_session_summary(self, execution_id: str, last_n: int = 10) -> List[Dict[str, Any]]:
        """Retrieve only the last N events — efficient context window for LLM prompts."""
        try:
            redis_key = self._session_key(execution_id)
            raw_events = await self._redis.lrange(redis_key, -last_n, -1)
            return [json.loads(e) for e in raw_events]
        except Exception:
            events = self._local_session.get(execution_id, [])
            return events[-last_n:] if events else []

    # ── Project Memory ─────────────────────────────────────────────────────────

    def set_project_fact(self, db: Session, project_id: str, key: str, value: str, context: Optional[Dict] = None) -> ProjectMemory:
        """
        Store or update a project-level fact. Uses upsert semantics —
        if the key already exists for this project, update the value.
        """
        existing = db.query(ProjectMemory).filter(
            ProjectMemory.project_id == project_id,
            ProjectMemory.key == key
        ).first()

        if existing:
            existing.value = value
            existing.context = context or {}
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            logger.debug(f"[ProjectMem] UPDATED {project_id}/{key}")
            return existing
        else:
            fact = ProjectMemory(
                project_id=project_id,
                key=key,
                value=value,
                context=context or {}
            )
            db.add(fact)
            db.commit()
            db.refresh(fact)
            logger.debug(f"[ProjectMem] SET {project_id}/{key}")
            return fact

    def get_project_facts(self, db: Session, project_id: str) -> Dict[str, str]:
        """
        Retrieve all project-level facts as a flat key→value dict.
        This is passed to the LLM as part of its system prompt context.
        """
        facts = db.query(ProjectMemory).filter(ProjectMemory.project_id == project_id).all()
        return {f.key: f.value for f in facts}

    def get_project_fact(self, db: Session, project_id: str, key: str) -> Optional[str]:
        """Retrieve a single project fact by key."""
        fact = db.query(ProjectMemory).filter(
            ProjectMemory.project_id == project_id,
            ProjectMemory.key == key
        ).first()
        return fact.value if fact else None

    def delete_project_fact(self, db: Session, project_id: str, key: str) -> bool:
        """Delete a project-level fact by key."""
        fact = db.query(ProjectMemory).filter(
            ProjectMemory.project_id == project_id,
            ProjectMemory.key == key
        ).first()
        if fact:
            db.delete(fact)
            db.commit()
            logger.debug(f"[ProjectMem] DELETED {project_id}/{key}")
            return True
        return False

    # ── Experience Memory ──────────────────────────────────────────────────────

    def save_experience(
        self,
        db: Session,
        problem: str,
        solution: str,
        tags: List[str],
        source_project_id: Optional[str] = None,
        source_execution_id: Optional[str] = None,
    ) -> ExperienceMemory:
        """
        Save a new experience (problem-solution pair) to the global experience store.
        """
        experience = ExperienceMemory(
            tags=tags,
            problem=problem,
            solution=solution,
            source_project_id=source_project_id,
            source_execution_id=source_execution_id,
        )
        db.add(experience)
        db.commit()
        db.refresh(experience)
        logger.info(f"[ExperienceMem] SAVED experience with tags={tags}")
        return experience

    def get_experience_by_id(self, db: Session, experience_id: str) -> Optional[ExperienceMemory]:
        """Retrieve an experience entry by its unique ID."""
        return db.query(ExperienceMemory).filter(ExperienceMemory.id == experience_id).first()

    def search_experiences(self, db: Session, query_tags: List[str], limit: int = 5) -> List[ExperienceMemory]:
        """
        Retrieve experiences whose tags overlap with the query tags.
        Uses PostgreSQL JSON containment — returns experiences sorted by tag overlap score.
        """
        all_experiences = db.query(ExperienceMemory).order_by(ExperienceMemory.created_at.desc()).limit(200).all()
        query_set = set(query_tags)
        
        scored = []
        for exp in all_experiences:
            exp_tags = set(exp.tags or [])
            overlap = len(query_set & exp_tags)
            if overlap > 0:
                scored.append((overlap, exp))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:limit]]

    def search_experiences_vector(self, db: Session, query_text: str, limit: int = 5) -> List[ExperienceMemory]:
        """
        Semantic vector search fallback for experience memory.
        Searches problem/solution text substring or tags when vector index is initializing.
        """
        query_lower = query_text.lower()
        all_experiences = db.query(ExperienceMemory).order_by(ExperienceMemory.created_at.desc()).limit(200).all()
        
        results = []
        for exp in all_experiences:
            if (
                query_lower in exp.problem.lower()
                or query_lower in exp.solution.lower()
                or any(query_lower in t.lower() for t in (exp.tags or []))
            ):
                results.append(exp)
        return results[:limit]


# Singleton instance used across the application
memory_manager = MemoryManager()
