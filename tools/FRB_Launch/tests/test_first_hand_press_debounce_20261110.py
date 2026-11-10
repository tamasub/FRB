"""First Hand switch-chatter regression with timers advanced deterministically.

Run the real ShurikenButton handlers in the no-PySide6 Qt stand-in. Windows
native input/paint still needs a physical device acceptance check.
"""
from pytest import mark
from unittest.mock import Mock
from test_shuriken_confirm_click_and_paint_20261105 import (
    DummyEvent, Preview, load_button_module, make_button,
)
from test_first_hand_wheel_confirmation_20261110 import build, click, Wheel


def setup_hand(count=4):
    mod = load_button_module()
    mod.ShurikenPreview = Preview
    hand, launcher = make_button(mod)
    launcher.shuriken_items.return_value = build(count)
    hand._press_timer.autofire = False
    hand._release_timer.autofire = False
    return hand, launcher


def evt(dx=0, dy=0):
    return DummyEvent(global_x=100 + dx, global_y=100 + dy)


def test_subthreshold_press_never_shows_a_preview_or_opens_confirmation():
    hand, _ = setup_hand()
    hand.mousePressEvent(evt())
    assert hand._press_timer.active
    assert hand._preview is None
    hand.mouseReleaseEvent(evt())
    assert not hand._press_timer.active
    hand._press_timer.fire()
    assert hand._preview is None
    assert hand._pending_confirmation is None
    hand.triggered.emit.assert_not_called()


@mark.parametrize('count,dx,dy,item_index', [
    (1,0,-40,0), (2,40,0,1), (3,0,40,2),
    (4,0,-40,0), (4,40,0,1), (4,0,40,2), (4,-40,0,3),
])
def test_qualified_press_then_settled_release_only_opens_confirmation(count,dx,dy,item_index):
    hand, _ = setup_hand(count)
    hand.mousePressEvent(evt())
    hand.mouseMoveEvent(evt(dx,dy))
    assert hand._preview is None and hand._selected_entry is None
    hand._press_timer.fire()  # exactly one 250ms qualification
    assert hand._press_qualified
    assert hand._preview.present.call_count == 1
    selected = hand._selected_entry
    assert selected.item_id == f'item_{item_index}'
    hand.mouseReleaseEvent(evt(dx,dy))
    assert hand._release_pending
    assert hand._pending_confirmation is None
    assert hand._preview.hide.call_count == 0
    hand._release_timer.fire()  # 120ms uninterrupted release
    assert hand._pending_confirmation.candidate_id == selected.item_id
    assert hand._selected_entry is selected
    assert hand._preview.hide.call_count == 0
    hand.triggered.emit.assert_not_called()
    hand.wheelEvent(Wheel(-120))
    click(hand)  # separate new deliberate click, after post-confirm grace
    hand.triggered.emit.assert_called_once_with(selected.item_id)


def test_release_press_bounce_keeps_same_preview_and_selection_without_confirmation():
    hand, _ = setup_hand(4)
    hand.mousePressEvent(evt())
    hand._press_timer.fire()
    hand.mouseMoveEvent(evt(0,-45))
    selected = hand._selected_entry
    hand.mouseReleaseEvent(evt(0,-45))
    assert hand._release_pending and hand._release_timer.active
    hand.mousePressEvent(evt(0,-45))  # transient re-press inside 120ms
    assert not hand._release_pending and not hand._release_timer.active
    hand._release_timer.fire()
    assert hand._pending_confirmation is None
    assert hand._selected_entry is selected
    hand._preview.hide.assert_not_called()
    hand.mouseMoveEvent(evt(0,0))  # return to center to intentionally cancel
    assert hand._selected_entry is None
    hand.mouseReleaseEvent(evt())
    hand._release_timer.fire()
    assert hand._pending_confirmation is None
    hand.triggered.emit.assert_not_called()
    hand._preview.hide.assert_called_once()


def test_short_early_release_press_requires_new_250ms_qualification():
    hand, _ = setup_hand(4)
    hand.mousePressEvent(evt())
    hand.mouseReleaseEvent(evt())  # no qualification yet
    hand.mousePressEvent(evt())
    assert hand._preview is None
    assert hand._press_timer.active
    hand._press_timer.fire()
    assert hand._press_qualified and hand._preview is not None


def test_bounce_returned_as_native_double_click_is_suppressed():
    hand, _ = setup_hand(4)
    hand.mousePressEvent(evt())
    hand._press_timer.fire()
    hand.mouseMoveEvent(evt(0,-45))
    hand.mouseReleaseEvent(evt(0,-45))
    double = evt(0,-45)
    hand.mouseDoubleClickEvent(double)
    assert double.accepted
    assert not hand._release_pending
    hand._release_timer.fire()
    assert hand._pending_confirmation is None
    hand.triggered.emit.assert_not_called()


def test_confirm_guard_is_independent_of_press_qualification():
    hand, _ = setup_hand(4)
    assert hand.PRESS_QUALIFY_MS == 250
    assert hand.RELEASE_SETTLE_MS == 120
    assert hand.CONFIRM_CLICK_GRACE_SECONDS == 0.25
    hand.mousePressEvent(evt())
    hand._press_timer.fire()
    hand.mouseMoveEvent(evt(0,-40))
    hand.mouseReleaseEvent(evt(0,-40))
    hand._release_timer.fire()
    pending = hand._pending_confirmation
    assert pending is not None and pending.choice == 'cancel'
    # Immediate ghost click must not close the dialog.
    hand.mousePressEvent(evt())
    hand.mouseReleaseEvent(evt())
    assert hand._pending_confirmation is pending
    hand.triggered.emit.assert_not_called()
