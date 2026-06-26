from __future__ import annotations

from pathlib import Path

from holyrail.config import HolyRailConfig
from holyrail.models import ProjectDocument
from holyrail.rendering.render import render_frames


def render_previews(
    project: ProjectDocument, output_dir: Path, config: HolyRailConfig
) -> list[Path]:
    return render_frames(project, output_dir, config, preview=True)
