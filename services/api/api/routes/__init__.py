from api.routes.auth import router as auth_router
from api.routes.projects import router as projects_router
from api.routes.repositories import router as repositories_router
from api.routes.tasks import router as tasks_router
from api.routes.executions import router as executions_router
from api.routes.repo_intel import router as repo_intel_router

__all__ = [
    "auth_router", "projects_router", "repositories_router",
    "tasks_router", "executions_router", "repo_intel_router"
]

