"""Safety contract: 1..4 actions share geometry; the FIRST-HAND button itself
is the sole wheel and click controller for the in-place confirmation overlay.
No first-flick release, stale release, or empty wheel can execute a command.
"""
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from test_shuriken_confirm_click_and_paint_20261105 import (
    load_button_module, DummyEvent, make_button, Preview,
)
from shuriken_model import configured_entries, choose_entry, current_indicator_position
from first_hand_confirmation import FirstHandConfirmation, CANCEL, OK


class Wheel:
    def __init__(self, y=0, pixels=0):
        self.y = y
        self.pixels = pixels
        self.accepted = False
    def angleDelta(self):
        return NS(y=lambda: self.y)
    def pixelDelta(self):
        return NS(y=lambda: self.pixels)
    def accept(self):
        self.accepted = True


def build(count):
    rows = [dict(item_id=f'item_{i}',title=f'選択候補{i}',enabled=True,
                 shuriken_enabled=True,shuriken_order=(i+1)*10,
                 shuriken_direction='legacy_wrong', shuriken_button_index=1)
            for i in range(count)]
    return configured_entries({'items':rows})


def make_flick(count, dx, dy):
    mod=load_button_module()
    mod.ShurikenPreview=Preview
    button, launcher=make_button(mod)
    launcher.shuriken_items.return_value=build(count)
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_x=100+dx,global_y=100+dy))
    chosen=button._selected_entry
    button.mouseReleaseEvent(DummyEvent(global_x=100+dx,global_y=100+dy))
    return button,launcher,chosen


def click(button, x=20, *, after_grace=True):
    # Simulate the user's deliberate NEW click after the 250-ms guard,
    # without sleeping in headless tests. Set False to test ghost clicks
    # that arrive immediately after showing the confirmation.
    if after_grace and button._pending_confirmation is not None:
        button._confirmation_opened_at -= button.CONFIRM_CLICK_GRACE_SECONDS + .01
    button.mousePressEvent(DummyEvent(x=x))
    button.mouseReleaseEvent(DummyEvent(x=x))


@pytest.mark.parametrize('count,dx,dy,index', [
    (1,0,-45,0),
    (2,-45,0,0),(2,45,0,1),
    (3,-45,-45,0),(3,45,-45,1),(3,0,45,2),
    (4,0,-45,0),(4,45,0,1),(4,0,45,2),(4,-45,0,3),
])
def test_every_count_freezes_eye_candidate_without_executing(count,dx,dy,index):
    button,launcher,chosen=make_flick(count,dx,dy)
    assert chosen.item_id == f'item_{index}'
    assert button._pending_confirmation.candidate_id == chosen.item_id
    assert button._pending_confirmation.candidate_title == chosen.title
    assert button._selected_entry == chosen
    assert current_indicator_position(button._entries,chosen.item_id)!=(0,0)
    button._preview.hide.assert_not_called()
    button._preview.set_confirmation.assert_called_with(button._pending_confirmation)
    button.triggered.emit.assert_not_called()
    button.mouseReleaseEvent(DummyEvent())  # ghost release
    button.triggered.emit.assert_not_called()
    assert button._pending_confirmation.candidate_id == chosen.item_id


def test_early_ghost_click_is_ignored_but_later_default_cancel_works():
    button,_,chosen=make_flick(4,0,-45)
    pending=button._pending_confirmation
    # Ghost press/release in the initial grace period cannot dismiss Cancel.
    click(button, after_grace=False)
    assert button._pending_confirmation is pending
    assert button._selected_entry is chosen
    button.triggered.emit.assert_not_called()
    button._preview.hide.assert_not_called()
    # After the grace period, a NEW click must accept the initial Cancel
    # without first forcing the wheel through OK (the reported regression).
    click(button)
    assert button._pending_confirmation is None
    button.triggered.emit.assert_not_called()


def test_wheel_over_first_hand_button_selects_ok_and_separate_click_executes_once():
    button,_,_=make_flick(4,0,-45)
    wheel=Wheel(-120)
    button.wheelEvent(wheel)
    assert wheel.accepted
    assert button._pending_confirmation.choice==OK
    assert button._pending_confirmation.wheel_selected
    button.triggered.emit.assert_not_called()
    button._preview.hide.assert_not_called()
    # The same button must receive a fresh press AND release to authorize.
    click(button)
    button.triggered.emit.assert_called_once_with('item_0')
    assert button._pending_confirmation is None
    assert button._selected_entry is None
    button._preview.hide.assert_called_once_with()
    button.mouseReleaseEvent(DummyEvent())
    button.triggered.emit.assert_called_once_with('item_0')


def test_wheel_cancel_suppresses_execution_even_after_ok():
    button,_,_=make_flick(3,45,-45)
    button.wheelEvent(Wheel(-120))  # OK
    button.wheelEvent(Wheel(120))   # cancel
    assert button._pending_confirmation.choice==CANCEL
    click(button)
    button.triggered.emit.assert_not_called()


def test_partial_wheel_does_not_select_ok_and_wheel_without_click_never_runs():
    button,_,_=make_flick(4,45,0)
    button.wheelEvent(Wheel(pixels=-18))
    assert button._pending_confirmation.choice==CANCEL
    button.triggered.emit.assert_not_called()
    button.wheelEvent(Wheel(pixels=-18))
    assert button._pending_confirmation.choice==OK
    assert button._pending_confirmation.candidate_id=='item_1'
    button.triggered.emit.assert_not_called()


def test_ghost_release_while_returning_center_cannot_trigger_ok():
    button,_,_=make_flick(4,0,-45)
    button.mouseMoveEvent(DummyEvent(global_x=100,global_y=100))
    assert button._pending_confirmation.candidate_id == 'item_0'
    assert button._selected_entry.item_id == 'item_0'
    button.mouseReleaseEvent(DummyEvent())
    assert button._pending_confirmation.choice==CANCEL
    button.triggered.emit.assert_not_called()


def test_returning_to_center_before_release_cancels_without_confirmation():
    mod=load_button_module();mod.ShurikenPreview=Preview
    button,launch=make_button(mod)
    launch.shuriken_items.return_value=build(4)
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_y=45))
    assert button._selected_entry is not None
    button.mouseMoveEvent(DummyEvent(global_y=100))
    assert button._selected_entry is None
    button.mouseReleaseEvent(DummyEvent())
    assert button._pending_confirmation is None
    button._preview.hide.assert_called_once_with()
    button.triggered.emit.assert_not_called()


def test_explicit_click_off_button_cancels_even_when_ok_selected():
    button,_,_=make_flick(2,-45,0)
    button.wheelEvent(Wheel(-120))
    click(button,x=80)
    button.triggered.emit.assert_not_called()


def test_existing_dialog_cannot_silently_dismiss_pending_confirmation():
    button,launcher,_=make_flick(4,0,-45)
    pending=button._pending_confirmation
    dialog=NS(remote_command=Mock())
    launcher._remote_confirmation=dialog
    click(button)
    assert button._pending_confirmation is pending
    dialog.remote_command.assert_not_called()
    button.triggered.emit.assert_not_called()
    launcher._remote_confirmation=None
    button.confirm_from_overlay('cancel')
    assert button._pending_confirmation is None


def test_confirmation_model_rejects_implicit_yes():
    confirmation=FirstHandConfirmation('abc','Some title')
    assert confirmation.commit(True) is None
    assert confirmation.wheel(1)==CANCEL
    assert confirmation.commit(True) is None
    assert confirmation.wheel(-1)==OK
    assert confirmation.commit(False) is None
    assert confirmation.commit(True)=='abc'


def test_preview_rejects_confirmation_when_eye_and_candidate_differ():
    mod=load_button_module()
    obj=NS(selected_id='eye_item', confirmation=None, update=Mock())
    wrong=FirstHandConfirmation('different_item','Wrong candidate')
    with pytest.raises(ValueError, match='eye and confirmation'):
        mod.ShurikenPreview.set_confirmation(obj, wrong)
    valid=FirstHandConfirmation('eye_item','Visible eye candidate')
    mod.ShurikenPreview.set_confirmation(obj, valid)
    assert obj.confirmation is valid
    obj.update.assert_called_once()
