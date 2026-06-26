from datetime import UTC, datetime, timedelta

from holyrail.analysis.report import build_analysis_report
from holyrail.models import FrameMetrics, ImageFrame


def _frame(index: int, capture_time: datetime | None = None) -> ImageFrame:
    return ImageFrame(
        index=index,
        path=f"{index:04d}.jpg",
        filename=f"{index:04d}.jpg",
        file_size=1,
        capture_time=capture_time,
    )


def _metrics(index: int, luminance: float, red: float = 1.0, blue: float = 1.0) -> FrameMetrics:
    return FrameMetrics(
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


def test_analysis_report_detects_exposure_and_white_balance_jumps() -> None:
    frames = [_frame(index) for index in range(4)]
    metrics = [
        _metrics(0, 0.20),
        _metrics(1, 0.21),
        _metrics(2, 0.50),
        _metrics(3, 0.51, red=1.4),
    ]

    report = build_analysis_report(frames, metrics)

    assert report.frame_count == 4
    assert report.exposure_jump_frames == [2]
    assert report.white_balance_jump_frames == [3]
    assert any(flag.index == 2 and "exposure_jump" in flag.flags for flag in report.frame_flags)


def test_analysis_report_detects_capture_discontinuities() -> None:
    start = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)
    frames = [
        _frame(0, start),
        _frame(1, start + timedelta(seconds=10)),
        _frame(2, start + timedelta(seconds=20)),
        _frame(3, start + timedelta(minutes=10)),
    ]
    metrics = [_metrics(index, 0.2) for index in range(4)]

    report = build_analysis_report(frames, metrics)

    assert report.capture_interval_seconds_median == 10.0
    assert report.discontinuity_frames == [3]
