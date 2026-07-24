from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Phantom Recovery API"
    ENVIRONMENT: str = "development"
    PRODUCTION_MODE: bool = False

    # Database (Supabase / Postgres)
    SUPABASE_DB_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # LLM & Vision Providers
    OPENROUTER_API_KEY: str = "placeholder-openrouter-key"
    ZENMUX_API_KEY: str = "placeholder-zenmux-key"
    NVIDIA_API_KEY: str = "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"
    NVIDIA_GLM_API_KEY: str = "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"
    NVIDIA_INTEGRATE_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    GLM_MODEL_NAME: str = "z-ai/glm-5.2"

    # Redis & Queues
    REDIS_URL: str = "redis://localhost:6379/0"
    WORKER_CONCURRENCY: int = 5
    RATE_LIMIT_PER_MINUTE: int = 100

    # Tool System Sandbox & Safeguards
    WORKSPACE_ROOT: str = "workspaces"
    EXECUTION_TIMEOUT_SECONDS: int = 300
    MAX_EXECUTION_STEPS: int = 15

    # Supabase Auth
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_KEY: str = "your-supabase-anon-key"
    SUPABASE_JWT_SECRET: str = "your-supabase-jwt-secret"

    # Hybrid GitHub Architecture Config
    GITHUB_CLIENT_ID: str = "placeholder-github-client-id"
    GITHUB_CLIENT_SECRET: str = "placeholder-github-client-secret"
    GITHUB_OAUTH_REDIRECT_URI: str = "http://localhost:3000/auth/github/callback"

    GITHUB_APP_ID: str = "placeholder-app-id"
    GITHUB_APP_PRIVATE_KEY_PATH: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: str = "phantom-webhook-secret-key"

    # Security Keys
    FERNET_ENCRYPTION_KEY: str = "dGVzdF9mZXJuZXRfa2V5XzMyX2J5dGVzX2xvbmdfc3RyPQ=="
    METRICS_AUTH_TOKEN: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
