from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

from holyrail.models import ImageFrame

RAW_EXTENSIONS = {
    ".3fr",
    ".arw",
    ".cr2",
    ".cr3",
    ".dng",
    ".erf",
    ".fff",
    ".iiq",
    ".kdc",
    ".mef",
    ".mos",
    ".mrw",
    ".nef",
    ".orf",
    ".pef",
    ".raf",
    ".raw",
    ".rw2",
    ".sr2",
    ".srf",
    ".x3f",
}
BITMAP_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
SUPPORTED_EXTENSIONS = RAW_EXTENSIONS | BITMAP_EXTENSIONS
EXIF_TAGS = {value: key for key, value in ExifTags.TAGS.items()}


def supported_image_path(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def discover_frames(source_root: Path, *, hash_files: bool = False) -> list[ImageFrame]:
    if not source_root.exists():
        raise FileNotFoundError(f"Image source does not exist: {source_root}")

    source_root = source_root.resolve()
    paths = [path for path in source_root.rglob("*") if supported_image_path(path)]
    frame_data = [_build_frame(path, source_root, hash_files=hash_files) for path in paths]
    frame_data.sort(key=_sequence_sort_key)

    frames: list[ImageFrame] = []
    for index, frame in enumerate(frame_data):
        frames.append(frame.model_copy(update={"index": index}))
    return frames


def _build_frame(path: Path, source_root: Path, *, hash_files: bool) -> ImageFrame:
    stat = path.stat()
    relative_path = path.resolve().relative_to(source_root)
    metadata = _extract_bitmap_metadata(path)

    return ImageFrame(
        index=0,
        path=relative_path.as_posix(),
        filename=path.name,
        file_size=stat.st_size,
        modified_time=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
        content_hash=_sha256(path) if hash_files else None,
        **metadata,
    )


def _sequence_sort_key(frame: ImageFrame) -> tuple[int, datetime | str, str]:
    if frame.capture_time is not None:
        return (0, frame.capture_time, frame.filename)
    return (1, frame.filename, frame.path)


def _extract_bitmap_metadata(path: Path) -> dict[str, Any]:
    if path.suffix.lower() not in BITMAP_EXTENSIONS:
        return {}

    try:
        with Image.open(path) as image:
            exif = image.getexif()
            metadata: dict[str, Any] = {
                "width": image.width,
                "height": image.height,
                "color_profile": _color_profile_name(image),
            }
            if exif:
                metadata.update(_extract_exif_fields(exif))
            return metadata
    except OSError:
        return {}


def _extract_exif_fields(exif: Image.Exif) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    fields["capture_time"] = _parse_capture_time(
        _exif_value(exif, "DateTimeOriginal")
        or _exif_value(exif, "DateTimeDigitized")
        or _exif_value(exif, "DateTime")
    )
    fields["camera_make"] = _clean_string(_exif_value(exif, "Make"))
    fields["camera_model"] = _clean_string(_exif_value(exif, "Model"))
    fields["lens_model"] = _clean_string(_exif_value(exif, "LensModel"))
    fields["iso"] = _optional_int(
        _exif_value(exif, "ISOSpeedRatings") or _exif_value(exif, "PhotographicSensitivity")
    )
    fields["aperture"] = _optional_float(_exif_value(exif, "FNumber"))
    fields["shutter_seconds"] = _optional_float(_exif_value(exif, "ExposureTime"))
    fields["focal_length"] = _optional_float(_exif_value(exif, "FocalLength"))
    fields["orientation"] = _optional_int(_exif_value(exif, "Orientation"))
    fields["white_balance"] = _white_balance_name(_exif_value(exif, "WhiteBalance"))
    return {key: value for key, value in fields.items() if value is not None}


def _exif_value(exif: Image.Exif, tag_name: str) -> Any:
    tag_id = EXIF_TAGS.get(tag_name)
    if tag_id is None:
        return None
    return exif.get(tag_id)


def _parse_capture_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Fraction):
        return float(value)
    if isinstance(value, tuple) and len(value) == 2:
        numerator, denominator = value
        return float(numerator) / float(denominator)
    try:
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, tuple):
        value = value[0] if value else None
    converted = _optional_float(value)
    return int(converted) if converted is not None else None


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _white_balance_name(value: Any) -> str | None:
    if value is None:
        return None
    names = {0: "auto", 1: "manual"}
    return names.get(_optional_int(value), str(value))


def _color_profile_name(image: Image.Image) -> str | None:
    if image.info.get("icc_profile"):
        return "embedded-icc"
    return image.mode


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
