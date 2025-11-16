"""
Backend entrypoint for the Job Hunt Agent.
This file initializes the FastAPI application and exposes basic health-check routes.
"""

from fastapi import FastAPI

app = FastAPI(title="Job Hunt Agent API")


@app.get("/health")
def health_check():
    """
    Returns basic health status to confirm the backend is running.
    """
    return {"status": "ok", "message": "Job Hunt Agent backend is running"}
