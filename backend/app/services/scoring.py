"""
Scoring engine for computing a match score between a job and a user profile.

The main entry point is `compute_match_score(job, profile)` which returns
a float between 0.0 and 1.0.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Iterable, Mapping, Optional, Sequence, Set


WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def _normalize(text: Optional[str]) -> str:
    """Return a normalized lowercase string or empty string if None."""
    if not text:
        return ""
    return text.lower()


def _tokenize(text: str) -> Set[str]:
    """Split text into a set of lowercase tokens."""
    return {match.group(0).lower() for match in WORD_RE.finditer(text or "")}


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    """Return True if any keyword appears in text (case-insensitive)."""
    t = _normalize(text)
    return any(k.lower() in t for k in keywords)


def _count_keywords(tokens: Set[str], keywords: Iterable[str]) -> int:
    """Count how many distinct keywords appear in the tokens set."""
    lowered = {k.lower() for k in keywords}
    return sum(1 for k in lowered if k in tokens)


def _parse_seniority_from_title(title: str) -> Optional[str]:
    """Extract a simple seniority level from a job title if present."""
    title_l = _normalize(title)

    if "intern" in title_l or "trainee" in title_l:
        return "intern"
    if "junior" in title_l or " jr " in title_l or " jr." in title_l:
        return "junior"
    if "lead" in title_l or "staff" in title_l or "principal" in title_l:
        return "lead"
    if "senior" in title_l or " sr " in title_l or " sr." in title_l:
        return "senior"
    if "mid" in title_l or "middle" in title_l:
        return "mid"

    return None


def _seniority_to_score(level: Optional[str]) -> int:
    """Map seniority string to an ordinal value for comparison."""
    mapping = {
        "intern": 0,
        "junior": 1,
        "mid": 2,
        "senior": 3,
        "lead": 4,
        "principal": 4,
    }
    if level is None:
        return -1
    return mapping.get(level, -1)


def _location_score(job_location: str, preferred_locations: Sequence[str], remote_only: bool) -> float:
    """Compute a location score between 0 and 1."""
    loc = _normalize(job_location)
    if not loc:
        return 0.2  # unknown location, small neutral score

    is_remote = "remote" in loc

    if remote_only and not is_remote:
        return 0.0

    if preferred_locations:
        for pref in preferred_locations:
            if pref and pref.lower() in loc:
                return 1.0

        if remote_only and is_remote:
            return 0.8

        return 0.3 if is_remote else 0.1

    return 0.6 if is_remote else 0.4


def _recency_score(published_at: Optional[datetime], max_days: int = 60) -> float:
    """Compute a score between 0 and 1 based on how recent the job is."""
    if published_at is None:
        return 0.5

    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    days = (now - published_at).days

    if days <= 0:
        return 1.0
    if days >= max_days:
        return 0.0

    return max(0.0, 1.0 - (days / max_days))


def compute_match_score(
    job: Mapping[str, object],
    profile: Mapping[str, object],
) -> float:
    """
    Compute a match score between 0.0 and 1.0 for a job and a user profile.

    The score combines title, skills, location, seniority, and recency signals.
    """
    title = _normalize(str(job.get("title") or ""))
    description = _normalize(str(job.get("description") or ""))
    location = _normalize(str(job.get("location") or ""))

    published_at = job.get("published_at")
    if isinstance(published_at, str):
        try:
            published_at = datetime.fromisoformat(published_at)
        except ValueError:
            published_at = None

    target_roles = profile.get("target_roles") or []
    skills = profile.get("skills") or []
    preferred_locations = profile.get("preferred_locations") or []
    remote_only = bool(profile.get("remote_only") or False)
    seniority_pref = profile.get("seniority_preference")
    bad_keywords = profile.get("bad_keywords") or []

    title_tokens = _tokenize(title)
    desc_tokens = _tokenize(description)
    all_tokens = title_tokens | desc_tokens

    # 1) Title score
    if target_roles:
        title_matches = _count_keywords(title_tokens, target_roles)
        title_score = min(1.0, title_matches / max(1, len(target_roles)))
    else:
        title_score = 0.5

    # 2) Skill score
    if skills:
        skill_matches = _count_keywords(all_tokens, skills)
        skill_score = min(1.0, skill_matches / max(1, len(skills)))
    else:
        skill_score = 0.5

    # 3) Location score
    location_score = _location_score(location, preferred_locations, remote_only)

    # 4) Seniority score
    seniority_job = _parse_seniority_from_title(title)
    if seniority_pref:
        s_job = _seniority_to_score(seniority_job)
        s_pref = _seniority_to_score(seniority_pref)
        if s_job == -1 or s_pref == -1:
            seniority_score = 0.5
        else:
            diff = abs(s_job - s_pref)
            if diff == 0:
                seniority_score = 1.0
            elif diff == 1:
                seniority_score = 0.7
            elif diff == 2:
                seniority_score = 0.4
            else:
                seniority_score = 0.1
    else:
        seniority_score = 0.5

    # 5) Recency score
    recency_score = _recency_score(published_at)

    # Weighted combination
    w_title = 3.0
    w_skills = 3.0
    w_location = 1.5
    w_seniority = 1.0
    w_recency = 1.0

    weighted = (
        w_title * title_score
        + w_skills * skill_score
        + w_location * location_score
        + w_seniority * seniority_score
        + w_recency * recency_score
    )
    base_score = weighted / (w_title + w_skills + w_location + w_seniority + w_recency)

    # Bad keywords penalty
    if bad_keywords and _contains_any(title + " " + description, bad_keywords):
        base_score *= 0.3

    return float(round(max(0.0, min(1.0, base_score)), 4))
