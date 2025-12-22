# Agentic-RAG-Ingestion
a standalone, black-box ingestion service that will later integrate into a larger Agentic-RAG-Platform.

## Architecture & Integration Notes

The following documents provide non-binding guidance to support
independent development and future integration:

- ARCHITECTURE_NOTES.md
- INGESTION_RETRIEVAL_EXPECTATIONS.md
- INGESTION_INTEGRATION_OVERVIEW.md

```
## Code Quality

This project enforces code quality via pre-commit hooks.

Before committing, ensure you have hooks installed:

```
uv run pre-commit install
````

To run all checks manually:

```
pre-commit run --all-files
```

Checks include:

* Ruff (linting)
* Pyright (static typing)
* Formatting & whitespace validation

````
