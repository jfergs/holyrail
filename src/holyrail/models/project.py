from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

CURRENT_SCHEMA_VERSION = 3
CURRENT_APP_VERSION = "0.1.0"


class ImageFrame(BaseModel):
    index: int
    path: str
    filename: str
    file_size: int
    modified_time: datetime | None = None
    content_hash: str | None = None
    capture_time: datetime | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    lens_model: str | None = None
    iso: int | None = None
    aperture: float | None = None
    shutter_seconds: float | None = None
    focal_length: float | None = None
    width: int | None = None
    height: int | None = None
    orientation: int | None = None
    white_balance: str | None = None
    color_profile: str | None = None


class FrameMetrics(BaseModel):
    index: int
    mean_luminance: float
    median_luminance: float
    shadow_luminance: float
    highlight_luminance: float
    histogram: list[int]
    red_mean: float
    green_mean: float
    blue_mean: float
    white_balance_r_over_g: float
    white_balance_b_over_g: float


class CorrectionFrame(BaseModel):
    index: int
    exposure_ev: float = 0.0
    temperature_shift: float = 0.0
    tint_shift: float = 0.0


class FrameAnalysisFlags(BaseModel):
    index: int
    flags: list[str] = Field(default_factory=list)


class SequenceAnalysisReport(BaseModel):
    frame_count: int = 0
    median_luminance_min: float | None = None
    median_luminance_max: float | None = None
    median_luminance_mean: float | None = None
    white_balance_r_over_g_min: float | None = None
    white_balance_r_over_g_max: float | None = None
    white_balance_b_over_g_min: float | None = None
    white_balance_b_over_g_max: float | None = None
    capture_interval_seconds_median: float | None = None
    exposure_jump_frames: list[int] = Field(default_factory=list)
    white_balance_jump_frames: list[int] = Field(default_factory=list)
    aperture_flicker_candidate_frames: list[int] = Field(default_factory=list)
    discontinuity_frames: list[int] = Field(default_factory=list)
    frame_flags: list[FrameAnalysisFlags] = Field(default_factory=list)


class SequenceMetrics(BaseModel):
    frames: list[FrameMetrics] = Field(default_factory=list)
    exposure_curve: list[float] = Field(default_factory=list)
    color_curve: list[tuple[float, float]] = Field(default_factory=list)
    corrections: list[CorrectionFrame] = Field(default_factory=list)
    analysis_report: SequenceAnalysisReport = Field(default_factory=SequenceAnalysisReport)


class ProjectDocument(BaseModel):
    schema_version: int = CURRENT_SCHEMA_VERSION
    created_with_app_version: str = CURRENT_APP_VERSION
    last_saved_with_app_version: str = CURRENT_APP_VERSION
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_root: str
    frames: list[ImageFrame] = Field(default_factory=list)
    metrics: SequenceMetrics = Field(default_factory=SequenceMetrics)

    @property
    def source_path(self) -> Path:
        return Path(self.source_root)

    def resolve_frame_path(self, frame: ImageFrame) -> Path:
        path = Path(frame.path)
        if path.is_absolute():
            return path
        return self.source_path / path
