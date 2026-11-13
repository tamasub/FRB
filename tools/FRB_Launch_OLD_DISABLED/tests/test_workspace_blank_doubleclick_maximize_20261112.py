"""0279 -> 0280: blank workspace band double-click mimics Windows titlebar.

Pure mouse-event contracts; actual Windows frameless window behaviour still
requires a GUI smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
HELPER = (ROOT / 'src/passive_header_drag.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


class QObject:
    def __init__(self, parent=None):
        pass


QEvent = NS(Type=NS(MouseButtonPress=1, MouseMove=2,
                    MouseButtonRelease=3, MouseButtonDblClick=4))
Qt = NS(MouseButton=NS(LeftButton=1, RightButton=2))


class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def __add__(self, other):
        return Point(self._x + other._x, self._y + other._y)
    def __sub__(self, other):
        return Point(self._x - other._x, self._y - other._y)
    def __eq__(self, other):
        return isinstance(other, Point) and (self._x, self._y) == (other._x, other._y)


class Event:
    def __init__(self, kind, x=0, y=0, button=1, buttons=1):
        self.kind, self.pt, self._button, self._buttons = kind, Point(x, y), button, buttons
        self.accepted = False
    def type(self): return self.kind
    def button(self): return self._button
    def buttons(self): return self._buttons
    def globalPosition(self): return NS(toPoint=lambda: self.pt)
    def accept(self): self.accepted = True


class Widget:
    def __init__(self, name): self.name = name
    def objectName(self): return self.name


class Window:
    def __init__(self, native=False):
        self.xy = Point(100, 200)
        self.native = native
        self.move_calls = 0
        self.system_move_calls = 0
        self.maximized = False
        self.toggle_calls = 0
    def pos(self): return self.xy
    def move(self, point):
        self.xy = point
        self.move_calls += 1
    def windowHandle(self): return self
    def startSystemMove(self):
        self.system_move_calls += 1
        return self.native
    def toggle_maximize_restore(self):
        self.maximized = not self.maximized
        self.toggle_calls += 1


def make_filter(window):
    node = next(c for c in ast.parse(HELPER).body if isinstance(c, ast.ClassDef)
                and c.name == 'PassiveHeaderDrag')
    namespace = {'QObject': QObject, 'QEvent': QEvent, 'Qt': Qt}
    exec(compile(ast.fix_missing_locations(ast.Module([node], type_ignores=[])),
                 '<passive_header_drag>', 'exec'), namespace)
    return namespace['PassiveHeaderDrag'](window)


def test_double_click_on_blank_switches_between_maximized_and_normal():
    window = Window(native=True)
    f = make_filter(window)
    blank = Widget('expandedWorkspaceDragHandle')
    for expected in (True, False):
        # Qt sends the first press/release before MouseButtonDblClick.
        assert f.eventFilter(blank, Event(1, 400, 65))
        assert window.system_move_calls == 0
        assert f.eventFilter(blank, Event(3, 400, 65, buttons=0))
        double = Event(4, 400, 65)
        assert f.eventFilter(blank, double)
        assert double.accepted
        assert window.maximized == expected
        assert window.move_calls == 0
        assert window.system_move_calls == 0
    assert window.toggle_calls == 2


def test_blank_band_drag_still_moves_after_threshold():
    blank = Widget('expandedWorkspaceDragHandle')
    window = Window(native=False)
    f = make_filter(window)
    assert f.eventFilter(blank, Event(1, 20, 30))
    assert f.eventFilter(blank, Event(2, 22, 31))
    assert window.move_calls == 0
    assert f.eventFilter(blank, Event(2, 27, 38))
    assert window.xy == Point(107, 208)
    assert window.system_move_calls == 1
    assert f.eventFilter(blank, Event(3, 27, 38, buttons=0))


def test_blank_band_native_drag_is_started_only_after_mouse_movement():
    blank = Widget('expandedWorkspaceDragHandle')
    window = Window(native=True)
    f = make_filter(window)
    assert f.eventFilter(blank, Event(1, 20, 30))
    assert window.system_move_calls == 0
    assert f.eventFilter(blank, Event(2, 26, 35))
    assert window.system_move_calls == 1
    assert window.move_calls == 0


def test_double_click_on_tab_button_does_not_toggle_window():
    window = Window()
    f = make_filter(window)
    for name in ('expandedWorkspaceTab', 'expandedPageButton', 'mainSearchField'):
        assert not f.eventFilter(Widget(name), Event(4, 40, 50))
    assert window.toggle_calls == 0


def test_normal_header_drag_is_unchanged():
    window = Window(native=True)
    f = make_filter(window)
    assert f.eventFilter(Widget('mainBrand'), Event(1, 20, 30))
    assert window.system_move_calls == 1
    assert window.toggle_calls == 0


def test_wiring_uses_existing_blank_handle_and_existing_maximize_callback():
    assert "self.workspace_drag_handle.setObjectName('expandedWorkspaceDragHandle')" in EXP
    assert 'self.launcher._passive_header_drag)' in EXP
    assert 'def toggle_maximize_restore(self):' in APP
    assert 'self.maximize_button.clicked.connect(self.toggle_maximize_restore)' in APP
