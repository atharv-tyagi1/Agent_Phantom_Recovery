import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from core.engine.state import ExecutionSnapshot, ExecutionStatus
from core.engine.context_builder import ContextBuilder
from core.engine.checkpoint import CheckpointManager
from core.tools.startup import tool_registry
from core.memory.manager import memory_manager
from core.llm.reviewer import GlobalReviewer, AuditReport
from core.llm.adapter import LLMAdapter
from core.llm.config import PRIMARY_MODEL

logger = logging.getLogger(__name__)


class ExecutionController:
    """
    Main Autonomous Execution Controller driving the Agent Phantom state machine.
    Orchestrates LLM decisions, tool execution, session memory, checkpoints, and GLM 5.2 Global Review.
    """

    def __init__(self, llm_adapter: Optional[LLMAdapter] = None, global_reviewer: Optional[GlobalReviewer] = None):
        self.llm = llm_adapter or LLMAdapter()
        self.reviewer = global_reviewer or GlobalReviewer()

    async def execute_task(
        self,
        db: Session,
        execution_id: str,
        task_id: str,
        project_id: str,
        task_prompt: str,
        workspace_path: str,
        repository_id: Optional[str] = None,
        max_steps: int = 15
    ) -> ExecutionSnapshot:
        
        snapshot = ExecutionSnapshot(
            execution_id=execution_id,
            task_id=task_id,
            project_id=project_id,
            status=ExecutionStatus.INITIALIZING,
            max_steps=max_steps
        )

        logger.info(f"[ExecutionController] Starting execution {execution_id} for task: '{task_prompt[:40]}...'")
        
        # Initial Checkpoint
        init_ckpt = CheckpointManager.create_checkpoint(workspace_path, label="init")
        if init_ckpt:
            snapshot.checkpoint_hashes.append(init_ckpt)

        while snapshot.current_step < snapshot.max_steps:
            snapshot.current_step += 1
            snapshot.status = ExecutionStatus.PLANNING

            # 1. Fetch Session Event Log
            session_events = await memory_manager.get_session(execution_id)

            # 2. Build Context Prompt
            messages = ContextBuilder.build_prompt_context(
                db=db,
                project_id=project_id,
                task_prompt=task_prompt,
                execution_id=execution_id,
                repository_id=repository_id,
                working_memory=snapshot.working_memory,
                session_events=session_events
            )

            # 3. LLM Step Decision
            try:
                llm_res = await self.llm.generate_completion(PRIMARY_MODEL, messages)
                content = llm_res["choices"][0]["message"]["content"]
                decision = json.loads(content)
            except Exception as e:
                logger.warning(f"[ExecutionController] Step {snapshot.current_step} LLM call failed: {e}")
                # Fallback decision structure
                decision = {
                    "thought": f"Encountered error or non-JSON output: {str(e)}",
                    "action_type": "complete",
                    "final_summary": "Execution completed via safety fallback."
                }

            thought = decision.get("thought", "")
            action_type = decision.get("action_type", "complete")

            # Log thought in session memory
            await memory_manager.append_session(execution_id, {
                "type": "thought",
                "step": snapshot.current_step,
                "content": thought
            })

            # Handle Action: Complete
            if action_type == "complete":
                snapshot.status = ExecutionStatus.REVIEWING
                logger.info(f"[ExecutionController] Step {snapshot.current_step}: Submitting to GLM 5.2 Global Reviewer...")

                # Submit to GLM 5.2 Global Reviewer
                audit_report: AuditReport = self.reviewer.review_execution(
                    task_goal=task_prompt,
                    execution_steps=session_events,
                    modified_files=snapshot.modified_files,
                    test_results=snapshot.last_error
                )

                await memory_manager.append_session(execution_id, {
                    "type": "global_review_audit",
                    "approved": audit_report.approved,
                    "quality_score": audit_report.quality_score,
                    "summary": audit_report.summary,
                    "rejection_reason": audit_report.rejection_reason,
                    "actionable_fix": audit_report.actionable_fix
                })

                if audit_report.approved:
                    snapshot.status = ExecutionStatus.COMPLETED
                    # Save successful pattern into Experience Memory
                    memory_manager.save_experience(
                        db=db,
                        problem=task_prompt,
                        solution=decision.get("final_summary", audit_report.summary),
                        tags=[t for t in task_prompt.split()[:5] if len(t) > 3],
                        source_project_id=project_id,
                        source_execution_id=execution_id
                    )
                    logger.info(f"[ExecutionController] Execution {execution_id} COMPLETED successfully!")
                    return snapshot
                else:
                    # Rejection -> Trigger Re-Planning Feedback Loop
                    snapshot.rejection_count += 1
                    logger.warning(
                        f"[ExecutionController] Rejection #{snapshot.rejection_count}: {audit_report.rejection_reason}"
                    )
                    snapshot.status = ExecutionStatus.RE_PLANNING
                    snapshot.working_memory["last_audit_rejection"] = {
                        "reason": audit_report.rejection_reason,
                        "fix": audit_report.actionable_fix
                    }
                    continue

            # Handle Action: Tool Call
            elif action_type == "tool_call":
                snapshot.status = ExecutionStatus.EXECUTING
                tool_name = decision.get("tool_name")
                tool_args = decision.get("tool_args", {})

                # Pre-tool Checkpoint
                ckpt = CheckpointManager.create_checkpoint(workspace_path, label=f"step-{snapshot.current_step}")
                if ckpt:
                    snapshot.checkpoint_hashes.append(ckpt)

                # Execute Tool
                tool_result = await tool_registry.execute_tool(tool_name, tool_args)

                # Track modified files if applicable
                if tool_name in ["write_file", "replace_file_content"]:
                    target_file = tool_args.get("file_path") or tool_args.get("target_file")
                    if target_file and target_file not in snapshot.modified_files:
                        snapshot.modified_files.append(target_file)

                # Append tool observation to Session Memory
                await memory_manager.append_session(execution_id, {
                    "type": "tool_observation",
                    "step": snapshot.current_step,
                    "tool_name": tool_name,
                    "success": tool_result.get("success", False),
                    "output": str(tool_result.get("output"))[:1000] if tool_result.get("output") else None,
                    "error": tool_result.get("error")
                })

                if not tool_result.get("success"):
                    snapshot.last_error = tool_result.get("error")

        # Max steps reached without completion
        snapshot.status = ExecutionStatus.FAILED
        snapshot.last_error = "Maximum step limit reached without achieving goal."
        logger.error(f"[ExecutionController] Execution {execution_id} FAILED: step limit reached.")
        return snapshot
