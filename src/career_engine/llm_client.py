"""LLM API client.

Isolates all Anthropic API communication so the rest of the package has no
direct dependency on the provider SDK. Other modules call `generate_text`;
they never import `anthropic` or handle its exceptions directly.

This module knows nothing about Career Profiles or the pipeline — it only
turns a text prompt into generated text.
"""

from __future__ import annotations

import os

import anthropic
from dotenv import load_dotenv

MODEL = "claude-opus-4-8"
MAX_TOKENS = 4096


class LLMError(RuntimeError):
    """Raised when the LLM cannot produce a response.

    Wraps provider-specific failures (missing key, authentication, network,
    API errors) in a single type so callers stay decoupled from the SDK.
    """


def generate_text(prompt: str) -> str:
    """Send a prompt to Claude and return the generated text.

    Args:
        prompt: The text prompt to send to the model.

    Returns:
        The model's response as plain text.

    Raises:
        LLMError: If ``ANTHROPIC_API_KEY`` is missing, authentication fails,
            or the API request cannot be completed.
    """
    # MVP scope: config is loaded and a fresh client is built on every call.
    # This is intentionally minimal — the pipeline makes exactly one LLM call
    # per run, so there is nothing to reuse or amortize.
    #
    # Revisit this the moment a single run issues MORE THAN ONE LLM call
    # (e.g. generating multiple artifacts, retries, or batch processing). At
    # that point:
    #   - move load_dotenv() to the application entry point (main.py) so config
    #     is loaded once at startup rather than on every call, and
    #   - make the Anthropic client a lazily cached singleton (or inject it) so
    #     the HTTP connection pool is reused across calls instead of rebuilt.
    # Until then, doing so would be premature optimization.
    load_dotenv()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add "
            "your Anthropic API key."
        )

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise LLMError(
            "Anthropic authentication failed. Check that ANTHROPIC_API_KEY is valid."
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise LLMError(
            "Could not reach the Anthropic API. Check your network connection."
        ) from exc
    except anthropic.APIError as exc:
        raise LLMError(f"Anthropic API request failed: {exc}") from exc

    return "".join(block.text for block in response.content if block.type == "text")
