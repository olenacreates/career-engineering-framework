"""Prompt artifacts.

Prompts are first-class engineering artifacts and live as external Markdown
files in this folder so they can be reviewed, edited, and versioned
independently of the Python code. This module exposes helpers to load them.
"""

from __future__ import annotations

from pathlib import Path


def load_prompt(name: str) -> str:
    """Return the text of the prompt Markdown file `name` in this folder.

    `name` is a filename relative to this package (e.g.
    ``"career_profile_prompt.md"``). Raises FileNotFoundError if it is missing.
    """
    path = Path(__file__).parent / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
