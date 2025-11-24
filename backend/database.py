"""
Database configuration using SQLAlchemy.
Supports both SQLite (default, for local dev) and PostgreSQL via DATABASE_URL.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# If DATABASE_URL is not set, fall back to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./job_hunt.db")

# Extra args only for SQLite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create engine
engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)

# Base class for ORM models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency used by FastAPI to obtain a clean DB session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
