import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from core.tools.base import BaseTool
from core.config import settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(settings.WORKSPACE_ROOT).resolve()
DEFAULT_TIMEOUT = 30  # seconds


# ── Argument Schema ───────────────────────────────────────────────────────────

class RunCommandArgs(BaseModel):
    command: str = Field(..., description="The shell command to execute inside the workspace.")
    timeout: Optional[int] = Field(
        default=DEFAULT_TIMEOUT,
        description=f"Execution timeout in seconds. Defaults to {DEFAULT_TIMEOUT}s. Max 120s."
    )
    working_dir: Optional[str] = Field(
        default=None,
        description="Relative path within the workspace to use as the working directory. Defaults to workspace root."
    )


# ── Concrete Tool Implementation ──────────────────────────────────────────────

class TerminalTool(BaseTool):
    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return (
            "Executes a shell command inside the secure workspace sandbox and returns the combined stdout/stderr. "
            "Use for running tests, linters, build commands, or inspecting the environment. "
            "Commands are always executed inside the workspace root (or a specified subdirectory). "
            "Commands are killed and an error is returned if they exceed the timeout."
        )

    @property
    def args_schema(self) -> Type[BaseModel]:
        return RunCommandArgs

    async def execute(self, command: str, timeout: int = DEFAULT_TIMEOUT, working_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        # Clamp timeout to a safe max to prevent runaway processes
        timeout = min(timeout or DEFAULT_TIMEOUT, 120)

        # Determine working directory — must be inside workspace root
        if working_dir:
            cwd = (WORKSPACE_ROOT / working_dir).resolve()
            if not str(cwd).startswith(str(WORKSPACE_ROOT)):
                return {
                    "success": False,
                    "output": None,
                    "error": f"Access denied: working_dir '{working_dir}' resolves outside the workspace sandbox."
                }
        else:
            cwd = WORKSPACE_ROOT

        logger.info(f"TerminalTool: running command in '{cwd}': {command!r}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(cwd)
            )

            try:
                stdout, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return {
                    "success": False,
                    "output": None,
                    "error": f"Command timed out after {timeout}s: {command!r}"
                }

            output = stdout.decode("utf-8", errors="replace")
            success = process.returncode == 0

            return {
                "success": success,
                "output": output,
                "error": None if success else f"Command exited with code {process.returncode}",
                "exit_code": process.returncode
            }

        except Exception as e:
            logger.error(f"TerminalTool error: {e}", exc_info=True)
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
