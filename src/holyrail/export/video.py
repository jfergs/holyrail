from __future__ import annotations

import subprocess
from pathlib import Path


def assemble_video(frames_dir: Path, output_path: Path, fps: int = 24) -> None:
    pattern = str(frames_dir / "*.jpg")
    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-pattern_type",
        "glob",
        "-i",
        pattern,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(command, check=True)
