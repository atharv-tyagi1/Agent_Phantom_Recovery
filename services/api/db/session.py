from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Hardened connection pool settings
db_pool_size = getattr(settings, "DB_POOL_SIZE", 20)
db_max_overflow = getattr(settings, "DB_MAX_OVERFLOW", 10)

engine = create_engine(
    settings.SUPABASE_DB_URL,
    pool_size=db_pool_size,
    max_overflow=db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
