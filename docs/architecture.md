# Architecture

HolyRail is designed as a long-lived computational photography platform. The
phase-one product is RAW timelapse processing, but the architecture keeps
workflow orchestration, project storage, algorithms, rendering, export, plugins,
and UI boundaries separate.

## Core Rules

- Source images are immutable.
- Project files store references, metrics, generated models, and user choices.
- Rendering writes new frames to an output directory.
- CLI workflows remain authoritative even after UI work begins.
- Optional acceleration and RAW dependencies must not make the base development
  loop fragile.

## Packages

- `analysis`: image loading and per-frame metrics.
- `curves`: generated correction models and future editable curves.
- `rendering`: preview and final frame rendering.
- `export`: video assembly and external export targets.
- `models`: shared Pydantic models.
- `project`: project persistence and future migrations.
- `metadata`: frame discovery and capture metadata.
- `plugins`: plugin contracts, manifests, and registry.
- `pipeline`: analyze, preview, render, and future workflow orchestration.
- `ui`: future PySide6 desktop shell.
- `cli`: command-line interface.

## Data Flow

```mermaid
flowchart LR
  A[Source Images] --> B[Frame Discovery]
  B --> C[Metadata Extraction]
  C --> D[Frame Metrics]
  D --> E[Sequence Analysis]
  E --> F[Correction Models]
  F --> G[Preview Artifacts]
  F --> H[Rendered Frames]
  H --> I[Video Export]
```

## Non-Destructive Project State

HolyRail project JSON should be treated as an editable processing plan. It can
contain generated analysis and correction data, but it must not require source
images to move or change. Future schema changes should use explicit migrations.
Frame paths are stored relative to the source root when possible so a project
directory can move with its images.

## Algorithm Boundary

Analysis must distinguish between natural scene evolution and camera-induced
variation. Sunset, sunrise, holy-grail, astro, landscape, construction, and
multi-day sequences all contain legitimate long-term changes. Correction models
should reduce short-term artifacts while preserving those trends.

## Plugin Boundary

Plugins should extend specific surfaces:

- analysis metrics
- correction curves
- rendering operations
- export targets
- UI panels

Core workflows must still run with plugins disabled.

## Project Inspection

`holyrail inspect` is a read-only health check for project files. It reports the
schema version, source root, frame count, metric count, correction count, missing
frame paths, and duplicate resolved paths. Future UI diagnostics should reuse
the same project diagnostics layer.

## Frame Identity

Frame discovery records relative paths, file size, modified time, optional
content hash, image dimensions, and available EXIF capture metadata. When
capture timestamps exist, they drive sequence ordering; otherwise HolyRail falls
back to deterministic filename/path ordering.

RAW files use an optional `rawpy` metadata path. LibRaw availability varies by
camera and format, so RAW fixture findings should be recorded with camera model
and file format.
