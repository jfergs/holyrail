# HolyRail

HolyRail is an open source computational photography platform for professional RAW timelapse processing and future image-sequence research workflows.

The phase-one implementation focuses on a non-destructive sequence workflow:

1. Analyze image sequences.
2. Build luminance, histogram, exposure, color, and white-balance metrics.
3. Persist a JSON project file without touching originals.
4. Generate preview frames.
5. Render processed frames and optionally assemble video with FFmpeg.

## Quick Start

```bash
uv sync --extra dev
uv run holyrail analyze /path/to/frames --project holyrail-project.json
uv run holyrail inspect --project holyrail-project.json
uv run holyrail report --project holyrail-project.json --output analysis-report.json
uv run holyrail preview --project holyrail-project.json --output previews
uv run holyrail render --project holyrail-project.json --output rendered --video output.mp4
```

RAW decoding uses `rawpy` when installed. Common bitmap formats are supported through OpenCV for development and tests.

## Architecture

HolyRail is split into small packages under `src/holyrail`:

- `analysis`: image metrics and sequence models.
- `curves`: correction curve generation.
- `rendering`: preview and high-quality frame rendering.
- `export`: video assembly and external export integrations.
- `models`: shared Pydantic data models.
- `project`: JSON project persistence.
- `metadata`: image and camera metadata extraction.
- `plugins`: plugin contracts and registry.
- `pipeline`: orchestration for analyze, preview, and render workflows.
- `ui`: future PySide6 desktop UI.
- `cli`: command-line entry points.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run black --check .
```

Planning lives in [BACKLOG.md](BACKLOG.md) and [SPRINTS.md](SPRINTS.md).
Contributor guidance lives in [CONTRIBUTING.md](CONTRIBUTING.md), and the
architecture overview lives in [docs/architecture.md](docs/architecture.md).

HolyRail is early-stage software. The public architecture is intentionally modular so image-processing algorithms can evolve without rewriting project storage, plugins, or UI layers.
