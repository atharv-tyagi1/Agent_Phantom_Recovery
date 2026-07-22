import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from core.memory.manager import memory_manager
from core.repo_intel.embeddings import CodeSearchEngine

logger = logging.getLogger(__name__)


SYSTEM_PERSONA_PROMPT = """You are Agent Phantom, an autonomous senior engineering agent.
You operate on a closed-loop execution model: Plan -> Investigate -> Use Tools -> Verify -> Audit.

Your Goal: Fulfill the user's software engineering task by producing precise file changes, running verification commands, and ensuring zero regressions.

Guidelines:
1. Always base decisions on verified codebase facts from the provided context.
2. Use tools methodically (read_file, write_file, terminal, git, nemotron_ocr).
3. If an audit report or rejection feedback is provided, incorporate the actionable fix immediately.

You MUST respond strictly in valid JSON format:
{
  "thought": "Reasoning about current state and next step",
  "action_type": "tool_call" OR "complete" OR "ask_clarification",
  "tool_name": "name of tool to execute if action_type is tool_call",
  "tool_args": { ... arguments matching the tool's schema ... },
  "final_summary": "summary text if action_type is complete"
}
"""


class ContextBuilder:
    """
    Synthesizes multi-source context (Project Memory, Session Log, Working Memory, AST Symbols)
    into high-signal system and user prompts for the LLM.
    """

    @staticmethod
    def build_prompt_context(
        db: Session,
        project_id: str,
        task_prompt: str,
        execution_id: str,
        repository_id: Optional[str] = None,
        working_memory: Optional[Dict[str, Any]] = None,
        session_events: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, str]]:
        
        # 1. Fetch Project Memory facts
        project_facts = memory_manager.get_project_facts(db, project_id) if project_id else {}

        # 2. Fetch Relevant Experience Memory suggestions
        prompt_words = task_prompt.split()
        experiences = memory_manager.search_experiences(db, query_tags=prompt_words[:5], limit=3)
        exp_snippets = [
            {"problem": e.problem, "solution": e.solution} for e in experiences
        ]

        # 3. Fetch AST Code Symbols if repository_id is provided
        symbols = []
        if repository_id:
            symbols = CodeSearchEngine.search_symbols(
                db=db,
                repository_id=repository_id,
                query=task_prompt,
                limit=8
            )

        # Build Context Overview Block
        context_payload = {
            "task_prompt": task_prompt,
            "project_facts": project_facts,
            "reusable_experiences": exp_snippets,
            "relevant_code_symbols": symbols,
            "working_memory": working_memory or {},
            "recent_session_events": session_events[-10:] if session_events else []
        }

        messages = [
            {"role": "system", "content": SYSTEM_PERSONA_PROMPT},
            {"role": "user", "content": f"### CURRENT EXECUTION CONTEXT:\n{json.dumps(context_payload, indent=2)}"}
        ]

        return messages
