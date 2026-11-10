"""World-standard: answer a Launch-owned confirmation without moving the pointer.

Model-level QApplication event filter regression against real source; actual
Windows/PySide6 GUI capture still needs an on-device acceptance check.
"""
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_list_confirmation_click_gate_20261110 import setup_question, event


def child(mod, question, *, inherits=(), parent=None):
    widget = mod.QWidget()
    widget._window = question
    widget.inherits = lambda name: name in inherits
    widget.parentWidget = lambda: parent if parent is not None else question
    return widget


def test_dialog_message_wheel_then_stationary_press_release_confirm_yes():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    message = child(mod, guard.question)
    types = mod.QEvent.Type
    assert guard.eventFilter(message, event(types.Wheel))
    assert owner.selected == owner.YES
    assert guard.eventFilter(message, event(types.MouseButtonPress, x=150, y=180))
    assert guard.eventFilter(message, event(types.MouseButtonRelease, x=150, y=180))
    buttons[owner.YES].click.assert_called_once_with()
    buttons[owner.NO].click.assert_not_called()


def test_press_on_message_release_on_dialog_with_same_pointer_confirms():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    message = child(mod, guard.question)
    background = child(mod, guard.question)
    types = mod.QEvent.Type
    guard.eventFilter(message, event(types.Wheel))
    # Qt may use a different child as the receiver on Release, despite a
    # stationary hardware cursor; matching the child identity was too strict.
    assert guard.eventFilter(message, event(types.MouseButtonPress, x=101, y=211))
    assert guard.eventFilter(background, event(types.MouseButtonRelease, x=101, y=211))
    buttons[owner.YES].click.assert_called_once_with()


def test_scroll_container_for_long_git_change_list_is_not_text_editor():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    scroll_area = child(mod, guard.question, inherits=('QAbstractScrollArea',))
    text_line = child(mod, guard.question, parent=scroll_area)
    types = mod.QEvent.Type
    guard.eventFilter(text_line, event(types.Wheel))
    assert guard.eventFilter(text_line, event(types.MouseButtonPress, x=8, y=9))
    assert guard.eventFilter(scroll_area, event(types.MouseButtonRelease, x=8, y=9))
    buttons[owner.YES].click.assert_called_once_with()


def test_cross_widget_click_is_not_cross_window_or_drag_permission():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    message = child(mod, guard.question)
    other = child(mod, object())
    background = child(mod, guard.question)
    types = mod.QEvent.Type
    guard.eventFilter(message, event(types.Wheel))
    assert guard.eventFilter(message, event(types.MouseButtonPress, x=50, y=60))
    assert guard.eventFilter(other, event(types.MouseButtonRelease, x=50, y=60))
    assert guard.eventFilter(background, event(types.MouseButtonRelease, x=50, y=60))
    buttons[owner.YES].click.assert_not_called()
    assert guard.eventFilter(message, event(types.MouseButtonPress, x=50, y=60))
    assert guard.eventFilter(background, event(types.MouseButtonRelease, x=50, y=68))
    buttons[owner.YES].click.assert_not_called()


def test_native_buttons_and_editors_never_trigger_additional_click():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    message = child(mod, guard.question)
    button = child(mod, guard.question, inherits=('QAbstractButton',))
    edit = child(mod, guard.question, inherits=('QLineEdit',))
    types = mod.QEvent.Type
    guard.eventFilter(message, event(types.Wheel))
    for native in (button, edit):
        guard.eventFilter(message, event(types.MouseButtonPress))
        for kind in (types.MouseButtonPress, types.MouseButtonRelease):
            e = event(kind)
            assert guard.eventFilter(native, e) is False
            e.accept.assert_not_called()
        guard.eventFilter(message, event(types.MouseButtonRelease))
    buttons[owner.YES].click.assert_not_called()


def test_dialog_not_wheel_armed_or_in_grace_stays_safe():
    mod, guard, owner, buttons, _, _, _, _ = setup_question()
    message = child(mod, guard.question)
    types = mod.QEvent.Type
    for kind in (types.MouseButtonPress, types.MouseButtonRelease):
        guard.eventFilter(message, event(kind))
    buttons[owner.NO].click.assert_not_called()
    guard.eventFilter(message, event(types.Wheel))
    guard._opened_at += 1
    for kind in (types.MouseButtonPress, types.MouseButtonRelease):
        guard.eventFilter(message, event(kind))
    buttons[owner.YES].click.assert_not_called()
