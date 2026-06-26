from pathlib import Path

import cv2
import numpy as np

from holyrail.cli.main import main


def _write_frame(path: Path, value: int) -> None:
    rgb = np.full((12, 12, 3), value, dtype=np.uint8)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    assert cv2.imwrite(str(path), bgr)


def test_cli_analyze_and_preview(tmp_path: Path) -> None:
    frames = tmp_path / "frames"
    frames.mkdir()
    _write_frame(frames / "0001.jpg", 48)
    _write_frame(frames / "0002.jpg", 64)
    project = tmp_path / "project.json"
    previews = tmp_path / "previews"

    assert main(["analyze", str(frames), "--project", str(project)]) == 0
    assert project.exists()
    assert main(["preview", "--project", str(project), "--output", str(previews)]) == 0

    assert len(list(previews.glob("*.jpg"))) == 2
