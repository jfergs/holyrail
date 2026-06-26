from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_rgb_image(path: Path) -> np.ndarray:
    if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}:
        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Could not decode image: {path}")
        if image.ndim == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    try:
        import rawpy
    except ImportError as exc:
        raise RuntimeError(
            f"RAW input requires the optional rawpy dependency: {path}. "
            "Install with `uv sync --extra raw`."
        ) from exc

    with rawpy.imread(str(path)) as raw:
        return raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=True,
            output_bps=16,
            gamma=(1, 1),
        )


def resize_for_analysis(image: np.ndarray, width: int) -> np.ndarray:
    height, current_width = image.shape[:2]
    if current_width <= width:
        return image
    scale = width / current_width
    return cv2.resize(image, (width, int(height * scale)), interpolation=cv2.INTER_AREA)
