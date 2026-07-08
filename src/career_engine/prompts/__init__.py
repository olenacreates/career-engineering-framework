"""Prompt artifacts.

Prompts are first-class engineering artifacts and live as external Markdown
files in this folder so they can be reviewed, edited, and versioned
independently of the Python code. This module exposes helpers to load them.
"""


def load_prompt(name):
    """Return the text of the prompt Markdown file `name` in this folder."""
    raise NotImplementedError  # TODO(Step 2)
