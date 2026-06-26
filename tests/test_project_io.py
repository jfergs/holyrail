from pathlib import Path

from holyrail.models import ProjectDocument
from holyrail.project import load_project, save_project


def test_project_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "project.json"
    project = ProjectDocument(source_root=str(tmp_path))

    save_project(project, path)
    loaded = load_project(path)

    assert loaded.source_root == str(tmp_path)
    assert loaded.schema_version == 1
