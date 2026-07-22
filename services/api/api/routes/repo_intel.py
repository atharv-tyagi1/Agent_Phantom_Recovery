from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from db.session import get_db
from db.models.repository import Repository
from db.models.user import User
from core.auth import get_current_user
from core.repo_intel import repo_indexer, CodeSearchEngine

router = APIRouter(prefix="/repositories", tags=["Repository Intelligence"])


# ── Pydantic Schemas ─────────────────────────────────────────────────────────

class CodeSearchRequest(BaseModel):
    query: str
    symbol_type: Optional[str] = None
    limit: int = 10


class CodeSymbolResponse(BaseModel):
    id: str
    name: str
    symbol_type: str
    file_path: str
    start_line: int
    end_line: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    relevance_score: Optional[float] = None

    class Config:
        from_attributes = True


# ── REST Endpoints ───────────────────────────────────────────────────────────

@router.post("/{repository_id}/index", response_model=Dict[str, Any])
def index_repository(
    repository_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger full AST parsing, symbol extraction, and dependency graph indexing for a repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = repo_indexer.index_repository(db, repository_id=repository_id, root_path=repo.local_path)
    return result


@router.get("/{repository_id}/symbols", response_model=List[CodeSymbolResponse])
def get_repository_symbols(
    repository_id: str,
    symbol_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List extracted AST code symbols for a repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return CodeSearchEngine.search_symbols(
        db=db,
        repository_id=repository_id,
        query="",
        limit=limit,
        symbol_type=symbol_type
    ) if not symbol_type else CodeSearchEngine.search_symbols(
        db=db,
        repository_id=repository_id,
        query=symbol_type,
        limit=limit
    )


@router.get("/{repository_id}/dependencies/impact", response_model=Dict[str, Any])
def get_file_impact_radius(
    repository_id: str,
    file_path: str = Query(..., description="Target file path to compute blast radius for"),
    max_depth: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compute the downstream impact radius (blast radius) if a target file is modified.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return repo_indexer.graph.get_impact_radius(file_path=file_path, max_depth=max_depth)


@router.post("/{repository_id}/search", response_model=List[CodeSymbolResponse])
def search_codebase(
    repository_id: str,
    body: CodeSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform hybrid semantic & symbol search across the repository codebase.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return CodeSearchEngine.search_symbols(
        db=db,
        repository_id=repository_id,
        query=body.query,
        limit=body.limit,
        symbol_type=body.symbol_type
    )
