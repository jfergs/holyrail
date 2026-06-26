import json
from pathlib import Path

from PIL import ExifTags, Image

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


def test_discover_frames_extracts_bitmap_metadata_and_hash(tmp_path: Path) -> None:
    frame_path = tmp_path / "frame.jpg"
    image = Image.new("RGB", (8, 6), color=(10, 20, 30))
    exif = Image.Exif()
    tags = {value: key for key, value in ExifTags.TAGS.items()}
    exif[tags["DateTimeOriginal"]] = "2026:06:26 12:34:56"
    exif[tags["Make"]] = "Holy"
    exif[tags["Model"]] = "Rail"
    exif[tags["FNumber"]] = 4.0
    exif[tags["ExposureTime"]] = 0.5
    exif[tags["ISOSpeedRatings"]] = 800
    exif[tags["FocalLength"]] = 24.0
    image.save(frame_path, exif=exif)

    [frame] = discover_frames(tmp_path, hash_files=True)

    assert frame.width == 8
    assert frame.height == 6
    assert frame.camera_make == "Holy"
    assert frame.camera_model == "Rail"
    assert frame.iso == 800
    assert frame.aperture == 4.0
    assert frame.shutter_seconds == 0.5
    assert frame.focal_length == 24.0
    assert frame.capture_time is not None
    assert frame.content_hash is not None


def test_discover_frames_orders_by_capture_time_when_available(tmp_path: Path) -> None:
    tags = {value: key for key, value in ExifTags.TAGS.items()}
    for filename, capture_time in [
        ("b.jpg", "2026:06:26 12:00:02"),
        ("a.jpg", "2026:06:26 12:00:01"),
    ]:
        image = Image.new("RGB", (4, 4), color=(1, 2, 3))
        exif = Image.Exif()
        exif[tags["DateTimeOriginal"]] = capture_time
        image.save(tmp_path / filename, exif=exif)

    frames = discover_frames(tmp_path)

    assert [frame.filename for frame in frames] == ["a.jpg", "b.jpg"]
    assert [frame.index for frame in frames] == [0, 1]


def test_project_diagnostics_reports_missing_frames(tmp_path: Path) -> None:
    project = ProjectDocument(
        source_root=str(tmp_path),
        frames=[ImageFrame(index=0, path="missing.jpg", filename="missing.jpg", file_size=1)],
    )

    diagnostics = inspect_project(project)

    assert not diagnostics.ok
    assert diagnostics.missing_frames == ["missing.jpg"]
