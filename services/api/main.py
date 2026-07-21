from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import redis.asyncio as redis

from core.config import settings
from db.session import get_db
from api.routes.auth import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
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
app.include_router(auth_router)
from api.routes import projects_router, repositories_router, tasks_router, executions_router
app.include_router(projects_router)
app.include_router(repositories_router)
app.include_router(tasks_router)
app.include_router(executions_router)


# ── Health / Readiness ───────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
async def ready_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        await app.state.redis.ping()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
