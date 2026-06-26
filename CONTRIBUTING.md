# Contributing To HolyRail

HolyRail is early-stage software. Contributions should favor clear architecture,
testable algorithms, and non-destructive workflows over clever shortcuts.

## Development Setup

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run black --check .
```

RAW support is optional during development:

```bash
uv sync --extra dev --extra raw
```

## Contribution Principles

- Preserve original source images. HolyRail edits must be non-destructive.
- Keep packages focused. Avoid large catch-all modules.
- Add tests for behavior that changes analysis, correction curves, rendering, or
  project file compatibility.
- Prefer deterministic outputs for tests and CLI workflows.
- Document known limits honestly, especially for image-processing heuristics.

## Pull Requests

Before opening a pull request:

1. Run `uv run pytest`.
2. Run `uv run ruff check .`.
3. Run `uv run black --check .`.
4. Update docs, backlog, or sprint notes when behavior or priorities change.

For algorithm changes, include the sequence type tested, expected behavior, and
how you verified that long-term scene evolution was not normalized away.

## Sample Data

Small generated fixtures may live in the repository. Large RAW sequences should
stay outside Git and be referenced by documentation or test-generation scripts.
