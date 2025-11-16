# Job Hunt Agent

Job Hunt Agent is an automated system designed to collect job postings from multiple free data sources, evaluate them based on a customizable user profile, and deliver daily recommendations via Telegram.  
The project is fully cost-free, modular, and ready to be extended with manual LinkedIn ingestion via Telegram + n8n.

## Current Features

- FastAPI backend with health endpoint (`/health`)
- In-memory user profile model with `GET /profile` and `PUT /profile`
- In-memory job model with basic scoring logic and ingestion endpoints:
  - `POST /jobs/test-ingest` (single job)
  - `POST /jobs/ingest/batch` (multiple jobs)
  - `GET /jobs?min_score=...` (filter by score)
  - `GET /jobs/recommended?min_score=...&limit=...&since=...` (top matching jobs for digests)




## Roadmap (MVP)

1. Backend skeleton (FastAPI) ✔
2. User profile model + API ✔
3. Job model + scoring engine
4. Automatic job ingestion (Remotive, RemoteOK, Jooble, Adzuna)
5. Daily digest generator + Telegram delivery via n8n
6. Job application status tracking
7. Manual LinkedIn ingestion (Telegram → n8n → backend)


## Tech Stack

- **Backend**: Python + FastAPI
- **Orchestration**: n8n (self-hosted)
- **Database**: SQLite (MVP), later optional migration to Postgres
- **Notifications**: Telegram bot
- **Hosting**: Local or free-tier platforms (Render, Railway, Fly.io)

## Project Structure (initial)

