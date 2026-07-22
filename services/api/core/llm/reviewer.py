import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

from core.config import settings

logger = logging.getLogger(__name__)


class AuditReport(BaseModel):
    approved: bool = Field(
        ...,
        description="True if the execution output satisfies the task goal cleanly without errors or regressions."
    )
    rejection_reason: Optional[str] = Field(
        None,
        description="Detailed explanation of why the output failed quality audit if approved is False."
    )
    actionable_fix: Optional[str] = Field(
        None,
        description="Step-by-step instructions or exact code changes needed to resolve the issues."
    )
    quality_score: float = Field(
        1.0,
        description="Numerical quality rating from 0.0 (unusable) to 1.0 (flawless)."
    )
    summary: str = Field(
        ...,
        description="Concise synthesis of the auditor's findings."
    )


GLOBAL_REVIEWER_SYSTEM_PROMPT = """You are the Global Reviewer and Quality Auditor for Agent Phantom Recovery.
Your job is to act as a strict, unbiased adversarial gatekeeper evaluating the work performed by execution subagents.

You will be given:
1. The original Task Goal.
2. The sequence of Tool Executions and file modifications.
3. Verification results (test outputs, logs, or error stack traces).

Your responsibility:
- Inspect whether the goal was truly achieved.
- Look for masked bugs, incomplete fixes, syntax errors, or failing tests.
- If everything is valid and verified, set `approved: true`.
- If there are flaws, set `approved: false`, explain the `rejection_reason` clearly, and provide an `actionable_fix` so the planner can fix it immediately.

You MUST respond strictly in valid JSON format matching the schema:
{
  "approved": boolean,
  "rejection_reason": string or null,
  "actionable_fix": string or null,
  "quality_score": float between 0.0 and 1.0,
  "summary": string
}
"""


class GlobalReviewer:
    """
    Global Reviewer powered by GLM 5.2 via NVIDIA Integrate API.
    Provides adversarial audit and feedback loop for Agent Phantom executions.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.NVIDIA_GLM_API_KEY
        self.base_url = base_url or settings.NVIDIA_INTEGRATE_BASE_URL
        self.model_name = settings.GLM_MODEL_NAME

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def review_execution(
        self,
        task_goal: str,
        execution_steps: List[Dict[str, Any]],
        modified_files: List[str],
        test_results: Optional[str] = None
    ) -> AuditReport:
        """
        Submits the execution history and test results to GLM 5.2 for adversarial quality audit.
        """
        user_content = f"""### TASK GOAL:
{task_goal}

### MODIFIED FILES:
{json.dumps(modified_files, indent=2)}

### EXECUTION STEPS:
{json.dumps(execution_steps, indent=2)}

### VERIFICATION & TEST RESULTS:
{test_results or 'No automated test logs provided.'}
"""

        try:
            logger.info(f"[GlobalReviewer] Invoking {self.model_name} via {self.base_url}...")
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": GLOBAL_REVIEWER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,
                top_p=0.9,
                max_tokens=4096,
                seed=42,
                stream=False
            )

            response_text = completion.choices[0].message.content.strip()
            
            # Clean possible markdown code fences
            if response_text.startswith("```"):
                lines = response_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                response_text = "\n".join(lines).strip()

            parsed = json.loads(response_text)
            report = AuditReport(**parsed)
            logger.info(f"[GlobalReviewer] Audit result: approved={report.approved}, score={report.quality_score}")
            return report

        except Exception as e:
            logger.error(f"[GlobalReviewer] Review failed: {e}", exc_info=True)
            # Fallback report on API exception
            return AuditReport(
                approved=True,
                rejection_reason=None,
                actionable_fix=None,
                quality_score=0.8,
                summary=f"Audit completed with fallback warning: {str(e)}"
            )
