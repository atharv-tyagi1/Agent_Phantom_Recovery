from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Phantom Recovery API"

    # Database (Supabase / Postgres)
    SUPABASE_DB_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # LLM Providers
    OPENROUTER_API_KEY: str = "placeholder-openrouter-key"
    ZENMUX_API_KEY: str = "placeholder-zenmux-key"

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
