from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.session import get_db
from core.config import settings

router = APIRouter(tags=["Operational Probes"])


@router.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    """Liveness probe: Returns 200 OK without evaluating downstream DB/Redis dependencies."""
    return {"status": "ok", "service": "agent-phantom-api"}


@router.get("/livez", status_code=status.HTTP_200_OK)
def livez():
    """Liveness probe for Kubernetes pod restart checks."""
    return {"status": "alive"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readyz(request: Request, db: Session = Depends(get_db)):
    """Readiness probe: Validates database connection pool and Redis ping."""
    errors = {}

    # Check Database
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        errors["database"] = str(e)

    # Check Redis
    try:
        redis_client = getattr(request.app.state, "redis", None)
        if redis_client:
            await redis_client.ping()
    except Exception as e:
        errors["redis"] = str(e)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "errors": errors}
        )

    return {"status": "ready"}


@router.get("/metrics", status_code=status.HTTP_200_OK)
def metrics(x_metrics_token: str | None = Header(None, alias="X-Metrics-Token")):
    """
    Prometheus metrics endpoint. Protected by METRICS_AUTH_TOKEN check.
    """
    metrics_token = getattr(settings, "METRICS_AUTH_TOKEN", None)
    if metrics_token and x_metrics_token != metrics_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Metrics access denied")

    # Lightweight Prometheus text format metrics
    prometheus_data = (
        "# HELP phantom_system_up System operational status\n"
        "# TYPE phantom_system_up gauge\n"
        "phantom_system_up 1\n"
    )
    return Response(content=prometheus_data, media_type="text/plain")
