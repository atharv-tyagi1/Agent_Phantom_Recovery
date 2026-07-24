from core.tools.registry import ToolRegistry
from core.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from core.tools.terminal import TerminalTool
from core.tools.git import (
    GitStatusTool, GitDiffTool, GitAddTool,
    GitCommitTool, GitBranchTool, GitCloneTool
)
from core.tools.ocr import NemotronOCRTool
from core.tools.github_pr import CreatePullRequestTool

def build_default_registry() -> ToolRegistry:
    """
    Instantiates and registers all available tools into a fresh ToolRegistry.
    Call this once at application startup and inject the registry where needed.
    """
    registry = ToolRegistry()

    # Filesystem tools
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirTool())

    # Terminal tool
    registry.register(TerminalTool())

    # Git & GitHub tools
    registry.register(GitStatusTool())
    registry.register(GitDiffTool())
    registry.register(GitAddTool())
    registry.register(GitCommitTool())
    registry.register(GitBranchTool())
    registry.register(GitCloneTool())
    registry.register(CreatePullRequestTool())

    # Vision / OCR tools
    registry.register(NemotronOCRTool())

    return registry

# Singleton registry used across the application
tool_registry = build_default_registry()
