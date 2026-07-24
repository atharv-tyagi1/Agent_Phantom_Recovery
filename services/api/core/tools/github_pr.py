import logging
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field
from core.tools.base import BaseTool
from core.github.client import GitHubClient

logger = logging.getLogger(__name__)


class CreatePullRequestInput(BaseModel):
    installation_token: Optional[str] = Field(default="", description="Short-lived GitHub App installation token")
    full_name: Optional[str] = Field(default="", description="Repository full name (owner/repo)")
    title: Optional[str] = Field(default="", description="Pull Request title")
    body: Optional[str] = Field(default="", description="Pull Request body content")
    head: Optional[str] = Field(default="", description="Head branch containing the patch")
    base: Optional[str] = Field(default="main", description="Base branch to merge into")


class CreatePullRequestTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_pull_request"

    @property
    def description(self) -> str:
        return "Creates a GitHub Pull Request with the verified patch and audit report description."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return CreatePullRequestInput

    async def execute(
        self,
        installation_token: str = "",
        full_name: str = "",
        title: str = "",
        body: str = "",
        head: str = "",
        base: str = "main",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Creates a Pull Request via GitHub App installation token.
        """
        try:
            pr_data = await GitHubClient.create_pull_request(
                installation_token=installation_token or "mock_installation_token",
                full_name=full_name or "agent-phantom/demo-repo",
                title=title or "fix: autonomous recovery patch",
                body=body or "Verified by Agent Phantom Closed-Loop Execution Engine & GLM 5.2 Audit.",
                head=head or "phantom/fix-branch",
                base=base or "main"
            )
            return {
                "success": True,
                "output": f"Successfully opened PR #{pr_data.get('number')} ({pr_data.get('html_url')})",
                "pr": pr_data,
                "error": None
            }
        except Exception as e:
            logger.error(f"[CreatePullRequestTool] Failed: {e}")
            return {"success": False, "output": None, "error": str(e)}
