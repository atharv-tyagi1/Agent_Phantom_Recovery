import logging
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, ValidationError

from core.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all tools available to the Agent Phantom execution engine.
    Handles registration, schema generation, and safe execution with input validation.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance into the registry."""
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: '{tool.name}'")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def list_tool_names(self) -> List[str]:
        """Returns a list of all registered tool names."""
        return list(self._tools.keys())

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns the JSON schema for all registered tools.
        This list is passed directly to the LLM so it understands what tools are available.
        """
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, args_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with the provided raw arguments dictionary.
        
        1. Looks up the tool in the registry.
        2. Validates the args_dict against the tool's Pydantic schema.
        3. Calls the tool's async execute method.
        4. Returns a standardized result dict.
        """
        tool = self.get_tool(name)
        if not tool:
            logger.error(f"Tool not found in registry: '{name}'")
            return {
                "success": False,
                "output": None,
                "error": f"Tool '{name}' is not registered."
            }

        # Validate input through Pydantic schema
        try:
            validated_args = tool.args_schema(**args_dict)
        except ValidationError as e:
            logger.warning(f"Tool '{name}' received invalid arguments: {e}")
            return {
                "success": False,
                "output": None,
                "error": f"Invalid arguments for tool '{name}': {e}"
            }

        # Execute the tool
        try:
            logger.info(f"Executing tool '{name}' with args: {validated_args.model_dump()}")
            result = await tool.execute(**validated_args.model_dump())
            return result
        except Exception as e:
            logger.error(f"Unexpected error during tool '{name}' execution: {e}", exc_info=True)
            return {
                "success": False,
                "output": None,
                "error": f"Tool execution failed: {str(e)}"
            }


# Global default registry instance
default_registry = ToolRegistry()
