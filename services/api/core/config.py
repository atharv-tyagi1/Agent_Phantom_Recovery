from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Phantom Recovery API"

    # Database (Supabase / Postgres)
    SUPABASE_DB_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # LLM & Vision Providers
    OPENROUTER_API_KEY: str = "placeholder-openrouter-key"
    ZENMUX_API_KEY: str = "placeholder-zenmux-key"
    NVIDIA_API_KEY: str = "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"
    NVIDIA_GLM_API_KEY: str = "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"
    NVIDIA_INTEGRATE_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    GLM_MODEL_NAME: str = "z-ai/glm-5.2"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Tool System Sandbox
    WORKSPACE_ROOT: str = "workspaces"

    # Supabase Auth
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_KEY: str = "your-supabase-anon-key"
    SUPABASE_JWT_SECRET: str = "your-supabase-jwt-secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
