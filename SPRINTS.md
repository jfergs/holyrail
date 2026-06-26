# HolyRail Sprint Plan

Sprints are nominally two weeks. The sequence is ordered to get HolyRail from
the current local scaffold to a credible open-source phase-one RAW timelapse
platform, then to a broader computational photography platform. Backlog card
IDs map to `BACKLOG.md`.

Dependency order matters:

- Repository publication gates external contribution.
- Project schema and metadata extraction gate reliable analysis.
- Synthetic sequence fixtures gate correction-model confidence.
- Analysis reports gate exposure, color, white-balance, and flicker models.
- Rendering/export hardening gates real user output.
- Plugin API and UI work should wait until the core workflow is stable.

---

## Sprint 0 - Initial Scaffold COMPLETE

**Goal:** Create the local project skeleton and prove the first CLI loop works.

**Completed:**

- Created `uv` Python package with `src/holyrail` layout.
- Added CLI entry points: `holyrail analyze`, `holyrail preview`, `holyrail render`.
- Added config model, example TOML, JSON project model, and project IO.
- Added image discovery, bitmap loading, optional RAW loading path, analysis
  metrics, sequence smoothing, preview/render pipeline, FFmpeg hook, plugin
  registry stub, tests, and docs skeleton.
- Added project backlog and workspace-tracker entries.

**Validation:**

- `pytest` passes.
- `ruff check .` passes.
- `black --check .` passes.

---

## Sprint 1 - Publish And Project Hygiene COMPLETE

**Backlog:** `HR-001`, `HR-023`

**Goal:** Make HolyRail a real repository with clean contributor entry points.

### Repository Publication

- Create `jfergs/holyrail` on GitHub.
- Commit the current scaffold.
- Push `main`.
- Add repository metadata: description, topics, license, default branch.
- Confirm `uv sync --extra dev` and CLI commands from a fresh checkout.

### Contribution Hygiene

- Add `CONTRIBUTING.md`.
- Add `CODE_OF_CONDUCT.md`.
- Add issue templates for bugs, feature requests, RAW support reports, and
  algorithm-quality reports.
- Add pull request template with test and sample-data notes.
- Add architecture overview in docs.

### CI

- Add GitHub Actions for `ruff`, `black --check`, and `pytest`.
- Cache `uv` dependencies.
- Run CI on pull requests and `main`.

**Acceptance Criteria:**

- Fresh clone can run `uv sync --extra dev` and `uv run pytest`.
- GitHub Actions pass on `main`.
- README points users to backlog, sprint plan, and docs.

**Completed:**

- Created public repository: `https://github.com/jfergs/holyrail`.
- Pushed initial `main` branch.
- Added repository topics for computational photography, RAW processing,
  timelapse, Python, OpenCV, and FFmpeg.
- Added contribution guide, code of conduct, issue templates, PR template, CI,
  and architecture docs.
- Validated a fresh clone in `/private/tmp/holyrail-fresh-check`.

**Validation:**

- `uv sync --extra dev` from fresh clone completed.
- `uv run pytest` passed from fresh clone.
- `uv run ruff check .` passed from fresh clone.
- `uv run black --check .` passed from fresh clone.

---

## Sprint 2 - Project Schema And Portable State COMPLETE

**Backlog:** `HR-002`

**Goal:** Make project files durable, portable, and safe to evolve.

### Schema Versioning

- Add explicit schema migration framework.
- Add tests for loading current schema and at least one legacy fixture.
- Record creation app version and last-write app version separately.
- Add validation error messages that identify the broken field and project path.

### Portable Paths

- Store frame paths relative to `source_root` when possible.
- Support absolute path fallback for external media.
- Add source-root relocation command or project repair helper.
- Detect missing, moved, renamed, and duplicate frames.

### Project Diagnostics

- Add `holyrail inspect --project ...`.
- Report frame count, source root, missing files, schema version, metrics state,
  render state, and analysis summary availability.
- Keep inspect read-only.

**Acceptance Criteria:**

- Project files can move with their source directory and still load.
- Missing frames produce actionable diagnostics, not tracebacks.
- `holyrail inspect` works against valid and intentionally damaged projects.

**Completed:**

- Added schema v2 and explicit v1-to-v2 migration.
- Split created-with and last-saved app version metadata.
- Stored discovered frame paths relative to `source_root`.
- Added shared frame path resolution for analysis, preview, and render.
- Added read-only `holyrail inspect`.
- Added project diagnostics for missing frames and duplicate resolved paths.

**Validation:**

- `uv run pytest` passed with 7 tests.
- `uv run ruff check .` passed.
- `uv run black --check .` passed.

---

## Sprint 3 - Metadata Extraction And Frame Identity COMPLETE

**Backlog:** `HR-003`, `HR-024`

**Goal:** Build reliable frame identity and capture metadata for RAW and bitmap
development inputs.

### Metadata Extraction

- Extract capture time, camera make/model, lens model, ISO, aperture, shutter
  speed, focal length, white balance, orientation, dimensions, and color profile
  where available.
- Prefer LibRaw/rawpy metadata for RAW files.
- Add EXIF fallback for JPEG/TIFF/PNG development inputs.
- Normalize shutter speed to seconds and aperture to f-number.

### Frame Identity

- Add content hash option for project repair and duplicate detection.
- Add fast identity mode using path, file size, modified time, and frame index.
- Preserve stable sequence ordering by capture time when available, filename
  otherwise.

### Sample Data

- Add synthetic fixture generation scripts.
- Create tiny generated fixtures for tests.
- Document how larger RAW sequences should be stored outside Git.

**Acceptance Criteria:**

- Metadata fields populate for generated EXIF bitmap fixtures.
- RAW metadata path is covered by optional-dependency tests or documented
  manual validation.
- Sequence ordering is deterministic and covered by tests.

**Completed:**

- Added explicit Pillow dependency for bitmap metadata extraction.
- Added frame identity fields: modified time and optional SHA-256 content hash.
- Added image metadata fields: width, height, focal length, orientation, white
  balance, and color profile marker.
- Extracted EXIF capture time, camera make/model, ISO, aperture, shutter, and
  focal length for bitmap inputs.
- Added capture-time ordering when EXIF timestamps are available.
- Added tests for EXIF extraction, hashing, and deterministic ordering.
- Added optional `rawpy` RAW metadata path for dimensions, camera make/model,
  and white-balance source marker.
- Documented RAW fixture validation workflow in `docs/raw-validation.md`.
- Added `holyrail inspect` counts for capture timestamps and content hashes.

**Validation:**

- `uv run pytest` passed with 12 tests.
- `uv run ruff check .` passed.
- `uv run black --check .` passed.

---

## Sprint 4 - Sequence Analysis Report COMPLETE

**Backlog:** `HR-004`, `HR-005`

**Goal:** Produce a trustworthy analysis report that distinguishes natural scene
evolution from camera-induced variation.

### Analysis Report Model

- Add sequence-level summary statistics for luminance, color, white balance,
  frame intervals, exposure settings, and capture gaps.
- Add per-frame analysis flags.
- Persist report in the project JSON.
- Export report as JSON for external tools.

### Event Detection

- Detect exposure jumps from metadata and luminance.
- Detect AWB jumps from channel ratios.
- Detect likely aperture flicker from high-frequency luminance variation.
- Detect discontinuities from capture-time gaps and abrupt histogram changes.

### Synthetic Regression Sequences

- Generate sunset, sunrise, holy grail, astro, AWB jump, flicker, and multi-day
  test sequences.
- Assert trend preservation and jump detection behavior.

**Acceptance Criteria:**

- Analysis report explains what HolyRail thinks is natural trend vs camera
  variation.
- Synthetic sequences prove long-term trends are preserved.
- Tests cover the main phase-one sequence types.

**Completed:**

- Added schema v3 with a persisted analysis report.
- Added summary statistics for luminance, white-balance ratios, and capture
  intervals.
- Added exposure jump, white-balance jump, aperture-flicker candidate, and
  capture-discontinuity detection.
- Added per-frame analysis flags.
- Added `holyrail report` JSON export.
- Added synthetic tests for exposure/WB jumps and capture discontinuities.
- Added reusable synthetic sequence fixtures.
- Added regression tests proving gradual sunset/sunrise trends are not flagged
  as exposure jumps.
- Added regression tests for holy-grail exposure steps, aperture flicker, AWB
  jumps, and multi-day gaps.

**Validation:**

- `uv run pytest` passed with 20 tests.
- `uv run ruff check .` passed.
- `uv run black --check .` passed.

---

## Sprint 5 - Exposure Curve Model

**Backlog:** `HR-010`, `HR-005`

**Goal:** Replace the initial smoothing placeholder with a non-destructive,
editable exposure correction model.

### Curve Representation

- Add curve data model: anchors, generated samples, algorithm metadata, and
  user override state.
- Store generated curves separately from rendered per-frame corrections.
- Support recomputing corrections after parameter changes.

### Exposure Modeling

- Build robust trend estimator for luminance/exposure.
- Preserve intentional sunset/sunrise/holy-grail changes.
- Correct auto-exposure jumps and short-period flicker without flattening the
  scene.
- Add tunable strength and smoothing window settings.

### CLI

- Add `holyrail curves exposure --project ...`.
- Add `holyrail analyze --recompute-curves`.
- Add curve export for graphing/UI work.

**Acceptance Criteria:**

- Exposure correction lowers short-term luminance variance on flicker fixtures.
- Exposure correction does not flatten sunset/sunrise fixtures.
- User-facing project data can explain the generated exposure curve.

---

## Sprint 6 - Color And White-Balance Curves

**Backlog:** `HR-011`, `HR-005`

**Goal:** Model color evolution without neutralizing intentional golden-hour,
blue-hour, or astro color shifts.

### Color Metrics

- Add chromaticity metrics beyond channel means.
- Track neutral candidates where possible.
- Add robust outlier rejection for saturated regions and night-sky frames.

### White-Balance Modeling

- Detect abrupt AWB jumps.
- Generate temperature/tint-style correction curves.
- Preserve long-term color mood changes.
- Add strength controls and per-segment behavior.

### Validation

- Add synthetic golden-hour, blue-hour, AWB jump, and mixed-light fixtures.
- Add before/after metric reports.

**Acceptance Criteria:**

- AWB jump fixture is smoothed without removing gradual color trend.
- Strongly colored intentional scenes are not forced neutral.
- Corrections are stored non-destructively and can be recomputed.

---

## Sprint 7 - Aperture Flicker And Sensor Noise

**Backlog:** `HR-012`

**Goal:** Add dedicated correction for subtle frame-to-frame brightness changes
that exposure curves alone should not handle.

### Flicker Detection

- Detect local high-frequency luminance changes after trend removal.
- Compare global luminance, local regions, and histogram shifts.
- Separate aperture flicker from real scene motion where possible.

### Flicker Correction

- Add per-frame deflicker strength.
- Support median-window and robust-statistics correction modes.
- Keep correction bounded to avoid visible pumping.

### Sensor Fluctuation Handling

- Track black-level or shadow instability where metadata allows.
- Add noise-aware behavior for high-ISO astro sequences.

**Acceptance Criteria:**

- Synthetic aperture flicker fixture improves measurably.
- Sunset/sunrise fixtures do not acquire artificial brightness plateaus.
- Correction limits prevent extreme single-frame overcorrection.

---

## Sprint 8 - Preview, Graphs, And Review Artifacts

**Backlog:** `HR-013`

**Goal:** Give users enough visual feedback to trust corrections before a full
render.

### Preview Outputs

- Generate before/after preview frames.
- Generate contact sheets for selected frames.
- Add representative-frame selection from start, end, key transitions, detected
  jumps, and flagged discontinuities.

### Graph Export

- Export exposure, luminance, color, white-balance, and flicker graphs.
- Support JSON graph data and PNG/SVG graph images.
- Add analysis report HTML or markdown summary.

### CLI

- Add preview options for count, width, before/after, contact sheet, and graph
  export.

**Acceptance Criteria:**

- A single command produces previews, contact sheet, and graphs.
- Report artifacts are deterministic and testable.
- Users can identify detected jumps from graph/report output.

---

## Sprint 9 - Render Quality And Export

**Backlog:** `HR-014`, `HR-015`

**Goal:** Make rendered output suitable for real timelapse workflows.

### Render Controls

- Support JPEG, PNG, TIFF, and 16-bit TIFF where possible.
- Add bit-depth, compression, quality, resize, and colorspace options.
- Preserve orientation and basic color metadata.
- Add deterministic output naming and manifest export.

### Pipeline Reliability

- Add resumable rendering.
- Add overwrite policy: fail, overwrite, skip-existing.
- Add progress reporting.
- Add clear error handling for unreadable frames and output failures.

### FFmpeg Export

- Replace glob ambiguity with manifest/list-file input.
- Support fps, codec, CRF, preset, pixel format, resolution, and output profile.
- Surface FFmpeg command and stderr cleanly.

**Acceptance Criteria:**

- Render output order is deterministic.
- Failed renders can resume.
- FFmpeg export works from a generated manifest.

---

## Sprint 10 - Plugin API And Extension Boundaries

**Backlog:** `HR-020`, `HR-023`

**Goal:** Define the stable extension points before third-party contribution
patterns harden by accident.

### Plugin Metadata

- Add plugin manifest model.
- Add plugin API version checks.
- Add safe discovery from configured plugin directories.
- Add enable/disable controls in config.

### Extension Points

- Analysis plugin interface.
- Curve model plugin interface.
- Renderer plugin interface.
- Export plugin interface.
- UI contribution placeholder interface.

### Examples And Docs

- Add a minimal example analysis plugin.
- Add plugin authoring guide.
- Add tests for plugin loading and version mismatch handling.

**Acceptance Criteria:**

- Example plugin loads in tests.
- Unsupported plugin API versions fail with clear diagnostics.
- Core pipeline can run with plugins disabled.

---

## Sprint 11 - Desktop UI Prototype

**Backlog:** `HR-021`

**Goal:** Build a PySide6 desktop prototype around the proven CLI workflow,
without moving business logic into the UI.

### UI Foundation

- Project open/save.
- Sequence import.
- Analysis status and diagnostics view.
- Graph preview panel.
- Before/after preview panel.
- Render/export panel.

### Architecture

- Keep UI as a thin client over project/pipeline services.
- Add background worker pattern for long-running analysis/render jobs.
- Add cancellation and progress.

### Packaging Research

- Identify packaging path for macOS, Windows, and Linux.
- Document optional dependencies and FFmpeg discovery.

**Acceptance Criteria:**

- UI can open a project, run analysis, show graphs/previews, and start render.
- Long-running jobs do not block the UI thread.
- CLI remains fully functional and authoritative.

---

## Sprint 12 - GPU Acceleration Research And Compute Backend

**Backlog:** `HR-022`

**Goal:** Identify where GPU acceleration matters and add a backend abstraction
without prematurely making GPU mandatory.

### Research

- Benchmark CPU NumPy/OpenCV baseline.
- Evaluate OpenCL, CUDA, Metal, ONNX Runtime, and PyTorch for likely hot paths.
- Measure histogram, resize, demosaic-adjacent operations, color transforms,
  and batch render throughput.

### Backend Abstraction

- Add compute backend interface.
- Keep CPU backend default and authoritative.
- Add optional experimental backend behind config flag.

### Documentation

- Publish benchmark methodology.
- Document installation constraints per OS.
- Identify features that should stay CPU-only.

**Acceptance Criteria:**

- Benchmarks show which operations justify GPU work.
- Experimental backend can be disabled cleanly.
- No core workflow requires GPU dependencies.

---

## Sprint 13 - Phase-One Beta Hardening

**Backlog:** `HR-002` through `HR-015`, `HR-023`, `HR-024`

**Goal:** Turn the workflow into a beta-quality RAW timelapse processor.

### Real-World Validation

- Validate against sunset, sunrise, holy grail, astro, landscape, construction,
  and multi-day sequences.
- Record sequence characteristics and failure modes.
- Add manual validation checklist.

### Performance

- Profile analysis and render throughput.
- Add batch-size or worker-count controls.
- Improve memory behavior on large sequences.

### Documentation

- Write end-to-end tutorial.
- Write troubleshooting guide.
- Document limits and known failure cases honestly.

### Release Prep

- Tag `v0.1.0-beta.1`.
- Publish release notes.
- Add roadmap for beta feedback.

**Acceptance Criteria:**

- A new user can process a bitmap or RAW sequence from README instructions.
- Known limitations are documented.
- Release artifacts and docs match the actual CLI behavior.

---

## Sprint 14 - Computational Photography Platform Expansion

**Backlog:** future `HR-030+`

**Goal:** Start expanding beyond phase-one timelapse while keeping the platform
architecture coherent.

### New Workflow Candidates

- Focus stacking.
- Exposure bracketing and HDR merge.
- Panorama preprocessing.
- Star trail and astro stacking.
- Long-term change detection.

### Platform Work

- Generalize project model for multiple workflow types.
- Add workflow registry.
- Add reusable asset/cache model.
- Add research-notebook style experiment outputs.

**Acceptance Criteria:**

- At least one non-timelapse workflow spike runs through the plugin/workflow
  architecture.
- Timelapse workflow remains unaffected.
- Backlog gains concrete `HR-030+` cards based on findings.
