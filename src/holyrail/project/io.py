from __future__ import annotations

from pathlib import Path

from holyrail.models import ProjectDocument


def load_project(path: Path) -> ProjectDocument:
    return ProjectDocument.model_validate_json(path.read_text(encoding="utf-8"))


def save_project(project: ProjectDocument, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(project.model_dump_json(indent=2), encoding="utf-8")
