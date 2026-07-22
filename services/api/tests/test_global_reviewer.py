import unittest
import json
from unittest.mock import patch, MagicMock

from core.llm.reviewer import GlobalReviewer, AuditReport


class TestGlobalReviewer(unittest.TestCase):

    def setUp(self):
        self.reviewer = GlobalReviewer(
            api_key="nvapi-test-key",
            base_url="https://integrate.api.nvidia.com/v1"
        )

    def test_reviewer_initialization(self):
        self.assertEqual(self.reviewer.api_key, "nvapi-test-key")
        self.assertEqual(self.reviewer.base_url, "https://integrate.api.nvidia.com/v1")
        self.assertEqual(self.reviewer.model_name, "z-ai/glm-5.2")

    @patch("openai.resources.chat.completions.Completions.create")
    def test_review_execution_approved(self, mock_create):
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "approved": True,
            "rejection_reason": None,
            "actionable_fix": None,
            "quality_score": 0.98,
            "summary": "Task completed cleanly with passing verification tests."
        })
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_create.return_value = mock_completion

        report = self.reviewer.review_execution(
            task_goal="Fix login authentication token expiration bug",
            execution_steps=[
                {"step": 1, "tool": "replace_file_content", "target": "auth.py"},
                {"step": 2, "tool": "run_command", "cmd": "pytest tests/test_auth.py"}
            ],
            modified_files=["services/api/core/auth.py"],
            test_results="2 passed in 0.45s"
        )

        self.assertTrue(report.approved)
        self.assertEqual(report.quality_score, 0.98)
        self.assertIn("cleanly", report.summary)

    @patch("openai.resources.chat.completions.Completions.create")
    def test_review_execution_rejected_with_fix(self, mock_create):
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "approved": False,
            "rejection_reason": "Missing null check for user avatar in dashboard.tsx",
            "actionable_fix": "Wrap user.avatar with optional chaining: user?.avatar ?? '/default.png'",
            "quality_score": 0.4,
            "summary": "Rejection due to potential TypeError in dashboard UI."
        })
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_create.return_value = mock_completion

        report = self.reviewer.review_execution(
            task_goal="Render user profile in dashboard",
            execution_steps=[
                {"step": 1, "tool": "replace_file_content", "target": "dashboard.tsx"}
            ],
            modified_files=["apps/web/src/app/dashboard/page.tsx"],
            test_results="TypeError: Cannot read properties of undefined (reading 'avatar')"
        )

        self.assertFalse(report.approved)
        self.assertEqual(report.quality_score, 0.4)
        self.assertIn("Missing null check", report.rejection_reason)
        self.assertIn("user?.avatar", report.actionable_fix)


if __name__ == "__main__":
    unittest.main()
