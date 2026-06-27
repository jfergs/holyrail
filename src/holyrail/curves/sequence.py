from __future__ import annotations

import math

from scipy.signal import savgol_filter

from holyrail.models import (
    ColorCurveAnchor,
    CorrectionFrame,
    CurveAnchor,
    FrameMetrics,
    GeneratedColorCurve,
    GeneratedCurve,
    SequenceAnalysisReport,
    SequenceMetrics,
)


def _smooth(values: list[float], window: int | None = None) -> list[float]:
    if len(values) < 5:
        return values
    window = window or _smoothing_window(len(values))
    if window is None or window < 5:
        return values
    return [float(value) for value in savgol_filter(values, window_length=window, polyorder=2)]


def build_exposure_model(
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None = None,
    *,
    strength: float = 1.0,
    max_correction_ev: float = 1.0,
    smoothing_window: int | None = None,
) -> GeneratedCurve:
    luminance_ev = [math.log2(max(frame.median_luminance, 1e-6)) for frame in frames]
    window = _validate_smoothing_window(smoothing_window, len(frames))
    smoothed = _smooth_segmented(luminance_ev, frames, analysis_report, window)
    samples = [
        _clamp(float((target - observed) * strength), -max_correction_ev, max_correction_ev)
        for observed, target in zip(luminance_ev, smoothed, strict=True)
    ]
    anchors = [
        CurveAnchor(index=frame.index, value=samples[index]) for index, frame in enumerate(frames)
    ]
    return GeneratedCurve(
        kind="exposure",
        algorithm="segmented-savgol-log-luminance-v1",
        strength=strength,
        smoothing_window=window,
        anchors=anchors,
        samples=samples,
    )


def _smooth_segmented(
    values: list[float],
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None,
    window: int | None,
) -> list[float]:
    if analysis_report is None:
        return _smooth(values, window=window)

    flicker_indices = set(analysis_report.aperture_flicker_candidate_frames)
    protected_indices = {
        index
        for index in analysis_report.exposure_jump_frames
        if index not in flicker_indices and index - 1 not in flicker_indices
    } | set(analysis_report.discontinuity_frames)
    if not protected_indices:
        return _smooth(values, window=window)

    smoothed = values.copy()
    start = 0
    for position, frame in enumerate(frames):
        if position > start and frame.index in protected_indices:
            smoothed[start:position] = _smooth(values[start:position], window=window)
            start = position
    smoothed[start:] = _smooth(values[start:], window=window)
    return smoothed


def _smoothing_window(value_count: int) -> int | None:
    if value_count < 5:
        return None
    window = min(value_count if value_count % 2 == 1 else value_count - 1, 21)
    return window if window >= 5 else None


def _validate_smoothing_window(window: int | None, value_count: int) -> int | None:
    if window is None:
        return _smoothing_window(value_count)
    if window < 5:
        return None
    window = min(window, value_count if value_count % 2 == 1 else value_count - 1)
    if window % 2 == 0:
        window -= 1
    return window if window >= 5 else None


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def build_color_model(
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None = None,
    *,
    strength: float = 1.0,
    max_shift: float = 0.5,
    smoothing_window: int | None = None,
) -> GeneratedColorCurve:
    red_ratios = [frame.white_balance_r_over_g for frame in frames]
    blue_ratios = [frame.white_balance_b_over_g for frame in frames]
    window = _validate_smoothing_window(smoothing_window, len(frames))
    smooth_r = _smooth_color_segmented(red_ratios, frames, analysis_report, window)
    smooth_b = _smooth_color_segmented(blue_ratios, frames, analysis_report, window)
    red_samples = [
        _clamp(float((target - observed) * strength), -max_shift, max_shift)
        for observed, target in zip(red_ratios, smooth_r, strict=True)
    ]
    blue_samples = [
        _clamp(float((target - observed) * strength), -max_shift, max_shift)
        for observed, target in zip(blue_ratios, smooth_b, strict=True)
    ]
    anchors = [
        ColorCurveAnchor(
            index=frame.index,
            red_shift=red_samples[index],
            blue_shift=blue_samples[index],
        )
        for index, frame in enumerate(frames)
    ]
    return GeneratedColorCurve(
        algorithm="segmented-savgol-white-balance-ratio-v1",
        strength=strength,
        smoothing_window=window,
        anchors=anchors,
        red_samples=red_samples,
        blue_samples=blue_samples,
    )


def _smooth_color_segmented(
    values: list[float],
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None,
    window: int | None,
) -> list[float]:
    if analysis_report is None:
        return _smooth(values, window=window)

    protected_indices = set(analysis_report.discontinuity_frames)
    if not protected_indices:
        return _smooth(values, window=window)

    smoothed = values.copy()
    start = 0
    for position, frame in enumerate(frames):
        if position > start and frame.index in protected_indices:
            smoothed[start:position] = _smooth(values[start:position], window=window)
            start = position
    smoothed[start:] = _smooth(values[start:], window=window)
    return smoothed


def build_sequence_metrics(
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None = None,
    *,
    exposure_strength: float = 1.0,
    max_exposure_correction_ev: float = 1.0,
    exposure_smoothing_window: int | None = None,
    color_strength: float = 1.0,
    max_color_shift: float = 0.5,
    color_smoothing_window: int | None = None,
) -> SequenceMetrics:
    exposure_model = build_exposure_model(
        frames,
        analysis_report,
        strength=exposure_strength,
        max_correction_ev=max_exposure_correction_ev,
        smoothing_window=exposure_smoothing_window,
    )
    color_model = build_color_model(
        frames,
        analysis_report,
        strength=color_strength,
        max_shift=max_color_shift,
        smoothing_window=color_smoothing_window,
    )

    corrections: list[CorrectionFrame] = []
    for index, frame in enumerate(frames):
        corrections.append(
            CorrectionFrame(
                index=frame.index,
                exposure_ev=exposure_model.samples[index],
                temperature_shift=color_model.blue_samples[index],
                tint_shift=color_model.red_samples[index],
            )
        )

    return SequenceMetrics(
        frames=frames,
        exposure_curve=exposure_model.samples,
        exposure_model=exposure_model,
        color_curve=list(zip(color_model.red_samples, color_model.blue_samples, strict=True)),
        color_model=color_model,
        corrections=corrections,
        analysis_report=analysis_report or SequenceAnalysisReport(),
    )
