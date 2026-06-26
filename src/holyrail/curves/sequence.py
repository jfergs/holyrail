from __future__ import annotations

import math

from scipy.signal import savgol_filter

from holyrail.models import (
    CorrectionFrame,
    CurveAnchor,
    FrameMetrics,
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
    *,
    strength: float = 1.0,
    max_correction_ev: float = 1.0,
    smoothing_window: int | None = None,
) -> GeneratedCurve:
    luminance_ev = [math.log2(max(frame.median_luminance, 1e-6)) for frame in frames]
    window = _validate_smoothing_window(smoothing_window, len(frames))
    smoothed = _smooth(luminance_ev, window=window)
    samples = [
        _clamp(float((target - observed) * strength), -max_correction_ev, max_correction_ev)
        for observed, target in zip(luminance_ev, smoothed, strict=True)
    ]
    anchors = [
        CurveAnchor(index=frame.index, value=samples[index]) for index, frame in enumerate(frames)
    ]
    return GeneratedCurve(
        kind="exposure",
        algorithm="savgol-log-luminance-v1",
        strength=strength,
        smoothing_window=window,
        anchors=anchors,
        samples=samples,
    )


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


def build_sequence_metrics(
    frames: list[FrameMetrics],
    analysis_report: SequenceAnalysisReport | None = None,
    *,
    exposure_strength: float = 1.0,
    max_exposure_correction_ev: float = 1.0,
    exposure_smoothing_window: int | None = None,
) -> SequenceMetrics:
    exposure_model = build_exposure_model(
        frames,
        strength=exposure_strength,
        max_correction_ev=max_exposure_correction_ev,
        smoothing_window=exposure_smoothing_window,
    )
    raw_r = [frame.white_balance_r_over_g for frame in frames]
    raw_b = [frame.white_balance_b_over_g for frame in frames]
    smooth_r = _smooth(raw_r)
    smooth_b = _smooth(raw_b)

    corrections: list[CorrectionFrame] = []
    for index, frame in enumerate(frames):
        corrections.append(
            CorrectionFrame(
                index=frame.index,
                exposure_ev=exposure_model.samples[index],
                temperature_shift=float(smooth_b[index] - frame.white_balance_b_over_g),
                tint_shift=float(smooth_r[index] - frame.white_balance_r_over_g),
            )
        )

    return SequenceMetrics(
        frames=frames,
        exposure_curve=exposure_model.samples,
        exposure_model=exposure_model,
        color_curve=list(zip(smooth_r, smooth_b, strict=True)),
        corrections=corrections,
        analysis_report=analysis_report or SequenceAnalysisReport(),
    )
