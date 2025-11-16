"""
Database configuration using SQLAlchemy + SQLite.
This module initializes the SQLite engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite:///./job_hunt.db"

# Create the engine that communicates with the SQLite database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite + FastAPI
)

# Base class for our ORM models
Base = declarative_base()

# Factory for database sessions
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
