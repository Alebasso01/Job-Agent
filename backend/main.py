"""
Backend entrypoint for the Job Hunt Agent.
This file initializes the FastAPI application and exposes health-check,
user profile, and basic in-memory job ingestion and scoring routes.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Job Hunt Agent API")


class UserProfile(BaseModel):
    """
    Represents the core preferences of the job seeker.
    """
    full_name: Optional[str] = None
    target_roles: List[str] = Field(default_factory=list)
    hard_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    locations_preferred: List[str] = Field(default_factory=list)
    min_salary: Optional[int] = None


class JobCreate(BaseModel):
    """
    Represents the minimal input required to create a job entry.
    """
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: str
    source_id: Optional[str] = None
    published_at: Optional[datetime] = None


class Job(BaseModel):
    """
    Represents a normalized job posting enriched with a match score.
    """
    id: str
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    url: Optional[str]
    source: str
    source_id: Optional[str]
    published_at: Optional[datetime]
    match_score: float


class JobBatchIngestRequest(BaseModel):
    """
    Represents a batch of jobs to be ingested in a single request.
    """
    jobs: List[JobCreate]


current_profile: Optional[UserProfile] = None
job_store: List[Job] = []


@app.get("/health")
def health_check():
    """
    Returns basic health status to confirm the backend is running.
    """
    return {"status": "ok", "message": "Job Hunt Agent backend is running"}


@app.get("/profile", response_model=UserProfile)
def get_profile():
    """
    Returns the currently stored user profile or an empty default profile.
    """
    global current_profile

    if current_profile is None:
        current_profile = UserProfile()

    return current_profile


@app.put("/profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    """
    Stores or updates the user profile used for job matching.
    """
    global current_profile

    current_profile = profile
    return current_profile


def compute_match_score(job: JobCreate, profile: UserProfile) -> float:
    """
    Computes a basic match score between a job and the user profile.
    """
    if not profile:
        return 0.0

    score = 0.0

    title_lower = job.title.lower()
    description_lower = (job.description or "").lower()
    location_lower = (job.location or "").lower()

    if profile.target_roles:
        for role in profile.target_roles:
            role_lower = role.lower()
            if role_lower in title_lower:
                score += 0.4
                break

    if profile.hard_skills:
        hard_matches = 0
        for skill in profile.hard_skills:
            skill_lower = skill.lower()
            if skill_lower in title_lower or skill_lower in description_lower:
                hard_matches += 1

        skill_ratio = hard_matches / len(profile.hard_skills)
        score += min(skill_ratio * 0.4, 0.4)

    if profile.nice_to_have_skills:
        nice_matches = 0
        for skill in profile.nice_to_have_skills:
            skill_lower = skill.lower()
            if skill_lower in title_lower or skill_lower in description_lower:
                nice_matches += 1

        nice_ratio = nice_matches / len(profile.nice_to_have_skills)
        score += min(nice_ratio * 0.15, 0.15)

    if profile.locations_preferred and location_lower:
        for location in profile.locations_preferred:
            if location.lower() in location_lower:
                score += 0.05
                break

    return max(0.0, min(score, 1.0))


@app.post("/jobs/test-ingest", response_model=Job)
def ingest_test_job(job_data: JobCreate):
    """
    Ingests a single test job, computes its score, and stores it in memory.
    """
    global current_profile, job_store

    if current_profile is None:
        current_profile = UserProfile()

    match_score = compute_match_score(job_data, current_profile)

    job = Job(
        id=str(uuid4()),
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

    job_store.append(job)
    return job


@app.post("/jobs/ingest/batch", response_model=List[Job])
def ingest_jobs_batch(batch: JobBatchIngestRequest):
    """
    Ingests multiple jobs, computes their scores, and stores them in memory.
    """
    global current_profile, job_store

    if current_profile is None:
        current_profile = UserProfile()

    created_jobs: List[Job] = []

    for job_data in batch.jobs:
        match_score = compute_match_score(job_data, current_profile)

        job = Job(
            id=str(uuid4()),
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

        job_store.append(job)
        created_jobs.append(job)

    return created_jobs


@app.get("/jobs", response_model=List[Job])
def list_jobs(min_score: Optional[float] = Query(default=None, ge=0.0, le=1.0)):
    """
    Returns all stored jobs, optionally filtered by a minimum match score.
    """
    if min_score is None:
        return job_store

    return [job for job in job_store if job.match_score >= min_score]


@app.get("/jobs/recommended", response_model=List[Job])
def list_recommended_jobs(
    min_score: float = Query(default=0.5, ge=0.0, le=1.0),
    limit: int = Query(default=10, ge=1),
    since: Optional[datetime] = Query(default=None),
):
    """
    Returns the top matching jobs sorted by score and optionally filtered by date.
    """
    filtered = [job for job in job_store if job.match_score >= min_score]

    if since is not None:
        filtered = [
            job for job in filtered
            if job.published_at is not None and job.published_at >= since
        ]

    filtered.sort(key=lambda j: j.match_score, reverse=True)
    return filtered[:limit]
