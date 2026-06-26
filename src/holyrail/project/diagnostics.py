from __future__ import annotations

from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field

from holyrail.models import ProjectDocument


class ProjectDiagnostics(BaseModel):
    project_path: str | None = None
    schema_version: int
    source_root: str
    frame_count: int
    metrics_frame_count: int
    correction_count: int
    frames_with_capture_time: int
    frames_with_content_hash: int
    missing_frames: list[str] = Field(default_factory=list)
    duplicate_paths: list[str] = Field(default_factory=list)

    @property
    def missing_count(self) -> int:
        return len(self.missing_frames)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicate_paths)

    @property
    def ok(self) -> bool:
        return self.missing_count == 0 and self.duplicate_count == 0


def inspect_project(
    project: ProjectDocument, project_path: Path | None = None
) -> ProjectDiagnostics:
    resolved_paths = [project.resolve_frame_path(frame) for frame in project.frames]
    missing_frames = [
        frame.path
        for frame, resolved_path in zip(project.frames, resolved_paths, strict=True)
        if not resolved_path.exists()
    ]
    duplicate_paths = sorted(
        path for path, count in Counter(str(path) for path in resolved_paths).items() if count > 1
    )

    return ProjectDiagnostics(
        project_path=str(project_path) if project_path is not None else None,
        schema_version=project.schema_version,
        source_root=project.source_root,
        frame_count=len(project.frames),
        metrics_frame_count=len(project.metrics.frames),
        correction_count=len(project.metrics.corrections),
        frames_with_capture_time=sum(1 for frame in project.frames if frame.capture_time),
        frames_with_content_hash=sum(1 for frame in project.frames if frame.content_hash),
        missing_frames=missing_frames,
        duplicate_paths=duplicate_paths,
    )
