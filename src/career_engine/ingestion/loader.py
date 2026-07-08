"""Step 1 — Ingestion.

Read the Brain Dump from a DOCX file and return its text as a plain
string. The DOCX format is contained entirely within this module: the
rest of the pipeline receives text and stays unaware of the file format.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.opc.exceptions import PackageNotFoundError


def load_brain_dump(path) -> str:
    """Load the Brain Dump from a DOCX file and return its text.

    Validity is decided by the parser, not the filename: python-docx
    attempts to open the file and we translate a parse failure into a
    clear error. Paragraph text is joined with newlines.

    Raises FileNotFoundError if the file is missing and ValueError if it is
    not a valid DOCX document or contains no text — there is nothing to
    extract from an empty Brain Dump.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Brain Dump not found: {file_path}")

    try:
        document = Document(str(file_path))
    except PackageNotFoundError as exc:
        raise ValueError(f"Brain Dump is not a valid DOCX file: {file_path}") from exc

    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    if not text.strip():
        raise ValueError(f"Brain Dump is empty: {file_path}")

    return text
