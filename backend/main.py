"""
Backend entrypoint for the Job Hunt Agent.
This file initializes the FastAPI application and exposes:
- health-check endpoint
- user profile CRUD endpoints
- job ingestion and recommendation endpoints backed by SQLite.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import (
    Job,
    JobCreate,
    JobRead,
    JobsBatchCreate,
    UserProfile as UserProfileORM,
    UserProfileRead,
    UserProfileUpdate,
)
from app.services.scoring import compute_match_score


app = FastAPI(title="Job Hunt Agent API")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_or_create_profile(db: Session) -> UserProfileORM:
    """
    Load the single user profile from the database, creating a default one if missing.
    """
    profile = db.query(UserProfileORM).first()
    if profile is None:
        profile = UserProfileORM()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health")
def health_check():
    """
    Returns basic health status to confirm the backend is running.
    """
    return {"status": "ok", "message": "Job Hunt Agent backend is running"}


# ---------------------------------------------------------------------------
# User profile endpoints
# ---------------------------------------------------------------------------


@app.get("/profile", response_model=UserProfileRead)
def get_profile(db: Session = Depends(get_db)):
    """
    Return the stored user profile, creating an empty one if none exists.
    """
    profile = get_or_create_profile(db)
    return profile



@app.put("/profile", response_model=UserProfileRead)
def update_profile(payload: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    Update the user profile stored in the database.
    """
    profile = get_or_create_profile(db)
    data = payload.dict()

    for key, value in data.items():
        if key == "remote_only":
            setattr(profile, key, int(bool(value)))
        else:
            setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)

    return profile


# ---------------------------------------------------------------------------
# Job ingestion endpoints
# ---------------------------------------------------------------------------


@app.post("/jobs/test-ingest", response_model=JobRead)
def ingest_test_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """
    Ingest a single test job, compute its score, and store it in the database.
    """
    profile = get_or_create_profile(db)

    profile_data = {
        "full_name": profile.full_name,
        "target_roles": profile.target_roles or [],
        "skills": profile.skills or [],
        "preferred_locations": profile.preferred_locations or [],
        "bad_keywords": profile.bad_keywords or [],
        "remote_only": bool(profile.remote_only),
        "seniority_preference": profile.seniority_preference,
    }

    match_score = compute_match_score(job_data.dict(), profile_data)

    new_job = Job(
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description,
        url=job_data.url,
        source=job_data.source,
        source_id=job_data.source_id,
        published_at=job_data.published_at,
        match_score=match_score,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return JobRead.from_orm(new_job)


@app.post("/jobs/ingest/batch", response_model=List[JobRead])
def ingest_jobs_batch(payload: JobsBatchCreate, db: Session = Depends(get_db)):
    """
    Ingest multiple jobs, compute their scores, and save them to the database,
    skipping duplicates based on (source, source_id).
    """
    profile = get_or_create_profile(db)

    profile_data = {
        "full_name": profile.full_name,
        "target_roles": profile.target_roles or [],
        "skills": profile.skills or [],
        "preferred_locations": profile.preferred_locations or [],
        "bad_keywords": profile.bad_keywords or [],
        "remote_only": bool(profile.remote_only),
        "seniority_preference": profile.seniority_preference,
    }

    stored_jobs: List[Job] = []

    for job_data in payload.jobs:
        existing: Optional[Job] = None

        if job_data.source_id:
            existing = (
                db.query(Job)
                .filter(
                    Job.source == job_data.source,
                    Job.source_id == job_data.source_id,
                )
                .first()
            )

        if existing is not None:
            stored_jobs.append(existing)
            continue

        match_score = compute_match_score(job_data.dict(), profile_data)

        new_job = Job(
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            description=job_data.description,
            url=job_data.url,
            source=job_data.source,
            source_id=job_data.source_id,
            published_at=job_data.published_at,
            match_score=match_score,
        )

        db.add(new_job)
        stored_jobs.append(new_job)

    db.commit()
    for job in stored_jobs:
        db.refresh(job)

    return [JobRead.from_orm(j) for j in stored_jobs]


# ---------------------------------------------------------------------------
# Job listing endpoints
# ---------------------------------------------------------------------------


@app.get("/jobs", response_model=List[JobRead])
def list_jobs(
    min_score: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """
    Return all stored jobs, optionally filtered by a minimum match score.
    """
    query = db.query(Job)

    if min_score is not None:
        query = query.filter(Job.match_score >= min_score)

    jobs = query.all()
    return [JobRead.from_orm(j) for j in jobs]


@app.get("/jobs/recommended", response_model=List[JobRead])
def list_recommended_jobs(
    min_score: float = Query(default=0.5, ge=0.0, le=1.0),
    limit: int = Query(default=10, ge=1),
    since: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Return top jobs sorted by score, with optional date filter.
    """
    query = db.query(Job).filter(Job.match_score >= min_score)

    if since is not None:
        query = query.filter(Job.published_at >= since)

    query = query.order_by(Job.match_score.desc())

    jobs = query.limit(limit).all()
    return [JobRead.from_orm(j) for j in jobs]


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------


Base.metadata.create_all(bind=engine)
