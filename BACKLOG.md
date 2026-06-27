# HolyRail Backlog

Project-local backlog for HolyRail, an open source computational photography
platform focused first on professional RAW timelapse workflows.

## Current State

- Local repository scaffolded at `/Users/fergs/dev/holyrail`.
- Python package, `uv` project, CLI, JSON project model, metrics analysis,
  preview/render pipeline, plugin registry stub, and docs skeleton exist.
- GitHub remote exists at `https://github.com/jfergs/holyrail`.
- Sprint plan exists in `SPRINTS.md`.
- Current validation passes: `pytest`, `ruff`, and `black --check`.

## Card Convention

HolyRail cards use `HR-XXX`.

## In Progress

- `HR-011` Implement color and white-balance correction curves:
  - Added schema v5 generated color model.
  - Stored red/green and blue/green shift samples, anchors, algorithm metadata,
    strength, and smoothing window separately from corrections.
  - Kept legacy `color_curve` sample pairs for compatibility.
  - Added color curve config: strength, max shift, and optional smoothing
    window.
  - Added `holyrail curves color` JSON export.
  - Added tests proving gradual golden-hour trends are preserved and abrupt
    AWB jumps receive tint correction.

## P0 - Foundation

- `HR-001` Publish initial repository.
  - Create `jfergs/holyrail` on GitHub.
  - Commit the scaffold.
  - Push `main`.
  - Confirm README install and CLI commands from a fresh checkout.

- `HR-002` Harden project file schema.
  - Add explicit project schema migration hooks.
  - Add relative-path handling for portable project files.
  - Add source-root validation and missing-frame diagnostics.

- `HR-003` Improve RAW metadata extraction.
  - Extract capture time, camera make/model, lens, ISO, aperture, shutter,
    focal length, white balance, and orientation.
  - Prefer LibRaw/rawpy metadata where available.
  - Add fallback EXIF extraction for bitmap development inputs.

- `HR-005` Add correction model tests with synthetic sequences.
  - Cover sunset, sunrise, holy grail transitions, flicker, AWB jumps, and
    multi-day discontinuities.
  - Verify long-term trends are preserved.
  - Verify short-term oscillations are reduced.

## P1 - Phase-One Workflow

- `HR-010` Implement non-destructive exposure correction curves.
  - Generate editable keyframe-style exposure curves.
  - Store curve controls separately from per-frame generated corrections.
  - Support recomputation without touching source files.

- `HR-011` Implement color and white-balance correction curves.
  - Model smooth temperature/tint changes.
  - Detect and correct abrupt AWB jumps.
  - Avoid neutralizing intentional golden-hour or blue-hour shifts.

- `HR-012` Add aperture flicker detection and correction.
  - Compare local luminance variation against global trend.
  - Build per-frame deflicker strengths.
  - Add regression tests for noisy image sequences.

- `HR-013` Add preview contact sheets and graph export.
  - Export exposure and color graphs as images or JSON.
  - Generate before/after preview frames.
  - Add a sequence overview suitable for UI integration.

- `HR-014` Improve render quality controls.
  - Support TIFF/PNG output.
  - Add bit-depth controls.
  - Preserve orientation and basic color metadata.
  - Add deterministic output naming.

- `HR-015` Make FFmpeg export robust.
  - Avoid glob ordering ambiguity.
  - Support frame-rate, codec, CRF, resolution, and color-space options.
  - Surface FFmpeg errors cleanly through the CLI.

## P2 - Platform Expansion

- `HR-020` Define plugin API versioning.
  - Add plugin metadata model.
  - Add discovery/loading strategy.
  - Add extension points for analysis, curves, rendering, export, and UI.

- `HR-021` Build PySide6 desktop UI prototype.
  - Project open/save.
  - Sequence analysis view.
  - Graph preview.
  - Render/export panel.

- `HR-022` Add GPU acceleration research spike.
  - Evaluate OpenCL, CUDA, Metal, ONNX Runtime, and PyTorch paths.
  - Identify which operations benefit most from GPU acceleration.
  - Keep CPU implementation authoritative.

- `HR-023` Add documentation for contributors.
  - Architecture guide.
  - Development setup.
  - Plugin authoring guide.
  - Computational photography terminology.

- `HR-024` Add sample data strategy.
  - Create tiny synthetic test sequences.
  - Document how larger RAW fixtures should be stored outside Git.
  - Add fixture generation scripts.

## Completed

- `HR-010` Implement non-destructive exposure correction curves:
  - Added schema v4 generated exposure model.
  - Stored exposure curve algorithm metadata, strength, smoothing window,
    anchors, and samples separately from per-frame corrections.
  - Kept legacy `exposure_curve` samples for compatibility.
  - Added `holyrail curves exposure` JSON export.
  - Added `holyrail recompute-curves` to regenerate curves from stored metrics.
  - Added exposure strength, smoothing-window, and max-correction settings.
  - Added segment-aware smoothing so exposure/discontinuity jumps do not get
    normalized away.
  - Tightened aperture-flicker detection to distinguish single-frame flicker
    from ramp-adjacent exposure changes.
  - Added tests for gradual trend preservation, holy-grail step preservation,
    flicker correction, strength scaling, and correction clamping.

- `HR-004` Build a real sequence analysis report:
  - Added schema v3 analysis report model.
  - Added sequence summary statistics for luminance, white-balance ratios, and
    capture intervals.
  - Added exposure jump, white-balance jump, aperture-flicker candidate, and
    capture-discontinuity detection.
  - Added per-frame analysis flags.
  - Added `holyrail report` JSON export.
  - Added synthetic fixtures/tests for sunset, sunrise, holy-grail exposure
    steps, aperture flicker, AWB jumps, and multi-day gaps.

- `HR-003` Improve RAW metadata extraction:
  - Bitmap metadata extraction is implemented for development/test inputs.
  - Frame dimensions, modified time, EXIF capture time, camera make/model,
    ISO, aperture, shutter, focal length, orientation, white balance, color
    profile marker, and optional SHA-256 content hash are supported.
  - Deterministic capture-time ordering is implemented.
  - Optional `rawpy` RAW metadata path extracts frame dimensions, camera
    make/model, and white-balance source marker where LibRaw exposes them.
  - RAW fixture validation workflow is documented in `docs/raw-validation.md`.

- `HR-002` Harden project file schema:
  - Added schema v2 with created/saved app-version fields.
  - Added v1 project migration.
  - Stored discovered frame paths relative to `source_root`.
  - Added source-root-aware frame path resolution.
  - Added read-only project diagnostics and `holyrail inspect`.
  - Added missing-frame and migration tests.

- `HR-001` Publish initial repository:
  - Created public GitHub repository.
  - Pushed `main`.
  - Added repository metadata and topics.
  - Confirmed fresh clone install and validation.

- Initial local scaffold:
  - Build system and dependencies.
  - CLI entry points: `analyze`, `preview`, `render`.
  - Configuration model and example TOML.
  - Project JSON model.
  - Image discovery and bitmap/RAW loader path.
  - Luminance, histogram, RGB, and white-balance metrics.
  - Sequence smoothing and generated correction frames.
  - Preview/render output.
  - FFmpeg export hook.
  - Tests and docs skeleton.
