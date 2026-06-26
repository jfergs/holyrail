from __future__ import annotations

from pathlib import Path

import numpy as np

from holyrail.analysis.loader import load_rgb_image, resize_for_analysis
from holyrail.config import AnalysisConfig
from holyrail.models import FrameMetrics, ImageFrame


def _to_float01(image: np.ndarray) -> np.ndarray:
    if np.issubdtype(image.dtype, np.integer):
        max_value = np.iinfo(image.dtype).max
        return image.astype(np.float32) / float(max_value)
    return np.clip(image.astype(np.float32), 0.0, 1.0)


def _resolve_frame_path(frame: ImageFrame, source_root: Path | None) -> Path:
    path = Path(frame.path)
    if path.is_absolute() or source_root is None:
        return path
    return source_root / path


def analyze_frame(
    frame: ImageFrame, config: AnalysisConfig, source_root: Path | None = None
) -> FrameMetrics:
    image = load_rgb_image(_resolve_frame_path(frame, source_root))
    image = resize_for_analysis(image, config.downsample_width)
    rgb = _to_float01(image)
    luminance = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    histogram, _ = np.histogram(luminance, bins=config.histogram_bins, range=(0.0, 1.0))
    channel_means = rgb.reshape(-1, 3).mean(axis=0)
    green = max(float(channel_means[1]), 1e-6)

    return FrameMetrics(
        index=frame.index,
        mean_luminance=float(np.mean(luminance)),
        median_luminance=float(np.median(luminance)),
        shadow_luminance=float(np.percentile(luminance, config.shadow_percentile)),
        highlight_luminance=float(np.percentile(luminance, config.highlight_percentile)),
        histogram=histogram.astype(int).tolist(),
        red_mean=float(channel_means[0]),
        green_mean=float(channel_means[1]),
        blue_mean=float(channel_means[2]),
        white_balance_r_over_g=float(channel_means[0] / green),
        white_balance_b_over_g=float(channel_means[2] / green),
    )


def analyze_sequence(
    frames: list[ImageFrame], config: AnalysisConfig, source_root: Path | None = None
) -> list[FrameMetrics]:
    return [analyze_frame(frame, config, source_root) for frame in frames]
