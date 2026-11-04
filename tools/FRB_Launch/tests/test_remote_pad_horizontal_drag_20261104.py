"""Qt-free regression tests for fixed WheelPad left/right drag commands."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
CLASS = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'WheelPad')


def method(name):
    node = next(n for n in CLASS.body if isinstance(n, ast.FunctionDef) and n.name == name)
    qt = NS(MouseButton=NS(LeftButton=1, RightButton=2))
    scope = {'Qt': qt}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'launch_remote.py', 'exec'), scope)
    return scope[name]


PRESS = method('mousePressEvent')
MOVE = method('mouseMoveEvent')
RELEASE = method('mouseReleaseEvent')
DOUBLE = method('mouseDoubleClickEvent')


class Pos:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def x(self):
        return self._x

    def y(self):
        return self._y


class Event:
    def __init__(self, x=30, y=20, button=1):
        self.point = Pos(x, y)
        self._button = button
        self.accept = Mock()

    def button(self):
        return self._button

    def position(self):
        return NS(toPoint=lambda: self.point)


def pad():
    return NS(_pressed=False, _ignore_double_release=False, _drag_start_pos=None,
              _dragged=False, DRAG_THRESHOLD_PX=18,
              rect=lambda: NS(contains=lambda p: 0 <= p.x() < 68 and 0 <= p.y() < 46),
              command=NS(emit=Mock()))


def gesture(end, *, mid=None, start=(30, 20)):
    widget = pad()
    PRESS(widget, Event(*start))
    if mid is not None:
        MOVE(widget, Event(*mid))
    RELEASE(widget, Event(*end))
    return [c.args[0] for c in widget.command.emit.call_args_list], widget


def test_small_motion_is_normal_click():
    assert gesture((42, 25))[0] == ['CLICK']


def test_left_drag_sends_existing_left_command_without_click():
    events, widget = gesture((4, 20), mid=(13, 21))
    assert events == ['LEFT']
    assert widget._pressed is False
    assert widget._drag_start_pos is None


def test_right_drag_sends_existing_right_command_without_click():
    assert gesture((58, 21), mid=(52, 21))[0] == ['RIGHT']


def test_release_outside_pad_still_gestures_without_moving_widget():
    assert gesture((100, 20), mid=(80, 20))[0] == ['RIGHT']
    assert '.move(' not in ast.get_source_segment(SOURCE, next(n for n in CLASS.body if isinstance(n, ast.FunctionDef) and n.name == 'mouseMoveEvent'))


def test_vertical_and_diagonal_drags_do_not_execute_click_or_arrows():
    assert gesture((33, 70), mid=(33, 44))[0] == []
    assert gesture((55, 48), mid=(50, 42))[0] == []


def test_move_out_and_back_does_not_generate_click():
    assert gesture((31, 20), mid=(60, 20))[0] == []


def test_click_and_double_click_remain_distinct():
    widget = pad()
    PRESS(widget, Event())
    RELEASE(widget, Event())
    DOUBLE(widget, Event())
    RELEASE(widget, Event())
    assert [c.args[0] for c in widget.command.emit.call_args_list] == ['CLICK', 'DOUBLE_CLICK']


def test_right_click_still_opens_context_menu():
    widget = pad()
    PRESS(widget, Event(button=2))
    RELEASE(widget, Event(button=2))
    assert [c.args[0] for c in widget.command.emit.call_args_list] == ['CONTEXT_MENU']


def test_only_pad_input_routing_changed():
    assert "self.command.emit('LEFT' if dx < 0 else 'RIGHT')" in SOURCE
    assert 'DRAG_THRESHOLD_PX = 18' in SOURCE
    assert 'self.pad.command.connect(self.command.emit)' in SOURCE
    assert "'LEFT', width=50" in SOURCE
    assert "'RIGHT', width=50" in SOURCE
