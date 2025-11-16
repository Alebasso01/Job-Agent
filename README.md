# Job Hunt Agent

Job Hunt Agent is an automated system designed to collect job postings from multiple free data sources, evaluate them based on a customizable user profile, and deliver daily recommendations via Telegram.  
The project is fully cost-free, modular, and ready to be extended with manual LinkedIn ingestion via Telegram + n8n.

## Current Features

- FastAPI backend with health endpoint (`/health`)
- Fully documented and structured backend in English
- Ready-to-extend architecture for job ingestion, scoring, and notifications

## Roadmap (MVP)

1. Backend skeleton (FastAPI) ✔
2. User profile model + API
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

