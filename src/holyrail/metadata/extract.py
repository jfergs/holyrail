from __future__ import annotations

from pathlib import Path

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


def supported_image_path(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def discover_frames(source_root: Path) -> list[ImageFrame]:
    if not source_root.exists():
        raise FileNotFoundError(f"Image source does not exist: {source_root}")

    paths = sorted(path for path in source_root.rglob("*") if supported_image_path(path))
    frames: list[ImageFrame] = []
    for index, path in enumerate(paths):
        stat = path.stat()
        frames.append(
            ImageFrame(
                index=index,
                path=str(path),
                filename=path.name,
                file_size=stat.st_size,
            )
        )
    return frames
