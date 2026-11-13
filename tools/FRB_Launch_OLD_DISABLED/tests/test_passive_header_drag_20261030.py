"""Header-only drag: mouse interaction contract without a Qt runtime.

Actual cursor capture and transparent-window rendering require a Windows GUI
smoke test. Keep noninteractive targets separate from editable controls.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
HELPER = (ROOT / 'src/passive_header_drag.py').read_text(encoding='utf-8')
MAIN = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


class QObject:
    def __init__(self, parent=None):
        self.parent = parent


QEvent = SimpleNamespace(Type=SimpleNamespace(MouseButtonPress=1, MouseMove=2,
                                                MouseButtonRelease=3, KeyPress=4))
Qt = SimpleNamespace(MouseButton=SimpleNamespace(LeftButton=1, RightButton=2))


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)


class Event:
    def __init__(self, kind, x=0, y=0, button=1, buttons=1):
        self.kind, self.point, self._button, self._buttons = kind, Point(x, y), button, buttons
        self.accepted = False

    def type(self):
        return self.kind

    def button(self):
        return self._button

    def buttons(self):
        return self._buttons

    def globalPosition(self):
        return SimpleNamespace(toPoint=lambda: self.point)

    def accept(self):
        self.accepted = True


class Window:
    def __init__(self, native=False):
        self.current = Point(100, 200)
        self.native = native
        self.system_move_calls = 0

    def pos(self):
        return self.current

    def move(self, pos):
        self.current = pos

    def windowHandle(self):
        return self

    def startSystemMove(self):
        self.system_move_calls += 1
        return self.native


def drag_filter(window):
    node = next(n for n in ast.parse(HELPER).body if isinstance(n, ast.ClassDef)
                and n.name == 'PassiveHeaderDrag')
    ns = dict(QObject=QObject, QEvent=QEvent, Qt=Qt)
    exec(compile(ast.fix_missing_locations(ast.Module([node], type_ignores=[])),
                 'passive_header_drag.py', 'exec'), ns)
    return ns['PassiveHeaderDrag'](window)


def test_left_drag_moves_window_with_no_native_handle_support():
    window = Window(native=False)
    drag = drag_filter(window)
    assert drag.eventFilter(None, Event(1, 40, 50))
    assert drag.eventFilter(None, Event(2, 70, 90))
    assert window.current == Point(130, 240)
    assert drag.eventFilter(None, Event(3, 70, 90, buttons=0))
    assert not drag.eventFilter(None, Event(2, 150, 170))
    assert window.current == Point(130, 240)


def test_native_system_move_prevents_manual_double_movement():
    window = Window(native=True)
    drag = drag_filter(window)
    assert drag.eventFilter(None, Event(1, 40, 50))
    assert window.system_move_calls == 1
    assert not drag.eventFilter(None, Event(2, 70, 90))
    assert window.current == Point(100, 200)
    assert not drag.eventFilter(None, Event(3, buttons=0))


def test_right_click_and_other_events_are_not_consumed():
    window = Window(native=False)
    drag = drag_filter(window)
    assert not drag.eventFilter(None, Event(1, button=2, buttons=2))
    assert not drag.eventFilter(None, Event(4))
    assert not drag.eventFilter(None, Event(2))
    assert window.system_move_calls == 0


def test_main_header_registers_only_background_and_brand_surfaces():
    assert 'self._passive_header_drag = PassiveHeaderDrag(self)' in MAIN
    registration = MAIN.split('for surface in (', 1)[1].split('):', 1)[0]
    for widget in ('self.search_bar', 'self.brand_widget', 'self.brand_icon_label',
                   'self.brand_title_label', 'self.header_divider'):
        assert widget in registration
    assert 'surface.installEventFilter(self._passive_header_drag)' in MAIN
    section = MAIN.split('self._passive_header_drag = PassiveHeaderDrag(self)', 1)[1]
    section = section.split('self.nav_toolbar = QWidget(self)', 1)[0]
    assert 'self.search.installEventFilter(self._passive_header_drag)' not in section
    assert 'self.theme_button.installEventFilter(self._passive_header_drag)' not in section
    assert 'self.close_button.installEventFilter(self._passive_header_drag)' not in section
    assert 'self.search_bar.setMinimumHeight(50)' in MAIN


def test_remote_draggable_title_but_not_home_close_buttons():
    assert 'title_frame.installEventFilter(self._passive_header_drag)' in REMOTE
    assert 'title.installEventFilter(self._passive_header_drag)' in REMOTE
    assert 'self._button(' in REMOTE
    assert 'WA_TranslucentBackground' in REMOTE
    assert 'drawRoundedRect' in REMOTE
    assert "QColor('#ccd3d7')" in REMOTE
    assert 'QPen(self._remote_outline, 1)' in REMOTE
    assert 'self.setFixedWidth(184)' in REMOTE
    assert 'height=37' in REMOTE
    assert 'FRB Remote v0.12' in REMOTE
