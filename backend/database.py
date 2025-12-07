"""
Database configuration using SQLAlchemy.

Supporta sia:
- SQLite locale (default, per sviluppo)
- PostgreSQL via DATABASE_URL (es. Neon, Supabase, Render, ecc.)

Le credenziali vengono lette da variabili d'ambiente,
caricate automaticamente da un file .env in locale.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carica le variabili dal file .env (solo in locale)
load_dotenv()

# Se DATABASE_URL non è settata, usa SQLite locale
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./job_hunt.db")

# Normalizza l'URL in caso di formato postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Argomenti extra solo per SQLite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Crea l'engine
engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

# Base per i modelli ORM
Base = declarative_base()

# Factory per le sessioni DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency per FastAPI: crea e chiude una sessione DB per ogni richiesta.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
