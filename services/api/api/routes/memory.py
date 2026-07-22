from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from db.session import get_db
from db.models.project import Project
from db.models.user import User
from core.auth import get_current_user
from core.memory.manager import memory_manager

router = APIRouter(tags=["Memory"])


# ── Pydantic Schemas ─────────────────────────────────────────────────────────

class ProjectFactRequest(BaseModel):
    key: str
    value: str
    context: Optional[Dict[str, Any]] = None


class ExperienceCreateRequest(BaseModel):
    problem: str
    solution: str
    tags: List[str]
    source_project_id: Optional[str] = None
    source_execution_id: Optional[str] = None


class ExperienceResponse(BaseModel):
    id: str
    problem: str
    solution: str
    tags: List[str]
    source_project_id: Optional[str] = None
    source_execution_id: Optional[str] = None
    created_at: Any

    class Config:
        from_attributes = True


# ── Project Memory Endpoints ──────────────────────────────────────────────────

@router.get("/projects/{project_id}/memory", response_model=Dict[str, str])
def get_project_memory(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all project-level memory facts as a key→value map.
    Used by the Antigravity IDE to render the Project Memory panel.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return memory_manager.get_project_facts(db, project_id)


@router.post("/projects/{project_id}/memory")
def set_project_memory(
    project_id: str,
    body: ProjectFactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set or update a project-level fact.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    fact = memory_manager.set_project_fact(
        db=db,
        project_id=project_id,
        key=body.key,
        value=body.value,
        context=body.context
    )
    return {"status": "ok", "key": fact.key, "value": fact.value}


@router.delete("/projects/{project_id}/memory/{key}")
def delete_project_memory(
    project_id: str,
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project-level fact by key.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    deleted = memory_manager.delete_project_fact(db, project_id, key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"status": "deleted", "key": key}


# ── Session Memory Endpoints ──────────────────────────────────────────────────

@router.get("/executions/{execution_id}/session", response_model=List[Dict[str, Any]])
async def get_session_memory(
    execution_id: str,
    last_n: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Returns the session event log for a given execution.
    If last_n > 0, returns only the most recent N events (for context-window efficiency).
    Used by the Antigravity IDE to render the Timeline panel.
    """
    if last_n > 0:
        return await memory_manager.get_session_summary(execution_id, last_n=last_n)
    return await memory_manager.get_session(execution_id)


# ── Experience Memory Endpoints ───────────────────────────────────────────────

@router.post("/experiences", response_model=ExperienceResponse)
def create_experience(
    body: ExperienceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a new reusable problem-solution experience.
    """
    exp = memory_manager.save_experience(
        db=db,
        problem=body.problem,
        solution=body.solution,
        tags=body.tags,
        source_project_id=body.source_project_id,
        source_execution_id=body.source_execution_id,
    )
    return exp


@router.get("/experiences/search", response_model=List[ExperienceResponse])
def search_experiences(
    query: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search experience memory by tag overlap or text query.
    """
    if tags:
        return memory_manager.search_experiences(db, query_tags=tags, limit=limit)
    elif query:
        return memory_manager.search_experiences_vector(db, query_text=query, limit=limit)
    else:
        return []

