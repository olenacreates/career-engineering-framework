"""Step 2 — Extraction.

The core MVP step. Transforms raw Brain Dump text into a structured
CareerProfile. Focuses only on the transformation: it delegates all API
communication to career_engine.llm_client and loads its instruction from
career_engine.prompts.
"""


def extract_profile(brain_dump):
    """Transform raw Brain Dump text into a CareerProfile."""
    raise NotImplementedError  # TODO(Step 2)
