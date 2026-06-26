# HolyRail Backlog

Project-local backlog for HolyRail, an open source computational photography
platform focused first on professional RAW timelapse workflows.

## Current State

- Local repository scaffolded at `/Users/fergs/dev/holyrail`.
- Python package, `uv` project, CLI, JSON project model, metrics analysis,
  preview/render pipeline, plugin registry stub, and docs skeleton exist.
- No GitHub remote exists yet.
- Sprint plan exists in `SPRINTS.md`.
- Initial validation passes: `pytest`, `ruff`, and `black --check`.

## Card Convention

HolyRail cards use `HR-XXX`.

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

- `HR-004` Build a real sequence analysis report.
  - Persist summary statistics for luminance, color, frame intervals, and
    detected discontinuities.
  - Flag exposure jumps, auto white-balance jumps, and likely aperture flicker.
  - Keep long-term scene evolution separate from short-term camera variation.

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
