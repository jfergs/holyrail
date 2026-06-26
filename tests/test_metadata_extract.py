from types import SimpleNamespace

from holyrail.metadata.extract import _raw_white_balance_name


def test_raw_white_balance_name_prefers_camera_white_balance() -> None:
    raw = SimpleNamespace(camera_whitebalance=[2.0, 1.0, 1.5, 1.0], daylight_whitebalance=[1])

    assert _raw_white_balance_name(raw) == "camera"


def test_raw_white_balance_name_uses_daylight_when_camera_absent() -> None:
    raw = SimpleNamespace(camera_whitebalance=None, daylight_whitebalance=[2.0, 1.0, 1.5, 1.0])

    assert _raw_white_balance_name(raw) == "daylight"


def test_raw_white_balance_name_handles_missing_data() -> None:
    raw = SimpleNamespace()

    assert _raw_white_balance_name(raw) is None
