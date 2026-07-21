"""
JWT verification and authentication dependency for FastAPI.
Validates Supabase-issued JWTs and manages user upsert on first login.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import settings
from db.session import get_db
from db.models.user import User, UserRole

security = HTTPBearer()


def verify_jwt(token: str) -> dict:
    """
    Decode and validate a Supabase-issued JWT.
    Returns the decoded payload on success; raises HTTPException on failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


def _upsert_user(db: Session, supabase_id: str, email: str) -> User:
    """
    Find or create a local user record linked to the Supabase auth user.
    """
    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if user is None:
        user = User(
            id=str(uuid.uuid4()),
            supabase_id=supabase_id,
            email=email,
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extracts Bearer token, verifies JWT, and returns the
    authenticated User record (creating it on first encounter).
    """
    payload = verify_jwt(credentials.credentials)

    supabase_id: Optional[str] = payload.get("sub")
    email: Optional[str] = payload.get("email")

    if not supabase_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
        )

    user = _upsert_user(db, supabase_id, email or "")
    return user
