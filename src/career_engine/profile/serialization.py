"""(De)serialization for the Career Profile.

Kept separate from models.py so the dataclasses stay plain data
containers. Converts a CareerProfile to/from a plain dict — used to save
the profile to output/ as JSON and to rebuild it from the extractor's
parsed LLM output.
"""

from __future__ import annotations

from dataclasses import asdict

from career_engine.profile.models import (
    Achievement,
    CareerProfile,
    HeroStory,
    Metadata,
    Skill,
)


def to_dict(profile: CareerProfile) -> dict:
    """Return a plain, JSON-serializable dict for `profile`."""
    return asdict(profile)


def from_dict(data: dict) -> CareerProfile:
    """Build a CareerProfile from a plain dict (e.g. parsed LLM JSON).

    Lenient by design: unknown keys are ignored and missing keys fall back
    to defaults, so LLM output is tolerated rather than rejected.
    """
    metadata = Metadata(**_only_known(Metadata, data.get("metadata", {})))
    skills = [Skill(**_only_known(Skill, s)) for s in data.get("skills", [])]
    achievements = [
        Achievement(**_only_known(Achievement, a))
        for a in data.get("achievements", [])
    ]
    hero_stories = [
        HeroStory(**_only_known(HeroStory, h)) for h in data.get("hero_stories", [])
    ]
    return CareerProfile(
        metadata=metadata,
        skills=skills,
        achievements=achievements,
        hero_stories=hero_stories,
        source_document=data.get("source_document", ""),
    )


def _only_known(cls, values: dict) -> dict:
    """Keep only the keys that are fields of dataclass `cls`."""
    allowed = {f.name for f in cls.__dataclass_fields__.values()}
    return {k: v for k, v in values.items() if k in allowed}
