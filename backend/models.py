"""
Database models and Pydantic schemas for the Job Hunt Agent backend.

This module defines:
- SQLAlchemy ORM models: Job, UserProfile
- Pydantic schemas for API I/O.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from database import Base


# ---------------------------------------------------------------------------
# SQLAlchemy ORM models
# ---------------------------------------------------------------------------


class Job(Base):
    """
    ORM model representing a single job offer stored in the database.
    """

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)

    source = Column(String, nullable=False)       # e.g. "remotive", "linkedin_manual"
    source_id = Column(String, nullable=False)    # ID provided by the source

    published_at = Column(DateTime, nullable=True)
    match_score = Column(Float, nullable=False, default=0.0)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class UserProfile(Base):
    """
    ORM model representing the user's job preferences and skills.

    This table is expected to have a single row (id = 1) in this project.
    """

    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True, default=1)

    full_name = Column(String, nullable=True)

    # Stored as JSON arrays in SQLite
    target_roles = Column(JSON, nullable=False, default=list)         # ["backend", "python"]
    skills = Column(JSON, nullable=False, default=list)               # ["python", "fastapi"]
    preferred_locations = Column(JSON, nullable=False, default=list)  # ["remote", "italy"]
    bad_keywords = Column(JSON, nullable=False, default=list)         # ["wordpress"]

    remote_only = Column(Integer, nullable=False, default=0)          # 0 = False, 1 = True
    seniority_preference = Column(String, nullable=True)              # "junior" | "mid" | "senior" | ...

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


# ---------------------------------------------------------------------------
# Pydantic schemas for Job
# ---------------------------------------------------------------------------


class JobBase(BaseModel):
    """
    Base fields shared by job-related schemas.
    """

    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: str
    source: str
    source_id: str
    published_at: Optional[datetime] = None


class JobCreate(JobBase):
    """
    Schema used when ingesting a new job from an external source.
    """

    pass


class JobRead(JobBase):
    """
    Schema returned by API endpoints when reading job objects.
    """

    id: str
    match_score: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class JobsBatchCreate(BaseModel):
    """
    Schema used by /jobs/ingest/batch endpoint to ingest multiple jobs.
    """

    jobs: List[JobCreate]


# ---------------------------------------------------------------------------
# Pydantic schemas for UserProfile
# ---------------------------------------------------------------------------


class UserProfileBase(BaseModel):
    """
    Base fields shared by user profile schemas.
    """

    full_name: Optional[str] = None

    target_roles: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    bad_keywords: List[str] = Field(default_factory=list)

    remote_only: bool = False
    seniority_preference: Optional[str] = Field(
        default=None,
        description="Desired seniority level, e.g. 'junior', 'mid', 'senior', 'lead'.",
    )


class UserProfileUpdate(UserProfileBase):
    """
    Schema used to update the active user profile.
    """

    pass


class UserProfileRead(UserProfileBase):
    """
    Schema returned by API endpoints when reading the user profile.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
