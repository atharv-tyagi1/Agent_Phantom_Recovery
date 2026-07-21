from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel


class BaseTool(ABC):
    """
    Abstract base class for all Agent Phantom tools.
    Every tool must declare its name, description, and an args_schema
    so that the ToolRegistry can expose its interface to the LLM.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this tool (e.g., 'read_file')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable and LLM-readable description of what this tool does,
        including when to use it and what it returns.
        """
        pass

    @property
    @abstractmethod
    def args_schema(self) -> Type[BaseModel]:
        """
        A Pydantic BaseModel class that defines and validates the tool's input arguments.
        The registry will parse raw LLM-provided dicts through this schema before execution.
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the validated keyword arguments.
        Must always return a dictionary result with at least:
          - 'success': bool
          - 'output': str (stdout, file contents, etc.) or None
          - 'error': str or None
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Returns a JSON-compatible schema dict describing the tool for the LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema()
        }
