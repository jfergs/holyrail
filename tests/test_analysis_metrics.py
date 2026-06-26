from pathlib import Path

import cv2
import numpy as np

from holyrail.analysis import analyze_frame
from holyrail.config import AnalysisConfig
from holyrail.models import ImageFrame


def test_analyze_frame_extracts_luminance_and_white_balance(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.jpg"
    rgb = np.zeros((16, 16, 3), dtype=np.uint8)
    rgb[..., 0] = 128
    rgb[..., 1] = 64
    rgb[..., 2] = 32
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    assert cv2.imwrite(str(image_path), bgr)

    metrics = analyze_frame(
        ImageFrame(index=0, path=str(image_path), filename=image_path.name, file_size=1),
        AnalysisConfig(histogram_bins=16),
    )

    assert metrics.index == 0
    assert 0 < metrics.mean_luminance < 1
    assert len(metrics.histogram) == 16
    assert metrics.white_balance_r_over_g > 1
    assert metrics.white_balance_b_over_g < 1
