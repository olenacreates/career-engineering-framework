"""LLM API client.

Isolates all external LLM/API communication so the rest of the package
has no direct dependency on the provider SDK. The extraction module calls
into this client; it never talks to the API directly.
"""


def complete(prompt, text):
    """Send `prompt` + `text` to the LLM and return the raw response.

    Kept intentionally generic so extraction owns the meaning of the
    request/response, while this module owns the transport.
    """
    raise NotImplementedError  # TODO(Step 2)
