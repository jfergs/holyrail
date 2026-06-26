# RAW Metadata Validation

HolyRail can discover RAW files and uses `rawpy` when the optional RAW extra is
installed:

```bash
uv sync --extra dev --extra raw
uv run holyrail analyze /path/to/raw-sequence --project raw-project.json
uv run holyrail inspect --project raw-project.json
```

## What To Check

`holyrail inspect` should report the expected frame count. The project JSON
should include any metadata LibRaw exposes through `rawpy`, currently:

- frame dimensions
- camera make
- camera model
- white-balance source marker
- file size
- modified time
- relative frame path

Capture time, lens, ISO, aperture, shutter, focal length, orientation, and color
profile support vary by RAW format and need camera-specific fixtures before they
can be treated as complete.

## Fixture Policy

Do not commit large RAW files to the repository. Use small public sample files
or locally stored validation sequences, then document camera model, RAW format,
and observed metadata behavior in issue reports or release notes.

## Manual Validation Template

```text
Camera:
RAW format:
Frame count:
Command:
Fields populated:
Fields missing:
Notes:
```
