from __future__ import annotations

import math

from scipy.signal import savgol_filter

from holyrail.models import (
    CorrectionFrame,
    FrameMetrics,
    SequenceAnalysisReport,
    SequenceMetrics,
)


def _smooth(values: list[float]) -> list[float]:
    if len(values) < 5:
        return values
    window = min(len(values) if len(values) % 2 == 1 else len(values) - 1, 21)
    if window < 5:
        return values
    return [float(value) for value in savgol_filter(values, window_length=window, polyorder=2)]


def build_sequence_metrics(
    frames: list[FrameMetrics], analysis_report: SequenceAnalysisReport | None = None
) -> SequenceMetrics:
    luminance = [max(frame.median_luminance, 1e-6) for frame in frames]
    exposure_curve = _smooth([math.log2(value) for value in luminance])
    raw_r = [frame.white_balance_r_over_g for frame in frames]
    raw_b = [frame.white_balance_b_over_g for frame in frames]
    smooth_r = _smooth(raw_r)
    smooth_b = _smooth(raw_b)

    corrections: list[CorrectionFrame] = []
    for index, frame in enumerate(frames):
        exposure_ev = exposure_curve[index] - math.log2(max(frame.median_luminance, 1e-6))
        corrections.append(
            CorrectionFrame(
                index=frame.index,
                exposure_ev=float(exposure_ev),
                temperature_shift=float(smooth_b[index] - frame.white_balance_b_over_g),
                tint_shift=float(smooth_r[index] - frame.white_balance_r_over_g),
            )
        )

    return SequenceMetrics(
        frames=frames,
        exposure_curve=exposure_curve,
        color_curve=list(zip(smooth_r, smooth_b, strict=True)),
        corrections=corrections,
        analysis_report=analysis_report or SequenceAnalysisReport(),
    )
