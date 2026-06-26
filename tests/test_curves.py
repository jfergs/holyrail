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
