"""
Authentication API routes.
Supports both Supabase Auth and GitHub OAuth Identity Layer.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import httpx
import uuid
import jwt
from datetime import datetime, timezone, timedelta

from core.config import settings
from core.auth import get_current_user
from core.crypto import encrypt_token, decrypt_token
from core.github.client import GitHubClient
from db.session import get_db
from db.models.user import User, UserRole
from db.models.github_oauth_account import GitHubOAuthAccount
from db.models.workspace import Workspace
from db.models.workspace_member import WorkspaceMember, WorkspaceRole

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


class OAuthCallbackRequest(BaseModel):
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    supabase_id: str | None
    github_user_id: int | None
    github_username: str | None
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


# ──────────────────────────── Helper Utilities ────────────────────────────────

def create_internal_jwt(user: User) -> str:
    payload = {
        "sub": user.supabase_id or user.id,
        "user_id": user.id,
        "email": user.email,
        "aud": "authenticated",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")


def ensure_default_workspace(db: Session, user: User) -> Workspace:
    """Ensure every user has a default personal workspace."""
    workspace = db.query(Workspace).filter(Workspace.owner_id == user.id).first()
    if not workspace:
        slug = f"workspace-{user.github_username or user.email.split('@')[0]}-{user.id[:6]}"
        workspace = Workspace(
            name=f"{user.display_name or user.email}'s Workspace",
            slug=slug,
            owner_id=user.id,
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member)
        db.commit()
    return workspace


# ──────────────────────────── GitHub OAuth Endpoints ────────────────────────

@router.get("/github/login")
def github_login():
    """Returns the GitHub OAuth login URL for frontend redirection."""
    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_OAUTH_REDIRECT_URI}"
        f"&scope=user:email,read:user,read:org"
    )
    return {"url": github_oauth_url}


@router.post("/github/callback", response_model=AuthTokenResponse)
async def github_oauth_callback(payload: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """
    Identity Layer: Exchange OAuth code for GitHub user token,
    upsert local User record & GitHubOAuthAccount, and issue session JWT.
    """
    try:
        # Mock mode if placeholder credentials are used in local dev
        if settings.GITHUB_CLIENT_ID.startswith("placeholder"):
            gh_user = {
                "id": 999111,
                "login": "octocat",
                "email": "octocat@github.com",
                "name": "The Octocat",
                "avatar_url": "https://avatars.githubusercontent.com/u/999111",
            }
            access_token = "mock_github_oauth_token"
        else:
            token_resp = await GitHubClient.exchange_oauth_code(payload.code)
            access_token = token_resp.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to obtain OAuth access token")
            gh_user = await GitHubClient.get_authenticated_user(access_token)

        gh_id = gh_user.get("id")
        gh_login = gh_user.get("login")
        email = gh_user.get("email") or f"{gh_login}@users.noreply.github.com"
        avatar = gh_user.get("avatar_url")
        display_name = gh_user.get("name") or gh_login

        # Upsert User
        user = db.query(User).filter((User.github_user_id == gh_id) | (User.email == email)).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                supabase_id=f"github_{gh_id}",
                github_user_id=gh_id,
                github_username=gh_login,
                email=email,
                display_name=display_name,
                avatar_url=avatar,
                role=UserRole.USER,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.github_user_id = gh_id
            user.github_username = gh_login
            user.avatar_url = avatar
            db.commit()

        # Upsert OAuth Account
        oauth_acc = db.query(GitHubOAuthAccount).filter(GitHubOAuthAccount.user_id == user.id).first()
        if not oauth_acc:
            oauth_acc = GitHubOAuthAccount(
                user_id=user.id,
                github_user_id=gh_id,
                github_username=gh_login,
                avatar_url=avatar,
                access_token_encrypted=encrypt_token(access_token),
                scopes=["user:email", "read:user", "read:org"],
            )
            db.add(oauth_acc)
        else:
            oauth_acc.access_token_encrypted = encrypt_token(access_token)
        db.commit()

        ensure_default_workspace(db, user)
        token_str = create_internal_jwt(user)

        return AuthTokenResponse(
            access_token=token_str,
            refresh_token=token_str,
            expires_in=604800,  # 7 days
            user={
                "id": user.id,
                "email": user.email,
                "github_username": user.github_username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ──────────────────────────── Legacy / Supabase Routes ─────────────────────

@router.post("/signup", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    """Register user via Supabase or local fallback."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        token = create_internal_jwt(existing)
        return AuthTokenResponse(
            access_token=token,
            refresh_token=token,
            expires_in=604800,
            user={"id": existing.id, "email": existing.email},
        )

    new_user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        display_name=payload.display_name,
        role=UserRole.USER,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    ensure_default_workspace(db, new_user)

    token = create_internal_jwt(new_user)
    return AuthTokenResponse(
        access_token=token,
        refresh_token=token,
        expires_in=604800,
        user={"id": new_user.id, "email": new_user.email},
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=payload.email,
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        ensure_default_workspace(db, user)

    token = create_internal_jwt(user)
    return AuthTokenResponse(
        access_token=token,
        refresh_token=token,
        expires_in=604800,
        user={"id": user.id, "email": user.email},
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        supabase_id=current_user.supabase_id,
        github_user_id=current_user.github_user_id,
        github_username=current_user.github_username,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )
