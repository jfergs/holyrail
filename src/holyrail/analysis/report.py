from __future__ import annotations

import math
from datetime import datetime
from statistics import median

from holyrail.models import (
    FrameAnalysisFlags,
    FrameMetrics,
    ImageFrame,
    SequenceAnalysisReport,
)

EXPOSURE_JUMP_EV_THRESHOLD = 0.5
WHITE_BALANCE_JUMP_THRESHOLD = 0.18
APERTURE_FLICKER_EV_THRESHOLD = 0.22
DISCONTINUITY_MIN_SECONDS = 60.0


def build_analysis_report(
    frames: list[ImageFrame], metrics: list[FrameMetrics]
) -> SequenceAnalysisReport:
    if not metrics:
        return SequenceAnalysisReport()

    median_luminance = [frame.median_luminance for frame in metrics]
    r_ratios = [frame.white_balance_r_over_g for frame in metrics]
    b_ratios = [frame.white_balance_b_over_g for frame in metrics]
    exposure_jump_frames = _detect_exposure_jumps(metrics)
    white_balance_jump_frames = _detect_white_balance_jumps(metrics)
    aperture_flicker_frames = _detect_aperture_flicker(metrics)
    discontinuity_frames = _detect_capture_discontinuities(frames)
    frame_flags = _build_frame_flags(
        metrics,
        exposure_jump_frames=exposure_jump_frames,
        white_balance_jump_frames=white_balance_jump_frames,
        aperture_flicker_frames=aperture_flicker_frames,
        discontinuity_frames=discontinuity_frames,
    )

    return SequenceAnalysisReport(
        frame_count=len(metrics),
        median_luminance_min=min(median_luminance),
        median_luminance_max=max(median_luminance),
        median_luminance_mean=sum(median_luminance) / len(median_luminance),
        white_balance_r_over_g_min=min(r_ratios),
        white_balance_r_over_g_max=max(r_ratios),
        white_balance_b_over_g_min=min(b_ratios),
        white_balance_b_over_g_max=max(b_ratios),
        capture_interval_seconds_median=_median_capture_interval_seconds(frames),
        exposure_jump_frames=exposure_jump_frames,
        white_balance_jump_frames=white_balance_jump_frames,
        aperture_flicker_candidate_frames=aperture_flicker_frames,
        discontinuity_frames=discontinuity_frames,
        frame_flags=frame_flags,
    )


def _detect_exposure_jumps(metrics: list[FrameMetrics]) -> list[int]:
    jumps: list[int] = []
    for previous, current in zip(metrics, metrics[1:], strict=False):
        previous_ev = math.log2(max(previous.median_luminance, 1e-6))
        current_ev = math.log2(max(current.median_luminance, 1e-6))
        if abs(current_ev - previous_ev) >= EXPOSURE_JUMP_EV_THRESHOLD:
            jumps.append(current.index)
    return jumps


def _detect_white_balance_jumps(metrics: list[FrameMetrics]) -> list[int]:
    jumps: list[int] = []
    for previous, current in zip(metrics, metrics[1:], strict=False):
        red_delta = abs(current.white_balance_r_over_g - previous.white_balance_r_over_g)
        blue_delta = abs(current.white_balance_b_over_g - previous.white_balance_b_over_g)
        if max(red_delta, blue_delta) >= WHITE_BALANCE_JUMP_THRESHOLD:
            jumps.append(current.index)
    return jumps


def _detect_aperture_flicker(metrics: list[FrameMetrics]) -> list[int]:
    if len(metrics) < 5:
        return []

    luminance_ev = [math.log2(max(frame.median_luminance, 1e-6)) for frame in metrics]
    flicker_frames: list[int] = []
    for index in range(1, len(metrics) - 1):
        local_expected = (luminance_ev[index - 1] + luminance_ev[index + 1]) / 2
        residual = luminance_ev[index] - local_expected
        if abs(residual) >= APERTURE_FLICKER_EV_THRESHOLD:
            flicker_frames.append(metrics[index].index)
    return flicker_frames


def _detect_capture_discontinuities(frames: list[ImageFrame]) -> list[int]:
    timestamped = [(frame.index, frame.capture_time) for frame in frames if frame.capture_time]
    if len(timestamped) < 3:
        return []

    intervals = [
        _seconds_between(previous_time, current_time)
        for (_, previous_time), (_, current_time) in zip(timestamped, timestamped[1:], strict=False)
    ]
    expected = median(intervals)
    threshold = max(expected * 2.5, DISCONTINUITY_MIN_SECONDS)
    return [
        current_index
        for ((_, previous_time), (current_index, current_time)), interval in zip(
            zip(timestamped, timestamped[1:], strict=False), intervals, strict=False
        )
        if interval >= threshold and _seconds_between(previous_time, current_time) >= threshold
    ]


def _median_capture_interval_seconds(frames: list[ImageFrame]) -> float | None:
    capture_times = [frame.capture_time for frame in frames if frame.capture_time]
    if len(capture_times) < 2:
        return None
    intervals = [
        _seconds_between(previous, current)
        for previous, current in zip(capture_times, capture_times[1:], strict=False)
    ]
    return float(median(intervals))


def _seconds_between(previous: datetime, current: datetime) -> float:
    return abs((current - previous).total_seconds())


def _build_frame_flags(
    metrics: list[FrameMetrics],
    *,
    exposure_jump_frames: list[int],
    white_balance_jump_frames: list[int],
    aperture_flicker_frames: list[int],
    discontinuity_frames: list[int],
) -> list[FrameAnalysisFlags]:
    exposure_jumps = set(exposure_jump_frames)
    white_balance_jumps = set(white_balance_jump_frames)
    aperture_flicker = set(aperture_flicker_frames)
    discontinuities = set(discontinuity_frames)
    flagged_frames: list[FrameAnalysisFlags] = []
    for frame in metrics:
        flags: list[str] = []
        if frame.index in exposure_jumps:
            flags.append("exposure_jump")
        if frame.index in white_balance_jumps:
            flags.append("white_balance_jump")
        if frame.index in aperture_flicker:
            flags.append("aperture_flicker_candidate")
        if frame.index in discontinuities:
            flags.append("capture_discontinuity")
        if flags:
            flagged_frames.append(FrameAnalysisFlags(index=frame.index, flags=flags))
    return flagged_frames
