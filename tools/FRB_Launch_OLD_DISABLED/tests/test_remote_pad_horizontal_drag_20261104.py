"""FRB Remote ぐりぐり: 2026-11-06 superseding left/right drag contract.

The retired horizontal drag-to-arrow was dangerous: LEFT while in List could
jump to List row one. The new hold-then-flick ONLY chooses the operating
controller. This is exercised against the real WheelPad method bodies with
small Qt-free timer/preview fakes (no Windows desktop needed).
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from shuriken_model import ShurikenEntry, choose_entry, current_indicator_position

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'launch_remote.py').read_text('utf-8')
TREE = ast.parse(SOURCE)
CLASS = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'WheelPad')


class FakePreview:
    def __init__(self, owner):
        self.owner = owner
        self.shown = False
        self.choices = []
    def present(self, button, entries, choice):
        self.shown = True
        self.choices.append(choice.item_id if choice else None)
    def hide(self):
        self.shown = False


QT = NS(MouseButton=NS(LeftButton=1, RightButton=2))


def method(name):
    node = next(n for n in CLASS.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {'Qt': QT, 'ShurikenPreview': FakePreview, 'choose_entry': choose_entry}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'launch_remote.py', 'exec'), scope)
    return scope[name]


class FakeTimer:
    def __init__(self, on_timeout):
        self.on_timeout = on_timeout
        self.pending = False
        self.delay = None
    def start(self, delay):
        self.delay = delay
        self.pending = True
    def stop(self):
        self.pending = False
    def fire(self):
        if self.pending:
            self.pending = False
            self.on_timeout()


class Pos:
    def __init__(self, x, y):
        self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y


class Event:
    def __init__(self, x=30, y=20, button=1):
        self.point = Pos(x, y)
        self._button = button
        self.accept = Mock()
    def button(self): return self._button
    def position(self): return NS(toPoint=lambda: self.point)


class FakePad:
    DRAG_THRESHOLD_PX = 18
    TARGET_SELECT_DEADZONE_PX = 12
    TARGET_MENU_HOLD_MS = 450

    _target_allowed = method('_target_allowed')
    _show_target_menu = method('_show_target_menu')
    _hide_target_menu = method('_hide_target_menu')
    mousePressEvent = method('mousePressEvent')
    mouseMoveEvent = method('mouseMoveEvent')
    mouseDoubleClickEvent = method('mouseDoubleClickEvent')
    mouseReleaseEvent = method('mouseReleaseEvent')

    def __init__(self, *, allowed=True):
        self._allowed = allowed
        self.target_switch_allowed = lambda: self._allowed
        self._target_menu_open = False
        self._target_preview = None
        self._target_choice = None
        self._target_entries = (
            ShurikenEntry('REMOTE_TARGET_EXP', 'Exp列', 0, 'left', 0),
            ShurikenEntry('REMOTE_TARGET_LIST', 'List列', 0, 'right', 1))
        self._pressed = False
        self._ignore_double_release = False
        self._drag_start_pos = None
        self._dragged = False
        self._target_hold_timer = FakeTimer(self._show_target_menu)
        self.command = NS(emit=Mock())

    def rect(self):
        return NS(contains=lambda p: 0 <= p.x() < 68 and 0 <= p.y() < 46)

    def commands(self):
        return [c.args[0] for c in self.command.emit.call_args_list]


def gesture(end, *, mid=None, start=(30, 20), long_hold=False, allowed=True):
    widget = FakePad(allowed=allowed)
    widget.mousePressEvent(Event(*start))
    if long_hold:
        widget._target_hold_timer.fire()
    if mid is not None:
        widget.mouseMoveEvent(Event(*mid))
    widget.mouseReleaseEvent(Event(*end))
    return widget


def test_short_click_keeps_click_behavior():
    assert gesture((42, 25)).commands() == ['CLICK']


def test_old_left_drag_is_disabled_even_when_pointer_leaves_pad():
    for end in ((4, 20), (-80, 20), (200, 20)):
        widget = gesture(end, mid=(12, 20))
        assert widget.commands() == []
        assert widget._drag_start_pos is None
        assert not widget._target_menu_open


def test_old_right_drag_is_disabled_not_an_arrow_command():
    assert gesture((58, 21), mid=(52, 21)).commands() == []
    assert gesture((100, 20), mid=(80, 20)).commands() == []


def test_moving_before_hold_cancels_menu_and_never_clicks():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget.mouseMoveEvent(Event(55, 20))
    assert not widget._target_hold_timer.pending
    widget._target_hold_timer.fire()
    assert widget._target_preview is None
    widget.mouseReleaseEvent(Event())
    assert widget.commands() == []


def test_long_hold_presents_horizontal_pair_and_center_eye():
    widget = FakePad()
    widget.mousePressEvent(Event())
    assert widget._target_hold_timer.delay == 450
    widget._target_hold_timer.fire()
    assert widget._target_menu_open
    assert widget._target_preview.shown
    assert widget._target_preview.choices == [None]
    assert current_indicator_position(widget._target_entries, '') == (0.0, 0.0)
    widget.mouseMoveEvent(Event(-12, 20))
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_EXP'
    assert current_indicator_position(widget._target_entries, 'REMOTE_TARGET_EXP') == (-42, 0)
    widget.mouseReleaseEvent(Event(-12, 20))
    assert widget.commands() == ['REMOTE_TARGET_EXP']
    assert not widget._target_preview.shown


def test_long_hold_right_switches_to_list_without_navigation():
    widget = gesture((100, 20), mid=(94, 20), long_hold=True)
    assert widget.commands() == ['REMOTE_TARGET_LIST']
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_LIST'


def test_long_hold_release_without_flick_cancels_not_click():
    assert gesture((30, 20), long_hold=True).commands() == []
    assert gesture((43, 20), long_hold=True).commands() == []


def test_diagonal_or_vertical_long_hold_cancels():
    assert gesture((66, 56), long_hold=True).commands() == []
    assert gesture((30, 80), long_hold=True).commands() == []


def test_non_files_context_does_not_open_exp_list_menu():
    widget = gesture((30, 20), long_hold=True, allowed=False)
    assert widget._target_preview is None
    assert widget.commands() == ['CLICK']


def test_disable_target_during_flick_blocks_switch():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseMoveEvent(Event(-40, 20))
    widget._allowed = False  # a dialog appeared mid-gesture
    widget.mouseReleaseEvent(Event(-40, 20))
    assert widget.commands() == []


def test_double_click_stays_distinct_from_single_click():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget.mouseReleaseEvent(Event())
    widget.mouseDoubleClickEvent(Event())
    widget.mouseReleaseEvent(Event())
    assert widget.commands() == ['CLICK', 'DOUBLE_CLICK']


def test_right_click_context_menu_still_available():
    widget = FakePad()
    widget.mousePressEvent(Event(button=2))
    widget.mouseReleaseEvent(Event(button=2))
    assert widget.commands() == ['CONTEXT_MENU']


def test_no_direct_LEFT_RIGHT_legacy_drag_or_pointer_warp():
    release = ast.get_source_segment(SOURCE, next(n for n in CLASS.body
        if isinstance(n, ast.FunctionDef) and n.name == 'mouseReleaseEvent'))
    move = ast.get_source_segment(SOURCE, next(n for n in CLASS.body
        if isinstance(n, ast.FunctionDef) and n.name == 'mouseMoveEvent'))
    assert "self.command.emit('LEFT' if dx < 0 else 'RIGHT')" not in SOURCE
    assert 'self.command.emit(chosen.item_id)' in release
    assert '.move(' not in move
    assert 'self.pad.command.connect(self.command.emit)' in SOURCE
    assert "'LEFT', width=50" in SOURCE and "'RIGHT', width=50" in SOURCE


def test_eye_selected_after_tiny_move_is_committed_on_slow_release():
    """A previously visible eye used to be ignored in the 18..26px gap."""
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseMoveEvent(Event(16, 20))  # 14px left, smaller than old thresholds
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_EXP'
    # No subsequent motion: even a very slow release is the same choice.
    widget.mouseReleaseEvent(Event(16, 20))
    assert widget.commands() == ['REMOTE_TARGET_EXP']


def test_release_uses_visible_eye_without_retesting_release_distance():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseMoveEvent(Event(46, 20))
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_LIST'
    # There was no new mouseMoveEvent, so the eye still displays List.
    widget.mouseReleaseEvent(Event(32, 20))
    assert widget.commands() == ['REMOTE_TARGET_LIST']


def test_eye_return_to_center_cancels_and_sides_can_reverse():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseMoveEvent(Event(6, 20))
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_EXP'
    widget.mouseMoveEvent(Event(52, 20))
    assert widget._target_preview.choices[-1] == 'REMOTE_TARGET_LIST'
    widget.mouseMoveEvent(Event(30, 20))
    assert widget._target_preview.choices[-1] is None
    widget.mouseReleaseEvent(Event(30, 20))
    assert widget.commands() == []


def test_diagonal_cancellation_matches_visible_eye_at_release():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseMoveEvent(Event(48, 70))
    assert widget._target_preview.choices[-1] is None
    widget.mouseReleaseEvent(Event(48, 70))
    assert widget.commands() == []


def test_release_without_move_never_executes_invisible_target():
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget._target_hold_timer.fire()
    widget.mouseReleaseEvent(Event(100, 20))
    assert widget.commands() == []  # Eye stayed at center.


def test_grigri_short_click_and_double_click_still_work_after_hold_fix():
    assert gesture((30, 20)).commands() == ['CLICK']
    widget = FakePad()
    widget.mousePressEvent(Event())
    widget.mouseReleaseEvent(Event())
    widget.mouseDoubleClickEvent(Event())
    widget.mouseReleaseEvent(Event())
    assert widget.commands() == ['CLICK', 'DOUBLE_CLICK']
