"""Step 2 — Extraction.

The core MVP step. Transforms raw Brain Dump text into a structured
CareerProfile. Focuses only on the transformation: it delegates all API
communication to career_engine.llm_client and loads its instruction from
career_engine.prompts.
"""

from __future__ import annotations

import json

from career_engine.llm_client import generate_text
from career_engine.profile.models import CareerProfile
from career_engine.profile.serialization import from_dict
from career_engine.prompts import load_prompt

PROMPT_NAME = "career_profile_prompt.md"
BRAIN_DUMP_PLACEHOLDER = "{{BRAIN_DUMP}}"


def extract_profile(brain_dump: str) -> CareerProfile:
    """Transform raw Brain Dump text into a CareerProfile.

    Loads the extraction prompt, injects the Brain Dump, sends it to the LLM,
    and parses the JSON response into a CareerProfile.

    Raises:
        LLMError: If the LLM request fails (propagated from llm_client).
        ValueError: If the response is not valid JSON or does not match the
            Career Profile schema.
    """
    template = load_prompt(PROMPT_NAME)
    # Literal replacement, not str.format: the prompt contains { } braces.
    prompt = template.replace(BRAIN_DUMP_PLACEHOLDER, brain_dump)

    raw_response = generate_text(prompt)

    data = _parse_json_object(raw_response)

    # Defensive: the prompt asks for a strict shape, but we never trust the
    # model to have obeyed. Turn a schema mismatch into a legible error rather
    # than a cryptic TypeError/AttributeError from deserialization.
    try:
        return from_dict(data)
    except (TypeError, AttributeError) as exc:
        raise ValueError(
            f"LLM output did not match the Career Profile schema: {exc}"
        ) from exc


def _parse_json_object(raw: str) -> dict:
    """Extract and parse the single JSON object from a raw LLM response.

    Tolerant of a model that wraps the JSON in prose or a Markdown code fence:
    we take everything from the first ``{`` to the last ``}``.
    """
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(
            f"LLM response did not contain a JSON object: {raw[:200]!r}"
        )

    snippet = raw[start : end + 1]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("LLM response JSON was not an object")

    return data
