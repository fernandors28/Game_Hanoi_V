from collections import deque

import pytest

from camera_Game import ControlGesto


def test_smooth_cursor_reduces_raw_jitter():
    current = (0.0, 0.0, 0.0)
    target = (10.0, -2.0, 8.0)

    smoothed = ControlGesto._smooth_cursor_position(current, target, smoothing=0.35)

    assert smoothed == pytest.approx((3.5, -0.7, 2.8))


def test_smooth_cursor_ignores_small_noise():
    current = (1.0, 0.0, 2.0)
    target = (1.08, 0.0, 2.03)

    smoothed = ControlGesto._smooth_cursor_position(current, target, smoothing=0.35)

    assert smoothed == pytest.approx(current)


def test_grab_state_is_stable_across_small_noise():
    gesto = ControlGesto.__new__(ControlGesto)
    gesto._grab_state = False
    gesto._grab_samples = deque(maxlen=4)
    gesto.grab_close_threshold = 0.12
    gesto.grab_open_threshold = 0.16

    assert gesto._update_grab_state(0.11) is True
    assert gesto._update_grab_state(0.13) is True
    assert gesto._update_grab_state(0.15) is True
    assert gesto._update_grab_state(0.18) is False
    assert gesto._update_grab_state(0.19) is False


