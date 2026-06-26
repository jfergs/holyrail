from __future__ import annotations

from pathlib import Path

from holyrail.analysis import analyze_sequence
from holyrail.config import HolyRailConfig
from holyrail.curves import build_sequence_metrics
from holyrail.export import assemble_video
from holyrail.metadata import discover_frames
from holyrail.models import ProjectDocument
from holyrail.project import load_project, save_project
from holyrail.rendering import render_frames, render_previews


def analyze(source: Path, project_path: Path, config: HolyRailConfig) -> ProjectDocument:
    frames = discover_frames(source)
    frame_metrics = analyze_sequence(frames, config.analysis)
    project = ProjectDocument(
        source_root=str(source),
        frames=frames,
        metrics=build_sequence_metrics(frame_metrics),
    )
    save_project(project, project_path)
    return project


def preview(project_path: Path, output_dir: Path, config: HolyRailConfig) -> list[Path]:
    project = load_project(project_path)
    return render_previews(project, output_dir, config)


def render(
    project_path: Path,
    output_dir: Path,
    config: HolyRailConfig,
    *,
    video_path: Path | None = None,
    fps: int = 24,
) -> list[Path]:
    project = load_project(project_path)
    frames = render_frames(project, output_dir, config)
    if video_path is not None:
        assemble_video(output_dir, video_path, fps=fps)
    return frames
