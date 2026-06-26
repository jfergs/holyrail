from datetime import UTC, datetime, timedelta

from holyrail.analysis.report import build_analysis_report
from holyrail.models import FrameMetrics, ImageFrame
from tests.synthetic_sequences import (
    aperture_flicker_luminance,
    awb_jump_red_values,
    frames,
    holy_grail_luminance,
    metrics,
    sunrise_luminance,
    sunset_luminance,
)


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


def test_analysis_report_preserves_gradual_sunset_trend() -> None:
    report = build_analysis_report(frames(12), metrics(sunset_luminance(12)))

    assert report.exposure_jump_frames == []
    assert report.aperture_flicker_candidate_frames == []
    assert report.median_luminance_max > report.median_luminance_min


def test_analysis_report_preserves_gradual_sunrise_trend() -> None:
    report = build_analysis_report(frames(12), metrics(sunrise_luminance(12)))

    assert report.exposure_jump_frames == []
    assert report.aperture_flicker_candidate_frames == []
    assert report.median_luminance_max > report.median_luminance_min


def test_analysis_report_flags_holy_grail_exposure_step() -> None:
    report = build_analysis_report(frames(6), metrics(holy_grail_luminance()))

    assert report.exposure_jump_frames == [3]


def test_analysis_report_flags_single_aperture_flicker_candidate() -> None:
    report = build_analysis_report(frames(7), metrics(aperture_flicker_luminance()))

    assert report.aperture_flicker_candidate_frames == [3]


def test_analysis_report_flags_awb_jump_without_exposure_jump() -> None:
    red_values = awb_jump_red_values(8)
    report = build_analysis_report(
        frames(8),
        metrics([0.25] * 8, red_values=red_values),
    )

    assert report.white_balance_jump_frames == [4]
    assert report.exposure_jump_frames == []


def test_analysis_report_flags_multiday_sequence_gap() -> None:
    start = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)
    sequence_frames = frames(4, start=start, step_seconds=10)
    sequence_frames.append(
        ImageFrame(
            index=4,
            path="0004.jpg",
            filename="0004.jpg",
            file_size=1,
            capture_time=start + timedelta(days=1),
        )
    )

    report = build_analysis_report(sequence_frames, metrics([0.2] * 5))

    assert report.discontinuity_frames == [4]
