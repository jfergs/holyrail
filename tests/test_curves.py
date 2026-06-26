from holyrail.curves import build_sequence_metrics
from tests.synthetic_sequences import aperture_flicker_luminance, metrics, sunset_luminance


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
