"""
Authentication API routes.
Proxies signup/login/logout/refresh to Supabase Auth and manages local user records.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import httpx

from core.config import settings
from core.auth import get_current_user
from db.session import get_db
from db.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

SUPABASE_AUTH_URL = f"{settings.SUPABASE_URL}/auth/v1"
SUPABASE_HEADERS = {
    "apikey": settings.SUPABASE_KEY,
    "Content-Type": "application/json",
}


# ──────────────────────────── Request / Response Schemas ─────────────────────

class SignUpRequest(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    supabase_id: str
    email: str
    display_name: str | None
    avatar_url: str | None
    role: str
    created_at: str

    class Config:
        from_attributes = True


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


# ──────────────────────────── Routes ─────────────────────────────────────────

@router.post("/signup", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new user via Supabase Auth and create a local record."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_AUTH_URL}/signup",
            headers=SUPABASE_HEADERS,
            json={"email": payload.email, "password": payload.password},
        )

    if resp.status_code >= 400:
        detail = resp.json().get("msg") or resp.json().get("error_description") or resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    data = resp.json()
    supabase_user = data.get("user", {})
    supabase_id = supabase_user.get("id", "")

    # Create local user record
    from db.models.user import UserRole
    import uuid
    existing = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not existing:
        new_user = User(
            id=str(uuid.uuid4()),
            supabase_id=supabase_id,
            email=payload.email,
            display_name=payload.display_name,
            role=UserRole.USER,
        )
        db.add(new_user)
        db.commit()

    return AuthTokenResponse(
        access_token=data.get("access_token", ""),
        refresh_token=data.get("refresh_token", ""),
        expires_in=data.get("expires_in", 3600),
        user=supabase_user,
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest):
    """Authenticate a user via Supabase Auth."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_AUTH_URL}/token?grant_type=password",
            headers=SUPABASE_HEADERS,
            json={"email": payload.email, "password": payload.password},
        )

    if resp.status_code >= 400:
        detail = resp.json().get("error_description") or resp.text
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    data = resp.json()
    return AuthTokenResponse(
        access_token=data.get("access_token", ""),
        refresh_token=data.get("refresh_token", ""),
        expires_in=data.get("expires_in", 3600),
        user=data.get("user", {}),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Sign out the current user. Supabase handles session invalidation
    client-side; this endpoint confirms the user was authenticated.
    """
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        supabase_id=current_user.supabase_id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_token(payload: RefreshRequest):
    """Refresh an access token via Supabase Auth."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_AUTH_URL}/token?grant_type=refresh_token",
            headers=SUPABASE_HEADERS,
            json={"refresh_token": payload.refresh_token},
        )

    if resp.status_code >= 400:
        detail = resp.json().get("error_description") or resp.text
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    data = resp.json()
    return AuthTokenResponse(
        access_token=data.get("access_token", ""),
        refresh_token=data.get("refresh_token", ""),
        expires_in=data.get("expires_in", 3600),
        user=data.get("user", {}),
    )
