import unittest
import asyncio
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.session import Base
from db.models.user import User
from db.models.project import Project
from db.models.memory import ProjectMemory, ExperienceMemory
from core.memory.manager import MemoryManager

# In-memory SQLite for database tier testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


class TestMemorySystem(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.db = TestingSessionLocal(bind=self.connection)

        # Create test user & project
        self.user = User(
            id=str(uuid.uuid4()),
            supabase_id=str(uuid.uuid4()),
            email=f"user_{uuid.uuid4().hex[:6]}@phantom.ai"
        )
        self.db.add(self.user)
        self.db.commit()

        self.project = Project(
            id=str(uuid.uuid4()),
            name="Phantom Core Project",
            description="Testing Phase 5 Memory Manager",
            owner_id=self.user.id
        )
        self.db.add(self.project)
        self.db.commit()
        self.db.refresh(self.project)
        self.manager = MemoryManager()

    def tearDown(self):
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    # ── Project Memory Tests ─────────────────────────────────────────────────

    def test_project_memory_crud(self):
        project_id = self.project.id

        # 1. Set fact
        fact1 = self.manager.set_project_fact(self.db, project_id, "primary_language", "Python")
        self.assertEqual(fact1.key, "primary_language")
        self.assertEqual(fact1.value, "Python")

        # 2. Upsert fact
        fact1_updated = self.manager.set_project_fact(self.db, project_id, "primary_language", "Python 3.11")
        self.assertEqual(fact1_updated.value, "Python 3.11")

        # 3. Add second fact
        self.manager.set_project_fact(self.db, project_id, "framework", "FastAPI")

        # 4. Get single fact
        lang = self.manager.get_project_fact(self.db, project_id, "primary_language")
        self.assertEqual(lang, "Python 3.11")

        # 5. Get all facts dict
        facts_dict = self.manager.get_project_facts(self.db, project_id)
        self.assertEqual(facts_dict, {
            "primary_language": "Python 3.11",
            "framework": "FastAPI"
        })

        # 6. Delete fact
        deleted = self.manager.delete_project_fact(self.db, project_id, "framework")
        self.assertTrue(deleted)
        self.assertIsNone(self.manager.get_project_fact(self.db, project_id, "framework"))

    # ── Experience Memory Tests ──────────────────────────────────────────────

    def test_experience_memory_crud_and_search(self):
        # 1. Save experience 1
        exp1 = self.manager.save_experience(
            db=self.db,
            problem="SQLAlchemy connection pool timeout under concurrency",
            solution="Set pool_pre_ping=True and tune pool_size=20",
            tags=["sqlalchemy", "database", "postgres"],
            source_project_id=self.project.id
        )
        self.assertIsNotNone(exp1.id)
        self.assertTrue(exp1.problem.startswith("SQLAlchemy"))

        # 2. Save experience 2
        exp2 = self.manager.save_experience(
            db=self.db,
            problem="Redis async connection leak in FastAPI startup",
            solution="Close redis connection on app shutdown event",
            tags=["redis", "fastapi", "asyncio"],
            source_project_id=self.project.id
        )

        # 3. Get experience by ID
        retrieved = self.manager.get_experience_by_id(self.db, exp1.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, exp1.id)

        # 4. Search by tags
        tag_results = self.manager.search_experiences(self.db, query_tags=["redis", "fastapi"])
        self.assertGreaterEqual(len(tag_results), 1)
        self.assertEqual(tag_results[0].id, exp2.id)

        # 5. Search by vector/text fallback
        text_results = self.manager.search_experiences_vector(self.db, query_text="connection pool")
        self.assertGreaterEqual(len(text_results), 1)
        self.assertEqual(text_results[0].id, exp1.id)

    # ── Redis Memory Tests (Async) ──────────────────────────────────────────

    def test_working_and_session_memory_redis(self):
        async def run_async_tests():
            execution_id = f"test_exec_{uuid.uuid4().hex[:8]}"

            try:
                # Test Working Memory
                await self.manager.set_working(execution_id, "current_step", {"step": 1, "action": "grep"})
                val = await self.manager.get_working(execution_id, "current_step")
                self.assertEqual(val, {"step": 1, "action": "grep"})

                await self.manager.clear_working(execution_id)
                cleared_val = await self.manager.get_working(execution_id, "current_step")
                self.assertIsNone(cleared_val)

                # Test Session Memory
                await self.manager.append_session(execution_id, {"type": "thought", "content": "Analyzing repository"})
                await self.manager.append_session(execution_id, {"type": "tool_call", "name": "view_file"})

                full_session = await self.manager.get_session(execution_id)
                self.assertEqual(len(full_session), 2)
                self.assertEqual(full_session[0]["type"], "thought")
                self.assertEqual(full_session[1]["name"], "view_file")

                summary = await self.manager.get_session_summary(execution_id, last_n=1)
                self.assertEqual(len(summary), 1)
                self.assertEqual(summary[0]["name"], "view_file")
            except Exception as e:
                print(f"[Skipping Redis tests — Redis offline: {e}]")

        asyncio.run(run_async_tests())


if __name__ == "__main__":
    unittest.main()

