from __future__ import annotations

from datetime import UTC, datetime, timedelta

from holyrail.models import FrameMetrics, ImageFrame


def frames(
    count: int, *, start: datetime | None = None, step_seconds: int = 10
) -> list[ImageFrame]:
    start = start or datetime(2026, 6, 26, 12, 0, tzinfo=UTC)
    return [
        ImageFrame(
            index=index,
            path=f"{index:04d}.jpg",
            filename=f"{index:04d}.jpg",
            file_size=1,
            capture_time=start + timedelta(seconds=index * step_seconds),
        )
        for index in range(count)
    ]


def metrics(
    luminance_values: list[float],
    *,
    red_values: list[float] | None = None,
    blue_values: list[float] | None = None,
) -> list[FrameMetrics]:
    red_values = red_values or [1.0] * len(luminance_values)
    blue_values = blue_values or [1.0] * len(luminance_values)
    return [
        FrameMetrics(
            index=index,
            mean_luminance=luminance,
            median_luminance=luminance,
            shadow_luminance=luminance * 0.5,
            highlight_luminance=min(luminance * 1.5, 1.0),
            histogram=[1],
            red_mean=red,
            green_mean=1.0,
            blue_mean=blue,
            white_balance_r_over_g=red,
            white_balance_b_over_g=blue,
        )
        for index, (luminance, red, blue) in enumerate(
            zip(luminance_values, red_values, blue_values, strict=True)
        )
    ]


def sunset_luminance(count: int) -> list[float]:
    return [0.75 - index * 0.025 for index in range(count)]


def sunrise_luminance(count: int) -> list[float]:
    return [0.12 + index * 0.025 for index in range(count)]


def holy_grail_luminance() -> list[float]:
    return [0.20, 0.21, 0.22, 0.45, 0.46, 0.47]


def aperture_flicker_luminance() -> list[float]:
    return [0.20, 0.20, 0.20, 0.29, 0.20, 0.20, 0.20]


def awb_jump_red_values(count: int) -> list[float]:
    return [1.0 if index < count // 2 else 1.32 for index in range(count)]


def golden_hour_red_values(count: int) -> list[float]:
    return [1.0 + index * 0.025 for index in range(count)]


def blue_hour_blue_values(count: int) -> list[float]:
    return [1.0 + index * 0.025 for index in range(count)]
