"""Pipeline orchestrator.

The single place that knows the workflow's step order:

    load -> extract -> populate source_document -> serialize -> write

Receives explicit input and output paths and orchestrates the stages. It does
not decide where files live (that is the entry point's concern), and each stage
stays unaware of the others.
"""

from __future__ import annotations

import json
from pathlib import Path

from career_engine.extraction.extractor import extract_profile
from career_engine.ingestion.loader import load_brain_dump
from career_engine.profile.serialization import to_dict


def run(input_path, output_path) -> None:
    """Extract a Career Profile from the Brain Dump and write it as JSON.

    Reads the Brain Dump at `input_path`, extracts a CareerProfile, records the
    source filename as provenance, serializes it, and writes the JSON to
    `output_path`.
    """
    brain_dump = load_brain_dump(input_path)

    profile = extract_profile(brain_dump)
    profile.source_document = Path(input_path).name

    data = to_dict(profile)

    Path(output_path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
