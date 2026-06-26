import json
from pathlib import Path

from holyrail.metadata import discover_frames
from holyrail.models import ImageFrame, ProjectDocument
from holyrail.project import inspect_project, load_project, save_project


def test_project_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "project.json"
    project = ProjectDocument(source_root=str(tmp_path))

    save_project(project, path)
    loaded = load_project(path)

    assert loaded.source_root == str(tmp_path)
    assert loaded.schema_version == 2
    assert loaded.last_saved_with_app_version == "0.1.0"


def test_load_project_migrates_schema_v1(tmp_path: Path) -> None:
    path = tmp_path / "project.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "app_version": "0.0.9",
                "source_root": str(tmp_path),
                "frames": [],
                "metrics": {},
            }
        ),
        encoding="utf-8",
    )

    loaded = load_project(path)

    assert loaded.schema_version == 2
    assert loaded.created_with_app_version == "0.0.9"
    assert loaded.last_saved_with_app_version == "0.0.9"


def test_discover_frames_stores_relative_paths(tmp_path: Path) -> None:
    frame_path = tmp_path / "nested" / "frame.jpg"
    frame_path.parent.mkdir()
    frame_path.write_bytes(b"placeholder")

    [frame] = discover_frames(tmp_path)

    assert frame.path == "nested/frame.jpg"


def test_project_diagnostics_reports_missing_frames(tmp_path: Path) -> None:
    project = ProjectDocument(
        source_root=str(tmp_path),
        frames=[ImageFrame(index=0, path="missing.jpg", filename="missing.jpg", file_size=1)],
    )

    diagnostics = inspect_project(project)

    assert not diagnostics.ok
    assert diagnostics.missing_frames == ["missing.jpg"]
