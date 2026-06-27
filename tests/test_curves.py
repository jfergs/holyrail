from holyrail.analysis.report import build_analysis_report
from holyrail.curves import build_sequence_metrics
from tests.synthetic_sequences import (
    aperture_flicker_luminance,
    frames,
    golden_hour_red_values,
    holy_grail_luminance,
    metrics,
    sunset_luminance,
)


def test_exposure_model_preserves_gradual_sunset_trend() -> None:
    sequence_metrics = build_sequence_metrics(metrics(sunset_luminance(12)))

    assert sequence_metrics.exposure_model is not None
    assert sequence_metrics.exposure_model.kind == "exposure"
    assert max(abs(sample) for sample in sequence_metrics.exposure_model.samples) < 0.01


def test_exposure_model_reduces_single_frame_flicker() -> None:
    sequence_metrics = build_sequence_metrics(metrics(aperture_flicker_luminance()))

    assert sequence_metrics.exposure_model is not None
    assert sequence_metrics.exposure_model.samples[3] < -0.2
    assert sequence_metrics.corrections[3].exposure_ev == sequence_metrics.exposure_model.samples[3]


def test_exposure_model_strength_scales_corrections() -> None:
    full_strength = build_sequence_metrics(metrics(aperture_flicker_luminance()))
    half_strength = build_sequence_metrics(
        metrics(aperture_flicker_luminance()), exposure_strength=0.5
    )

    assert half_strength.exposure_model is not None
    assert full_strength.exposure_model is not None
    assert half_strength.exposure_model.samples[3] == full_strength.exposure_model.samples[3] * 0.5


def test_exposure_model_clamps_extreme_corrections() -> None:
    sequence_metrics = build_sequence_metrics(
        metrics([0.2, 0.2, 0.2, 0.9, 0.2, 0.2, 0.2]),
        max_exposure_correction_ev=0.25,
    )

    assert sequence_metrics.exposure_model is not None
    assert min(sequence_metrics.exposure_model.samples) == -0.25


def test_exposure_model_does_not_smooth_across_holy_grail_step() -> None:
    sequence_frames = frames(6)
    sequence_metrics_input = metrics(holy_grail_luminance())
    report = build_analysis_report(sequence_frames, sequence_metrics_input)
    sequence_metrics = build_sequence_metrics(sequence_metrics_input, analysis_report=report)

    assert sequence_metrics.exposure_model is not None
    assert report.exposure_jump_frames == [3]
    assert max(abs(sample) for sample in sequence_metrics.exposure_model.samples) == 0.0


def test_exposure_model_still_corrects_flicker_with_analysis_report() -> None:
    sequence_frames = frames(7)
    sequence_metrics_input = metrics(aperture_flicker_luminance())
    report = build_analysis_report(sequence_frames, sequence_metrics_input)
    sequence_metrics = build_sequence_metrics(sequence_metrics_input, analysis_report=report)

    assert sequence_metrics.exposure_model is not None
    assert sequence_metrics.exposure_model.samples[3] < -0.2


def test_color_model_preserves_gradual_golden_hour_trend() -> None:
    red_values = golden_hour_red_values(12)
    sequence_metrics = build_sequence_metrics(
        metrics([0.25] * 12, red_values=red_values),
    )

    assert sequence_metrics.color_model is not None
    assert max(abs(sample) for sample in sequence_metrics.color_model.red_samples) < 0.01
    assert max(abs(correction.tint_shift) for correction in sequence_metrics.corrections) < 0.01


def test_color_model_corrects_abrupt_awb_jump() -> None:
    red_values = [1.0, 1.0, 1.0, 1.35, 1.35, 1.35, 1.35]
    sequence_frames = frames(7)
    sequence_metrics_input = metrics([0.25] * 7, red_values=red_values)
    report = build_analysis_report(sequence_frames, sequence_metrics_input)
    sequence_metrics = build_sequence_metrics(sequence_metrics_input, analysis_report=report)

    assert sequence_metrics.color_model is not None
    assert report.white_balance_jump_frames == [3]
    assert sequence_metrics.color_model.red_samples[3] < -0.1
    assert sequence_metrics.corrections[3].tint_shift == sequence_metrics.color_model.red_samples[3]
