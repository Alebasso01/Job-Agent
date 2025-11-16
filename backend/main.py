"""
Backend entrypoint for the Job Hunt Agent.
This file initializes the FastAPI application and exposes health-check and user profile routes.
"""

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Job Hunt Agent API")


class UserProfile(BaseModel):
    """
    Represents the core preferences of the job seeker.
    """
    full_name: Optional[str] = None
    target_roles: list[str] = Field(default_factory=list)
    hard_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    locations_preferred: list[str] = Field(default_factory=list)
    min_salary: Optional[int] = None


current_profile: Optional[UserProfile] = None


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
