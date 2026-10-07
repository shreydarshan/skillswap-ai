from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# SQLAlchemy database engine configured with DATABASE_URL
# pool_pre_ping checks database connection liveness before executing queries
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# Database session factory for dependency injection
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models in SkillSwap AI.
    Future models (User, Skill, SwapRequest, Rating) will inherit from this base class.
    """
    pass


def get_db() -> Generator:
    """
    FastAPI Dependency that yields a SQLAlchemy database session per request
    and ensures it is cleanly closed after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
