from __future__ import annotations

import json
from pathlib import Path

from holyrail.models import ProjectDocument
from holyrail.models.project import CURRENT_APP_VERSION, CURRENT_SCHEMA_VERSION
from holyrail.project.migrations import migrate_project_data


def load_project(path: Path) -> ProjectDocument:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProjectDocument.model_validate(migrate_project_data(data))


def save_project(project: ProjectDocument, path: Path) -> None:
    project.schema_version = CURRENT_SCHEMA_VERSION
    project.last_saved_with_app_version = CURRENT_APP_VERSION
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(project.model_dump_json(indent=2), encoding="utf-8")
