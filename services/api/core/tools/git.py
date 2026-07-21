import logging
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type

from pydantic import BaseModel, Field

from core.tools.base import BaseTool
from core.tools.terminal import TerminalTool
from core.config import settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(settings.WORKSPACE_ROOT).resolve()

# Reuse the TerminalTool for subprocess execution
_terminal = TerminalTool()


# ── Argument Schemas ──────────────────────────────────────────────────────────

class GitStatusArgs(BaseModel):
    repo_path: str = Field(default=".", description="Relative path to the git repository within the workspace.")

class GitDiffArgs(BaseModel):
    repo_path: str = Field(default=".", description="Relative path to the git repository within the workspace.")
    file_path: Optional[str] = Field(default=None, description="Optional: a specific file to diff.")
    staged: bool = Field(default=False, description="If true, shows staged diff (--cached).")

class GitAddArgs(BaseModel):
    repo_path: str = Field(default=".", description="Relative path to the git repository within the workspace.")
    file_path: str = Field(default=".", description="File or pattern to stage. Use '.' for all changes.")

class GitCommitArgs(BaseModel):
    repo_path: str = Field(default=".", description="Relative path to the git repository within the workspace.")
    message: str = Field(..., description="Commit message.")

class GitBranchArgs(BaseModel):
    repo_path: str = Field(default=".", description="Relative path to the git repository within the workspace.")
    action: Literal["list", "create", "checkout"] = Field(..., description="'list' existing branches, 'create' new, or 'checkout' existing.")
    branch_name: Optional[str] = Field(default=None, description="Branch name. Required for 'create' and 'checkout' actions.")

class GitCloneArgs(BaseModel):
    repo_url: str = Field(..., description="The remote repository URL to clone.")
    destination: str = Field(..., description="Relative path inside the workspace where the repo will be cloned.")


# ── Concrete Tool Implementations ─────────────────────────────────────────────

class GitStatusTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Shows the current git status (modified, staged, untracked files) of a repository in the workspace."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitStatusArgs

    async def execute(self, repo_path: str = ".", **kwargs) -> Dict[str, Any]:
        return await _terminal.execute(command="git status", working_dir=repo_path)


class GitDiffTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Shows the diff of uncommitted changes (or staged changes) in the repository. Use to inspect what was changed before committing."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitDiffArgs

    async def execute(self, repo_path: str = ".", file_path: Optional[str] = None, staged: bool = False, **kwargs) -> Dict[str, Any]:
        cmd_parts = ["git", "diff"]
        if staged:
            cmd_parts.append("--cached")
        if file_path:
            cmd_parts.append(f"-- {file_path}")
        return await _terminal.execute(command=" ".join(cmd_parts), working_dir=repo_path)


class GitAddTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_add"

    @property
    def description(self) -> str:
        return "Stages files for the next commit. Use '.' for all changes, or a specific file path."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitAddArgs

    async def execute(self, repo_path: str = ".", file_path: str = ".", **kwargs) -> Dict[str, Any]:
        return await _terminal.execute(command=f"git add {file_path}", working_dir=repo_path)


class GitCommitTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return "Creates a new git commit with a provided message for all staged changes."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitCommitArgs

    async def execute(self, repo_path: str = ".", message: str = "", **kwargs) -> Dict[str, Any]:
        # Escape quotes to prevent shell injection
        safe_message = message.replace('"', '\\"')
        return await _terminal.execute(command=f'git commit -m "{safe_message}"', working_dir=repo_path)


class GitBranchTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_branch"

    @property
    def description(self) -> str:
        return "Manages git branches. Can list all branches, create a new branch, or checkout an existing one."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitBranchArgs

    async def execute(self, repo_path: str = ".", action: str = "list", branch_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if action == "list":
            cmd = "git branch -a"
        elif action == "create":
            if not branch_name:
                return {"success": False, "output": None, "error": "branch_name is required for 'create' action."}
            cmd = f"git checkout -b {branch_name}"
        elif action == "checkout":
            if not branch_name:
                return {"success": False, "output": None, "error": "branch_name is required for 'checkout' action."}
            cmd = f"git checkout {branch_name}"
        else:
            return {"success": False, "output": None, "error": f"Unknown action: {action}"}

        return await _terminal.execute(command=cmd, working_dir=repo_path)


class GitCloneTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_clone"

    @property
    def description(self) -> str:
        return "Clones a remote git repository into the specified path inside the workspace."

    @property
    def args_schema(self) -> Type[BaseModel]:
        return GitCloneArgs

    async def execute(self, repo_url: str, destination: str, **kwargs) -> Dict[str, Any]:
        return await _terminal.execute(command=f"git clone {repo_url} {destination}")
