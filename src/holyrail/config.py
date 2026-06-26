from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field


class AnalysisConfig(BaseModel):
    downsample_width: int = Field(default=1024, ge=128)
    histogram_bins: int = Field(default=256, ge=16)
    highlight_percentile: float = Field(default=99.0, gt=50.0, le=100.0)
    shadow_percentile: float = Field(default=1.0, ge=0.0, lt=50.0)


class ExposureCurveConfig(BaseModel):
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    max_correction_ev: float = Field(default=1.0, gt=0.0, le=5.0)
    smoothing_window: int | None = Field(default=None, ge=5)


class RenderConfig(BaseModel):
    jpeg_quality: int = Field(default=95, ge=1, le=100)
    preview_width: int = Field(default=1280, ge=128)
    output_extension: str = "jpg"


class HolyRailConfig(BaseModel):
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    exposure: ExposureCurveConfig = Field(default_factory=ExposureCurveConfig)
    render: RenderConfig = Field(default_factory=RenderConfig)

    @classmethod
    def load(cls, path: Path | None) -> HolyRailConfig:
        if path is None:
            return cls()
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        return cls.model_validate(data)
