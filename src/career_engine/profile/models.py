"""Career Profile data model — the single source of truth (ADR-001).

Plain dataclasses only: these are data containers with no behavior.
Defined with the stdlib (no Pydantic in Sprint 1) to keep dependencies
minimal.

    CareerProfile
      - Metadata
      - Skills
      - Achievements
      - Hero Stories

Conversion to/from plain dicts lives in serialization.py so the models
stay free of logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metadata:
    """High-level facts about the professional."""

    name: str = ""
    headline: str = ""
    location: str = ""
    email: str = ""
    summary: str = ""
    target_roles: list[str] = field(default_factory=list)


@dataclass
class Skill:
    """A single professional skill, optionally grouped by category."""

    name: str
    category: str = ""


@dataclass
class Achievement:
    """A concrete accomplishment, its context, and its impact."""

    title: str
    context: str = ""
    impact: str = ""


@dataclass
class HeroStory:
    """A narrative career story in situation / action / result form."""

    title: str
    situation: str = ""
    action: str = ""
    result: str = ""


@dataclass
class CareerProfile:
    """The single source of truth generated from a Brain Dump."""

    metadata: Metadata = field(default_factory=Metadata)
    skills: list[Skill] = field(default_factory=list)
    achievements: list[Achievement] = field(default_factory=list)
    hero_stories: list[HeroStory] = field(default_factory=list)
    source_document: str = ""
