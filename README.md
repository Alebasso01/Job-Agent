# Job Hunt Agent

Job Hunt Agent is a lightweight backend that stores job postings from free external APIs, scores them using a customizable user profile, and exposes endpoints for external automations (n8n) to ingest jobs and generate daily Telegram digests.

---

## System Flow Overview

1. **User Profile Setup**  
   The user defines roles, skills, and locations. These preferences guide the job scoring.

2. **Job Ingestion (via n8n)**  
   n8n fetches jobs from free APIs, maps them, and sends them to the backend in batch.

3. **Scoring & Storage**  
   Each job is scored against the user profile and saved in SQLite (duplicates skipped).

4. **Job Retrieval**  
   External automations request recommended jobs to build daily/weekly digests.

5. **Notifications**  
   n8n sends top jobs to the user via Telegram.

---

## Feature Checklist

### ⭐ Core Backend

| Feature | Status |
|--------|--------|
| FastAPI backend skeleton | ✔️ |
| SQLite database + SQLAlchemy ORM | ✔️ |
| User profile CRUD (`GET /profile`, `PUT /profile`) | ✔️ |
| Job ingestion endpoints (`test-ingest`, `batch ingest`) | ✔️ |
| Job scoring engine (v1 basic) | ✔️ |
| Recommended jobs (`/jobs/recommended`) | ✔️ |

---

### 🔄 Integrations & Automations

| Feature | Status |
|--------|--------|
| n8n workflow for Remotive ingestion | ✔️ |
| Mapping & batch send to backend | ✔️ |
| Daily job retrieval for digest | ⏳ |
| Telegram delivery via bot | ⏳ |
| Ingestion from additional sources (RemoteOK, Adzuna, Jooble) | ⏳ |
| Manual LinkedIn ingestion (Telegram → n8n → backend) | ⏳ |

---

### 📈 Scoring & Intelligence

| Feature | Status |
|--------|--------|
| Basic scoring (roles, skills, location) | ✔️ |
| Weight tuning / configurable scoring | ⏳ |
| AI-based job ranking | ⏳ |

---

### 🗂 Job Management

| Feature | Status |
|--------|--------|
| Job application status (applied, interview, rejected...) | ⏳ |
| Notes & reminders | ⏳ |
| Filtering by status | ⏳ |

---

## Tech Stack

- **Backend:** Python + FastAPI  
- **Database:** SQLite + SQLAlchemy  
- **Automations:** n8n (self-hosted)  
- **Notifications:** Telegram bot  

