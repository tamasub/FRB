"""Regression: Git Yes/No covers Files List and the non-activating Remote.

The QMessageBox surface itself must be an input route, not just the Files List
underneath it. These are model-level Qt stubs; no claim of Windows GUI testing.
"""
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_list_confirmation_click_gate_20261110 import (
    setup_question, event, send_click,
)


def dialog_surface():
    mod, guard, owner, buttons, pad, viewport, view, remote = setup_question()
    widget = mod.QWidget()
    widget._window = guard.question
    return mod, guard, owner, buttons, widget, pad, viewport


def test_dialog_wheel_selects_yes_and_click_on_same_surface_confirms():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    assert guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=-120))
    assert owner.selected == owner.YES
    assert owner._explicit_choice
    buttons[owner.YES].click.assert_not_called()
    send_click(mod, guard, widget)
    buttons[owner.YES].click.assert_called_once_with()
    buttons[owner.NO].click.assert_not_called()


def test_dialog_wheel_reverse_selects_no_and_click_confirms_no():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    assert guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=-120))
    assert guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=120))
    assert owner.selected == owner.NO
    send_click(mod, guard, widget)
    buttons[owner.NO].click.assert_called_once_with()
    buttons[owner.YES].click.assert_not_called()


def test_dialog_surface_does_not_confirm_by_unarmed_background_click():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    send_click(mod, guard, widget)
    buttons[owner.NO].click.assert_not_called()
    buttons[owner.YES].click.assert_not_called()


def test_wheel_during_pressed_dialog_resets_armed_click():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    assert guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonPress))
    assert guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=-120))
    assert guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonRelease))
    buttons[owner.YES].click.assert_not_called()
    send_click(mod, guard, widget)
    buttons[owner.YES].click.assert_called_once_with()


def test_dialog_double_click_right_button_drag_and_stray_release_are_safe():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=-120))
    send_click(mod, guard, widget, button=2)
    send_click(mod, guard, widget, x=5, end_x=40)
    guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonRelease))
    guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonPress))
    guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonDblClick))
    guard.eventFilter(widget, event(mod.QEvent.Type.MouseButtonRelease))
    buttons[owner.YES].click.assert_not_called()


def test_dialog_surface_click_before_opening_grace_is_ignored_even_after_wheel():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    guard.eventFilter(widget, event(mod.QEvent.Type.Wheel, angle=-120))
    guard._opened_at += 1
    send_click(mod, guard, widget)
    buttons[owner.YES].click.assert_not_called()


def test_native_dialog_buttons_still_receive_normal_mouse_events():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    widget.inherits = lambda name: name == 'QAbstractButton'
    for kind in (mod.QEvent.Type.MouseButtonPress,
                 mod.QEvent.Type.MouseButtonRelease):
        ev = event(kind)
        assert guard.eventFilter(widget, ev) is False
        ev.accept.assert_not_called()


def test_text_editing_remains_native_even_after_dialog_wheel():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    editor = mod.QWidget()
    editor._window = guard.question
    editor.inherits = lambda name: name == 'QLineEdit'
    text = NS(remote_has_selected=False, selected='Cancel',
              background_wheel=Mock(), remote_command=Mock())
    guard.wheel_receiver = text
    ev = event(mod.QEvent.Type.Wheel)
    assert guard.eventFilter(widget, ev)
    text.background_wheel.assert_called_once_with(ev)
    for kind in (mod.QEvent.Type.MouseButtonPress,
                 mod.QEvent.Type.MouseButtonRelease):
        e = event(kind)
        assert guard.eventFilter(editor, e) is False
        e.accept.assert_not_called()
    text.remote_command.assert_not_called()


def test_remote_pad_and_original_files_list_routes_still_work():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    guard.eventFilter(viewport, event(mod.QEvent.Type.Wheel, angle=-120))
    assert owner.selected == owner.YES
    send_click(mod, guard, pad)
    buttons[owner.YES].click.assert_called_once_with()


def test_dialog_no_keyboard_or_background_action_leak():
    mod, guard, owner, buttons, widget, pad, viewport = dialog_surface()
    other = mod.QWidget()
    other._window = object()
    for kind in (mod.QEvent.Type.KeyPress, mod.QEvent.Type.ShortcutOverride,
                 mod.QEvent.Type.MouseButtonPress):
        ev = event(kind)
        assert guard.eventFilter(other, ev)
        ev.accept.assert_called_once()
