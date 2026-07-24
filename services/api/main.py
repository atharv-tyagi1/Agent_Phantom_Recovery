from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import logging
import redis.asyncio as redis

from core.config import settings
from db.session import get_db, Base, engine
import db.models  # Register all SQLAlchemy models
from core.security.security_middleware import SecurityHeadersMiddleware
from core.observability.logging_config import configure_structured_logging

configure_structured_logging()
logger = logging.getLogger(__name__)


# Run schema migrations & table creation safely
def init_db_schema():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            migration_sqls = [
                "ALTER TABLE repositories ADD COLUMN IF NOT EXISTS installation_id VARCHAR",
                "ALTER TABLE repositories ADD COLUMN IF NOT EXISTS github_repo_id BIGINT",
                "ALTER TABLE repositories ADD COLUMN IF NOT EXISTS full_name VARCHAR",
                "ALTER TABLE repositories ADD COLUMN IF NOT EXISTS clone_status VARCHAR DEFAULT 'pending'",
                "ALTER TABLE repositories ADD COLUMN IF NOT EXISTS last_commit_sha VARCHAR",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS github_user_id BIGINT",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS github_username VARCHAR",
                "ALTER TABLE users ALTER COLUMN supabase_id DROP NOT NULL",
                "ALTER TABLE projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR",
            ]
            for sql in migration_sqls:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                except Exception as e:
                    logger.debug(f"Column migration skipped or already exists: {e}")
    except Exception as e:
        logger.warning(f"DB schema migration check skipped: {e}")

init_db_schema()

app = FastAPI(title=settings.PROJECT_NAME)

# ── Security Middleware ──────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Correlation-ID Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    return response


# ── Lifecycle Events ─────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    app.state.redis = redis.from_url(settings.REDIS_URL)


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()


# ── Routers ──────────────────────────────────────────────────────────────────
from api.routes.probes import router as probes_router
from api.routes.auth import router as auth_router
from api.routes.workspaces import router as workspaces_router
from api.routes.github_app import router as github_app_router
from api.routes.webhooks import router as webhooks_router
from api.routes.monitoring import router as monitoring_router

from api.routes import (
    projects_router, repositories_router, tasks_router,
    executions_router, repo_intel_router
)
from api.routes.memory import router as memory_router
from api.routes.ws import router as ws_router

app.include_router(probes_router)
app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(github_app_router)
app.include_router(webhooks_router)
app.include_router(monitoring_router)
app.include_router(projects_router)
app.include_router(repositories_router)
app.include_router(tasks_router)
app.include_router(executions_router)
app.include_router(memory_router)
app.include_router(repo_intel_router)
app.include_router(ws_router)
