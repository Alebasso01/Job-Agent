"""
SQLAlchemy ORM models for SQLite database.
Defines database tables for the Job Hunt Agent.
"""

from sqlalchemy import Column, Integer, String, Text
from database import Base


class UserProfileDB(Base):
    """
    Database model representing the user's profile stored persistently.
    """

    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=True)
    target_roles = Column(Text, nullable=True)          # Stored as comma-separated strings
    hard_skills = Column(Text, nullable=True)
    nice_to_have_skills = Column(Text, nullable=True)
    locations_preferred = Column(Text, nullable=True)
    min_salary = Column(Integer, nullable=True)


def list_to_text(items: list[str]) -> str:
    if not items:
        return ""
    return ",".join(items)

def text_to_list(text: str) -> list[str]:
    if not text:
        return []
    return [item.strip() for item in text.split(",")]
