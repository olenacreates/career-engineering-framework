"""Pipeline orchestrator.

The single place that knows the step order:

    load (ingestion) -> extract (extraction) -> generate (generation)

Reads the Brain Dump from input/ and writes the Career Profile and
Master CV to output/. Each stage stays unaware of the others.
"""


def run():
    """Run the full Brain Dump -> Career Profile -> Master CV pipeline."""
    raise NotImplementedError  # TODO(Step 2)
