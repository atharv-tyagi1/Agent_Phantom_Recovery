import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from db.models.webhook_event import WebhookEvent
from db.models.repository import Repository
from db.models.repository_monitoring import RepositoryMonitoringSettings, MonitoringMode
from db.models.task import Task, TaskPriority
from db.models.execution import Execution
from core.repo_intel.incremental_indexer import IncrementalASTIndexer
from core.engine.controller import ExecutionController

logger = logging.getLogger(__name__)


async def handle_webhook_event(db: Session, event: WebhookEvent) -> Dict[str, Any]:
    """
    Main webhook event router processing push, pull_request, and installation events.
    """
    event_type = event.github_event_type
    payload = event.payload

    if event_type == "push":
        return await _handle_push_event(db, payload)
    elif event_type == "pull_request":
        return await _handle_pr_event(db, payload)
    elif event_type in ["installation", "installation_repositories"]:
        return {"status": "installation_updated"}
    else:
        return {"status": "ignored", "event_type": event_type}


async def _handle_push_event(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    repo_payload = payload.get("repository", {})
    github_repo_id = repo_payload.get("id")
    full_name = repo_payload.get("full_name")
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")
    head_commit = payload.get("head_commit", {})
    commit_sha = head_commit.get("id", "")
    commit_message = head_commit.get("message", "")

    # Lookup repository record
    repo = db.query(Repository).filter(
        (Repository.github_repo_id == github_repo_id) | (Repository.full_name == full_name)
    ).first()

    if not repo:
        logger.info(f"[WebhookProcessor] Repository {full_name} not linked in Agent Phantom. Ignoring.")
        return {"status": "repo_not_linked"}

    # Extract modified file lists from head commit
    added = head_commit.get("added", [])
    modified = head_commit.get("modified", [])
    removed = head_commit.get("removed", [])

    # Perform Incremental AST Re-indexing
    if repo.local_path:
        IncrementalASTIndexer.process_diff_files(
            db=db,
            repository_id=repo.id,
            root_path=repo.local_path,
            added_files=added,
            modified_files=modified,
            deleted_files=removed
        )

    repo.last_commit_sha = commit_sha
    db.commit()

    # Check Monitoring Settings
    monitoring = db.query(RepositoryMonitoringSettings).filter(
        RepositoryMonitoringSettings.repository_id == repo.id
    ).first()

    if not monitoring or monitoring.mode == MonitoringMode.MANUAL or not monitoring.trigger_on_push:
        return {"status": "push_indexed_no_trigger", "mode": monitoring.mode.value if monitoring else "none"}

    # Trigger Autonomous Execution if mode is auto_investigate, auto_fix, or auto_pr
    task_title = f"Autonomous Push Audit: {commit_sha[:7]} - {commit_message[:50]}"
    task = Task(
        project_id=repo.project_id,
        title=task_title,
        description=f"Automated recovery investigation triggered by push on branch '{branch}' (SHA: {commit_sha}).",
        priority=TaskPriority.HIGH
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    execution = Execution(
        task_id=task.id,
        project_id=repo.project_id,
        goal=task.title
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Launch controller state machine
    controller = ExecutionController()
    workspace_path = repo.local_path or f"workspaces/{repo.project_id}/{repo.name}"
    
    snapshot = await controller.execute_task(
        db=db,
        execution_id=execution.id,
        task_id=task.id,
        project_id=repo.project_id,
        task_prompt=task.title,
        workspace_path=workspace_path,
        repository_id=repo.id,
        max_steps=10
    )

    return {
        "status": "auto_execution_completed",
        "execution_id": execution.id,
        "execution_status": snapshot.status.value
    }


async def _handle_pr_event(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action")
    pr_dict = payload.get("pull_request", {})
    pr_number = pr_dict.get("number")
    title = pr_dict.get("title")
    logger.info(f"[WebhookProcessor] PR Event #{pr_number} ({action}): {title}")
    return {"status": "pr_event_processed", "action": action, "pr_number": pr_number}
