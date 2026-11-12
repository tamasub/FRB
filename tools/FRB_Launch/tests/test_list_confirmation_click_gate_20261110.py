"""Real method contract: explicit ぐりぐり selection + ANY Launch click commits.

The original List wheel forwarding worked, but QApplication's confirmation
filter swallowed both mouse clicks and never delivered CLICK. Tests use the
actual source with small Qt stubs; Windows native widget delivery remains an
on-device acceptance criterion. No filesystem or Git operation is run.
"""
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_remote_confirmation_footer_and_header_20261103 import fake_confirmation_module


def setup_question():
    module, widgets = fake_confirmation_module()
    module.Qt.MouseButton = NS(LeftButton=1, RightButton=2)
    question = object()
    remote = NS()
    pad = widgets.QWidget()
    pad._window = remote
    remote.pad = pad
    launcher = widgets.QWidget()
    launcher._window = launcher
    list_window = launcher
    tree = widgets.QWidget()
    tree._window = list_window
    viewport = widgets.QWidget()
    viewport._window = list_window
    tree.viewport = lambda: viewport
    view = NS(_workspace_mode='files', middle=NS(tree=tree))
    question_ctrl = module.RemoteConfirmation.__new__(module.RemoteConfirmation)
    yes, no = question_ctrl.YES, question_ctrl.NO
    buttons = {name: NS(click=Mock(), setFocus=Mock(), update=Mock(), setStyleSheet=Mock())
               for name in (yes, no)}
    question_ctrl.launcher = launcher
    launcher.remote_window = remote
    launcher.expanded_view = view
    question_ctrl.dialog = NS(button=lambda selected:buttons[selected], setDefaultButton=Mock())
    question_ctrl.selected = no
    question_ctrl._explicit_choice = False
    question_ctrl._background_wheel_angle = 0
    question_ctrl._background_wheel_pixel = 0
    guard = module.ConfirmationInputGuard(question, remote, question_ctrl)
    guard._opened_at -= 1  # A deliberate click after the initial grace window.
    return module, guard, question_ctrl, buttons, pad, viewport, view, remote


def event(t, *, button=1, x=5, y=5, angle=-120):
    class Point:
        def __init__(self, px, py):
            self.x, self.y = px, py
        def __sub__(self, other):
            return NS(manhattanLength=lambda: abs(self.x - other.x) + abs(self.y - other.y))
    loc=Point(x,y)
    return NS(type=lambda:t, button=lambda:button, globalPosition=lambda:NS(toPoint=lambda:loc),
              angleDelta=lambda:NS(y=lambda:angle), pixelDelta=lambda:NS(y=lambda:0), accept=Mock())


def send_click(mod, guard, target, *, button=1, x=5, y=5, end_x=None):
    types=mod.QEvent.Type
    press=event(types.MouseButtonPress,button=button,x=x,y=y)
    release=event(types.MouseButtonRelease,button=button,x=end_x if end_x is not None else x,y=y)
    assert guard.eventFilter(target,press) is True
    assert guard.eventFilter(target,release) is True
    return press,release


def test_wheel_on_files_list_then_click_same_list_commits_selected_yes():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    assert guard.eventFilter(viewport,event(mod.QEvent.Type.Wheel)) is True
    assert owner.selected==owner.YES
    buttons[owner.YES].click.assert_not_called()
    send_click(mod,guard,viewport)
    buttons[owner.YES].click.assert_called_once_with()
    buttons[owner.NO].click.assert_not_called()


def test_explicit_click_on_real_grigri_pad_commits_initial_no_without_wheel():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    send_click(mod,guard,pad)
    buttons[owner.NO].click.assert_called_once_with()
    buttons[owner.YES].click.assert_not_called()


def test_files_list_cannot_confirm_without_explicit_wheel_selection():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    send_click(mod,guard,viewport)
    buttons[owner.NO].click.assert_not_called()
    buttons[owner.YES].click.assert_not_called()


def test_click_before_grace_or_stray_release_cannot_commit():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    guard._opened_at += 1  # Initial click might belong to the opening menu.
    send_click(mod,guard,pad)
    buttons[owner.NO].click.assert_not_called()
    guard._opened_at -= 2
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonRelease)) is True
    buttons[owner.NO].click.assert_not_called()
    send_click(mod,guard,pad)
    buttons[owner.NO].click.assert_called_once_with()


def test_click_drag_outside_dblclick_right_click_are_all_non_confirming():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    send_click(mod,guard,pad,x=5,end_x=30)
    send_click(mod,guard,pad,button=2)
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonPress)) is True
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonDblClick)) is True
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonRelease)) is True
    buttons[owner.NO].click.assert_not_called()


def test_any_launch_surface_is_valid_after_selection_but_external_window_is_not():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    owner.remote_command('DOWN')
    # A browser/list/Exp widget in Launch is still owned by Launch.
    view._workspace_mode='browser'
    send_click(mod,guard,viewport)
    buttons[owner.YES].click.assert_called_once_with()
    external=type(viewport)()
    external._window=object()
    send_click(mod,guard,external)
    buttons[owner.YES].click.assert_called_once_with()


def test_exp_header_and_list_areas_share_the_same_click_semantics():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    owner.remote_command('DOWN')
    exp = type(viewport)()
    exp._window=owner.launcher
    header = type(viewport)()
    header._window=owner.launcher
    send_click(mod,guard,exp)
    send_click(mod,guard,header)
    assert buttons[owner.YES].click.call_count==2


def test_direct_cancel_button_wins_over_wheel_selected_ok():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    owner.remote_command('DOWN')
    actual_cancel=type(viewport)()
    actual_cancel._window=guard.question
    actual_cancel.inherits=lambda name:name=='QAbstractButton'
    press=event(mod.QEvent.Type.MouseButtonPress)
    release=event(mod.QEvent.Type.MouseButtonRelease)
    assert guard.eventFilter(actual_cancel, press) is False
    assert guard.eventFilter(actual_cancel, release) is False
    # Qt sends the native button.clicked -- the guard must not synthesize OK.
    buttons[owner.NO].click()
    buttons[owner.NO].click.assert_called_once_with()
    buttons[owner.YES].click.assert_not_called()


def test_text_dialog_receives_same_guard_click_and_preserves_selected_cancel():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    text=NS(launcher=owner.launcher,remote_has_selected=True,selected='Cancel',remote_command=Mock())
    guard.wheel_receiver=text
    send_click(mod,guard,viewport)
    text.remote_command.assert_called_once_with('CLICK')
    buttons[owner.NO].click.assert_not_called()


def test_click_on_dialog_button_is_native_and_not_intercepted():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    widget=type(pad)()
    widget._window=guard.question
    widget.inherits = lambda name: name == 'QAbstractButton'
    e=event(mod.QEvent.Type.MouseButtonPress)
    assert guard.eventFilter(widget,e) is False
    e.accept.assert_not_called()


def test_long_press_is_not_a_confirmation_click():
    mod,guard,owner,buttons,pad,viewport,view,remote=setup_question()
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonPress)) is True
    # A long hold followed by a spurious release is not intentional approval.
    source,obj,point,pressed_at = guard._click_press
    guard._click_press = (source,obj,point,pressed_at - guard.CLICK_MAX_HOLD_SECONDS - .01)
    assert guard.eventFilter(pad,event(mod.QEvent.Type.MouseButtonRelease)) is True
    buttons[owner.NO].click.assert_not_called()
