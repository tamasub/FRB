"""Confirmation click grace: block ghost Qt events, not human Cancel.

Time is injected into the actual mousePressEvent function rather than sleeping.
The UI remains anchored on the same First Hand button; 1-4 sectors are tested.
"""
from unittest.mock import patch

import pytest
from test_first_hand_wheel_confirmation_20261110 import make_flick, Wheel
from test_shuriken_confirm_click_and_paint_20261105 import DummyEvent


class FakeClock:
    def __init__(self, value=100.0):
        self.value = value
    def __call__(self):
        return self.value


def press(button):
    button.mousePressEvent(DummyEvent())


def release(button):
    button.mouseReleaseEvent(DummyEvent())


@pytest.mark.parametrize('count,dx,dy', [(1,0,-45),(2,45,0),(3,-45,-45),(4,0,-45)])
def test_ghost_click_before_250ms_ignored_then_default_cancel_with_one_click(count,dx,dy):
    button,_,chosen = make_flick(count,dx,dy)
    pending = button._pending_confirmation
    assert pending.choice == 'cancel'
    assert pending.wheel_selected is False
    assert button.CONFIRM_CLICK_GRACE_SECONDS == .250
    button._confirmation_opened_at = 100.0
    clock = FakeClock(100.249)
    with patch.dict(button.mousePressEvent.__func__.__globals__, {'monotonic': clock}):
        press(button)
        release(button)
        assert button._pending_confirmation is pending
        assert button._selected_entry is chosen
        button._preview.hide.assert_not_called()
        button.triggered.emit.assert_not_called()
        # Once the guard has passed, an ordinary new click must cancel.
        clock.value = 100.251
        press(button)
        release(button)
    assert button._pending_confirmation is None
    assert button._preview.hide.call_count == 1
    button.triggered.emit.assert_not_called()


def test_press_just_before_guard_cannot_become_a_click_by_releasing_after_guard():
    button,_,chosen=make_flick(4,0,-45)
    button._confirmation_opened_at=100.0
    clock=FakeClock(100.249)
    with patch.dict(button.mousePressEvent.__func__.__globals__, {'monotonic': clock}):
        press(button)
        # The Release may arrive much later. Only the Press can arm.
        clock.value=101.0
        release(button)
        assert button._pending_confirmation is not None
        assert button._selected_entry is chosen
        button.triggered.emit.assert_not_called()
        press(button)
        release(button)
    assert button._pending_confirmation is None


def test_wheel_ok_before_guard_does_not_execute_early_click():
    button,_,chosen=make_flick(4,0,-45)
    button._confirmation_opened_at=100.0
    clock=FakeClock(100.050)
    button.wheelEvent(Wheel(-120))
    assert button._pending_confirmation.choice == 'ok'
    with patch.dict(button.mousePressEvent.__func__.__globals__, {'monotonic': clock}):
        press(button)
        release(button)
        assert button._pending_confirmation is not None
        button.triggered.emit.assert_not_called()
        clock.value=100.251
        press(button)
        release(button)
    button.triggered.emit.assert_called_once_with(chosen.item_id)
    assert button._pending_confirmation is None


def test_ghost_release_without_new_press_does_not_cancel_even_after_guard():
    button,_,chosen=make_flick(4,0,-45)
    button._confirmation_opened_at=100.0
    clock=FakeClock(101.0)
    with patch.dict(button.mousePressEvent.__func__.__globals__, {'monotonic': clock}):
        release(button)
        release(button)
    assert button._pending_confirmation is not None
    assert button._selected_entry is chosen
    button.triggered.emit.assert_not_called()


def test_real_overlay_cancel_still_possible_without_wheel():
    button,_,_=make_flick(4,0,-45)
    button.confirm_from_overlay('cancel')
    assert button._pending_confirmation is None
    button.triggered.emit.assert_not_called()


def test_native_double_click_while_confirmation_open_never_confirms():
    button, _, chosen = make_flick(4, 0, -45)
    button._confirmation_opened_at = 100.0
    clock = FakeClock(101.0)
    with patch.dict(button.mousePressEvent.__func__.__globals__, {'monotonic': clock}):
        # The double-click's SECOND down is not an ordinary confirmation Press.
        # Qt can still send a matching mouse release afterwards.
        event = DummyEvent()
        button.mouseDoubleClickEvent(event)
        assert event.accepted
        release(button)
    assert button._pending_confirmation is not None
    assert button._selected_entry is chosen
    button.triggered.emit.assert_not_called()


def test_native_double_click_cannot_confirm_ok_after_wheel():
    button, _, chosen = make_flick(4, 0, -45)
    button.wheelEvent(Wheel(-120))
    assert button._pending_confirmation.choice == 'ok'
    event = DummyEvent()
    button.mouseDoubleClickEvent(event)
    button.mouseReleaseEvent(DummyEvent())
    assert event.accepted
    assert button._pending_confirmation is not None
    button.triggered.emit.assert_not_called()
