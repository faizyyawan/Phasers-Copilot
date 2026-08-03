"""Document indexing entry point.

Not implemented yet: this module will embed chunks and index them in Qdrant.
"""


def main() -> None:
    """Report that Qdrant indexing has not been built yet."""
    message = (
        "Qdrant indexing is not implemented yet. "
        "Next step: persist embedded knowledge chunks into data/qdrant/."
    )
    raise SystemExit(message)


if __name__ == "__main__":
    main()
