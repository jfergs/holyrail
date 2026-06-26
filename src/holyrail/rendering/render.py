from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from holyrail.analysis.loader import load_rgb_image, resize_for_analysis
from holyrail.config import HolyRailConfig
from holyrail.models import CorrectionFrame, ImageFrame, ProjectDocument


def _apply_exposure(rgb: np.ndarray, correction: CorrectionFrame | None) -> np.ndarray:
    if correction is None:
        return rgb
    multiplier = 2.0**correction.exposure_ev
    return np.clip(rgb.astype(np.float32) * multiplier, 0, np.iinfo(rgb.dtype).max).astype(
        rgb.dtype
    )


def _write_rgb(path: Path, rgb: np.ndarray, jpeg_quality: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    params = (
        [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        if path.suffix.lower() in {".jpg", ".jpeg"}
        else []
    )
    if not cv2.imwrite(str(path), bgr, params):
        raise ValueError(f"Could not write rendered frame: {path}")


def _output_name(frame: ImageFrame, extension: str) -> str:
    return f"{frame.index:06d}_{Path(frame.filename).stem}.{extension.lstrip('.')}"


def render_frames(
    project: ProjectDocument,
    output_dir: Path,
    config: HolyRailConfig,
    *,
    preview: bool = False,
) -> list[Path]:
    corrections = {correction.index: correction for correction in project.metrics.corrections}
    output_paths: list[Path] = []
    for frame in project.frames:
        rgb = load_rgb_image(project.resolve_frame_path(frame))
        if preview:
            rgb = resize_for_analysis(rgb, config.render.preview_width)
        rgb = _apply_exposure(rgb, corrections.get(frame.index))
        output_path = output_dir / _output_name(frame, config.render.output_extension)
        _write_rgb(output_path, rgb, config.render.jpeg_quality)
        output_paths.append(output_path)
    return output_paths
