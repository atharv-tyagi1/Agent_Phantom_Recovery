import unittest
import asyncio
import os
import uuid
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.session import Base
from db.models.user import User
from db.models.project import Project
from db.models.repository import Repository
from db.models.task import Task
from db.models.execution import Execution
from core.engine.state import ExecutionSnapshot, ExecutionStatus
from core.engine.context_builder import ContextBuilder
from core.engine.checkpoint import CheckpointManager
from core.engine.controller import ExecutionController
from core.llm.reviewer import AuditReport

# In-memory SQLite for engine testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


class TestAgentExecutionEngine(unittest.TestCase):

    def setUp(self):
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.db = TestingSessionLocal(bind=self.connection)

        self.user = User(
            id=str(uuid.uuid4()),
            supabase_id=str(uuid.uuid4()),
            email=f"user_{uuid.uuid4().hex[:6]}@phantom.ai"
        )
        self.db.add(self.user)
        self.db.commit()

        self.project = Project(
            id=str(uuid.uuid4()),
            name="Phantom Execution Test Project",
            description="Testing Phase 7 Execution Engine",
            owner_id=self.user.id
        )
        self.db.add(self.project)
        self.db.commit()

        self.workspace_dir = tempfile.mkdtemp()
        self.repo = Repository(
            id=str(uuid.uuid4()),
            project_id=self.project.id,
            name="Test Local Workspace",
            git_url="https://github.com/phantom/test.git",
            local_path=self.workspace_dir
        )
        self.db.add(self.repo)
        self.db.commit()

        self.task = Task(
            id=str(uuid.uuid4()),
            project_id=self.project.id,
            title="Refactor Auth Token Validator",
            description="Refactor validate_token function to use expiration timestamp"
        )
        self.db.add(self.task)
        self.db.commit()

    def tearDown(self):
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir, ignore_errors=True)
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    # ── State Machine & Snapshot Tests ────────────────────────────────────────

    def test_execution_snapshot(self):
        snap = ExecutionSnapshot(
            execution_id="exec-123",
            task_id=self.task.id,
            project_id=self.project.id,
            status=ExecutionStatus.INITIALIZING
        )
        self.assertEqual(snap.status, ExecutionStatus.INITIALIZING)
        self.assertEqual(snap.current_step, 0)
        self.assertEqual(snap.max_steps, 25)

    # ── Context Builder Tests ─────────────────────────────────────────────────

    def test_context_builder(self):
        messages = ContextBuilder.build_prompt_context(
            db=self.db,
            project_id=self.project.id,
            task_prompt="Fix login token validation bug",
            execution_id="exec-456",
            repository_id=self.repo.id
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("Fix login token validation bug", messages[1]["content"])

    # ── Checkpoint Manager Tests ──────────────────────────────────────────────

    def test_checkpoint_manager_graceful_fallback(self):
        # Non-git folder should return None without crashing
        ckpt = CheckpointManager.create_checkpoint(self.workspace_dir, label="test")
        self.assertIsNone(ckpt)

    # ── Execution Controller & GLM 5.2 Feedback Loop Tests ────────────────────

    def test_execution_controller_approved_flow(self):
        mock_llm = MagicMock()
        mock_reviewer = MagicMock()
        mock_llm.generate_completion = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "thought": "Refactored token validator successfully.",
                        "action_type": "complete",
                        "final_summary": "Token validator updated."
                    })
                }
            }]
        })

        # GLM 5.2 Reviewer: approved
        mock_reviewer.review_execution.return_value = AuditReport(
            approved=True,
            quality_score=0.95,
            summary="Refactor is clean and verified."
        )

        controller = ExecutionController(llm_adapter=mock_llm, global_reviewer=mock_reviewer)
        
        async def run_exec():
            return await controller.execute_task(
                db=self.db,
                execution_id=f"exec-{uuid.uuid4().hex[:6]}",
                task_id=self.task.id,
                project_id=self.project.id,
                task_prompt="Refactor validate_token function",
                workspace_path=self.workspace_dir,
                repository_id=self.repo.id,
                max_steps=5
            )

        snapshot = asyncio.run(run_exec())
        self.assertEqual(snapshot.status, ExecutionStatus.COMPLETED)
        self.assertEqual(snapshot.rejection_count, 0)

    def test_execution_controller_rejection_and_replanning_loop(self):
        mock_llm = MagicMock()
        mock_reviewer = MagicMock()

        # Step 1: Complete -> Rejected by GLM 5.2
        # Step 2: Complete -> Approved by GLM 5.2
        mock_llm.generate_completion = AsyncMock(side_effect=[
            {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "thought": "Initial draft of token fix.",
                            "action_type": "complete",
                            "final_summary": "First draft complete."
                        })
                    }
                }]
            },
            {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "thought": "Incorporated GLM 5.2 feedback to fix null check.",
                            "action_type": "complete",
                            "final_summary": "Second draft complete."
                        })
                    }
                }]
            }
        ])

        mock_reviewer.review_execution.side_effect = [
            AuditReport(
                approved=False,
                rejection_reason="Missing check for expired token timestamp",
                actionable_fix="Add `if token.exp < now: return False`",
                quality_score=0.3,
                summary="Rejection due to missing expiration validation"
            ),
            AuditReport(
                approved=True,
                quality_score=0.96,
                summary="Approved after adding expiration validation"
            )
        ]

        controller = ExecutionController(llm_adapter=mock_llm, global_reviewer=mock_reviewer)

        async def run_exec():
            return await controller.execute_task(
                db=self.db,
                execution_id=f"exec-{uuid.uuid4().hex[:6]}",
                task_id=self.task.id,
                project_id=self.project.id,
                task_prompt="Refactor validate_token function with expiration",
                workspace_path=self.workspace_dir,
                repository_id=self.repo.id,
                max_steps=5
            )

        snapshot = asyncio.run(run_exec())
        self.assertEqual(snapshot.status, ExecutionStatus.COMPLETED)
        self.assertEqual(snapshot.rejection_count, 1)


if __name__ == "__main__":
    unittest.main()
