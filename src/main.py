"""Application entry point.

Owns the application's launch concerns:
  - define the entry point;
  - provide the input/output path conventions;
  - invoke the pipeline;
  - present user-facing success and error messages.

Boundary: main owns "where" (the file locations); the pipeline owns "what
order" (the workflow). This file stays thin — it wires up and runs the
pipeline and never contains pipeline logic itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

from career_engine.llm_client import LLMError
from career_engine.pipeline import run

INPUT_PATH = Path("input/brain_dump.docx")
OUTPUT_PATH = Path("output/career_profile.json")


def main() -> None:
    """Run Brain Dump -> Career Profile extraction and report the result."""
    try:
        run(INPUT_PATH, OUTPUT_PATH)
    except (FileNotFoundError, ValueError, LLMError) as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Career Profile written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
