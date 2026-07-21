import logging
import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type

from pydantic import BaseModel, Field

from core.tools.base import BaseTool
from core.config import settings

logger = logging.getLogger(__name__)

# Workspace sandbox root — all filesystem operations are locked inside here
WORKSPACE_ROOT = Path(settings.WORKSPACE_ROOT).resolve()


# ── Argument Schemas ──────────────────────────────────────────────────────────

class ReadFileArgs(BaseModel):
    path: str = Field(..., description="Relative path to the file inside the workspace root.")

class WriteFileArgs(BaseModel):
    path: str = Field(..., description="Relative path to the file inside the workspace root.")
    content: str = Field(..., description="Content to write into the file.")
    mode: Literal["write", "append"] = Field(default="write", description="'write' to overwrite, 'append' to add to end.")

class ListDirArgs(BaseModel):
    path: str = Field(default=".", description="Relative path to the directory inside the workspace root.")


# ── Security Helper ───────────────────────────────────────────────────────────

def _resolve_safe_path(relative_path: str) -> Path:
    """
    Resolve a relative path against the workspace root and verify it doesn't
    escape the sandbox. Raises ValueError on directory traversal attempts.
    """
    resolved = (WORKSPACE_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(WORKSPACE_ROOT)):
        raise ValueError(
            f"Access denied: path '{relative_path}' resolves outside the workspace sandbox."
        )
    return resolved


# ── Concrete Tool Implementations ─────────────────────────────────────────────

class ReadFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Reads the full content of a file within the project workspace. "
            "Use this to inspect source code, configuration files, or any text-based file. "
            "Provide a relative path from the workspace root."
        )

    @property
    def args_schema(self) -> Type[BaseModel]:
        return ReadFileArgs

    async def execute(self, path: str, **kwargs) -> Dict[str, Any]:
        try:
            safe_path = _resolve_safe_path(path)
            if not safe_path.exists():
                return {"success": False, "output": None, "error": f"File not found: {path}"}
            if not safe_path.is_file():
                return {"success": False, "output": None, "error": f"Path is not a file: {path}"}
            content = safe_path.read_text(encoding="utf-8", errors="replace")
            return {"success": True, "output": content, "error": None}
        except ValueError as e:
            return {"success": False, "output": None, "error": str(e)}
        except Exception as e:
            logger.error(f"ReadFileTool error: {e}", exc_info=True)
            return {"success": False, "output": None, "error": str(e)}


class WriteFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Writes or appends content to a file within the project workspace. "
            "Creates parent directories if they don't exist. "
            "Provide a relative path and the content string. "
            "mode='write' overwrites the file; mode='append' adds to the end."
        )

    @property
    def args_schema(self) -> Type[BaseModel]:
        return WriteFileArgs

    async def execute(self, path: str, content: str, mode: str = "write", **kwargs) -> Dict[str, Any]:
        try:
            safe_path = _resolve_safe_path(path)
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            file_mode = "w" if mode == "write" else "a"
            with open(safe_path, file_mode, encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "output": f"Successfully wrote to {path}", "error": None}
        except ValueError as e:
            return {"success": False, "output": None, "error": str(e)}
        except Exception as e:
            logger.error(f"WriteFileTool error: {e}", exc_info=True)
            return {"success": False, "output": None, "error": str(e)}


class ListDirTool(BaseTool):
    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return (
            "Lists the files and subdirectories at a given path within the project workspace. "
            "Useful for exploring the codebase structure before reading specific files. "
            "Provide a relative path, or '.' for the workspace root."
        )

    @property
    def args_schema(self) -> Type[BaseModel]:
        return ListDirArgs

    async def execute(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        try:
            safe_path = _resolve_safe_path(path)
            if not safe_path.exists():
                return {"success": False, "output": None, "error": f"Directory not found: {path}"}
            if not safe_path.is_dir():
                return {"success": False, "output": None, "error": f"Path is not a directory: {path}"}
            entries = []
            for entry in sorted(safe_path.iterdir()):
                entry_type = "dir" if entry.is_dir() else "file"
                size = "" if entry.is_dir() else f" ({entry.stat().st_size} bytes)"
                entries.append(f"[{entry_type}] {entry.name}{size}")
            output = "\n".join(entries) if entries else "(empty directory)"
            return {"success": True, "output": output, "error": None}
        except ValueError as e:
            return {"success": False, "output": None, "error": str(e)}
        except Exception as e:
            logger.error(f"ListDirTool error: {e}", exc_info=True)
            return {"success": False, "output": None, "error": str(e)}
