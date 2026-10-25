"""Pointer-follow regression without needing Qt/Windows graphical session."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from bookmark_cursor_follow import cursor_target, is_warp_generated_mouse_move


def test_geometry_preserves_horizontal_position_and_centers_vertically():
    assert cursor_target((300, 200), (0, 58, 300, 30), 157) == (157, 72)


def test_geometry_clamps_pointer_into_visible_row_and_viewport():
    assert cursor_target((120, 80), (0, 65, 120, 40), 999) == (107, 72)
    assert cursor_target((120, 80), (0, -15, 120, 30), -100) == (12, 7)


def test_geometry_does_not_warp_to_hidden_or_empty_rows():
    assert cursor_target((100, 50), (0, 52, 100, 30), 40) is None
    assert cursor_target((100, 50), (0, -40, 100, 30), 40) is None
    assert cursor_target((0, 50), (0, 0, 0, 20), 40) is None
    assert cursor_target((100, 50), (100, 0, 20, 20), 40) is None


def test_warp_hover_filter_discriminates_manual_move():
    assert is_warp_generated_mouse_move((42, 71), (42, 70))
    assert not is_warp_generated_mouse_move((50, 71), (42, 70))
    assert not is_warp_generated_mouse_move((42, 71), None)


def _method(name, custom_env=None):
    code = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    module = ast.parse(code)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'ExpandedLauncherView')
    func = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(custom_env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])), '<real expanded_view>', 'exec'), ns)
    return ns[name]


class Point:
    def __init__(self, x, y): self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def __eq__(self, other): return isinstance(other, Point) and (self._x, self._y) == (other._x, other._y)


class Rect:
    def __init__(self, x, y, w, h): self.x0, self.y0, self.w, self.h = x, y, w, h
    def left(self): return self.x0
    def top(self): return self.y0
    def width(self): return self.w
    def height(self): return self.h
    def contains(self, p): return 0 <= p.x() < self.w and 0 <= p.y() < self.h


class Viewport:
    def __init__(self): self.w, self.h = 240, 160
    def mapFromGlobal(self, p): return Point(p.x()-100, p.y()-200)
    def mapToGlobal(self, p): return Point(p.x()+100, p.y()+200)
    def rect(self): return Rect(0, 0, self.w, self.h)
    def width(self): return self.w
    def height(self): return self.h


class Tree:
    def __init__(self, row): self.row, self.viewport_obj = row, Viewport()
    def isVisible(self): return True
    def currentItem(self): return self.row
    def viewport(self): return self.viewport_obj
    def visualItemRect(self, item): return Rect(0, 70, 240, 33)


class Cursor:
    position = Point(160, 218)
    changes = []
    @classmethod
    def pos(cls): return cls.position
    @classmethod
    def setPos(cls, p):
        cls.position = p
        cls.changes.append(p)


class FakeTimer:
    pending = []
    @classmethod
    def singleShot(cls, millis, fn): cls.pending.append(fn)


def _mock_view():
    Cursor.position = Point(160, 218)
    Cursor.changes = []
    FakeTimer.pending = []
    tree = Tree(object())
    view = SimpleNamespace(
        _bookmark_follow_scheduled=False,
        _bookmark_follow_pending=None,
        _bookmark_warp_global=None,
        launcher=SimpleNamespace(bookmark_pointer_follow=True),
        right=SimpleNamespace(tree=tree),
        isVisible=lambda: True)
    env = dict(QTimer=FakeTimer, QCursor=Cursor, QPoint=Point,
               QApplication=SimpleNamespace(mouseButtons=lambda: 0),
               Qt=SimpleNamespace(MouseButton=SimpleNamespace(NoButton=0)),
               cursor_target=cursor_target)
    view.follow_bookmark_pointer = lambda: _method('follow_bookmark_pointer', env)(view)
    view.schedule_bookmark_pointer_follow = lambda item: _method('schedule_bookmark_pointer_follow', env)(view, item)
    return view, tree


def test_wheel_warp_moves_only_y_and_coalesces_rapid_selection():
    view, tree = _mock_view()
    view.schedule_bookmark_pointer_follow(tree.row)
    view.schedule_bookmark_pointer_follow(tree.row)
    assert len(FakeTimer.pending) == 1
    FakeTimer.pending.pop()()
    assert Cursor.position == Point(160, 286)  # row midpoint, same x as before
    assert view._bookmark_warp_global == (160, 286)
    assert not view._bookmark_follow_scheduled


def test_no_warp_if_disabled_or_mouse_left_pane_or_no_longer_selected():
    view, tree = _mock_view()
    view.launcher.bookmark_pointer_follow = False
    view.schedule_bookmark_pointer_follow(tree.row)
    FakeTimer.pending.pop()()
    assert not Cursor.changes

    view, tree = _mock_view()
    Cursor.position = Point(50, 205)  # outside bookmark viewport at x < 100
    view.schedule_bookmark_pointer_follow(tree.row)
    FakeTimer.pending.pop()()
    assert not Cursor.changes

    view, tree = _mock_view()
    view.schedule_bookmark_pointer_follow(tree.row)
    tree.row = object()
    FakeTimer.pending.pop()()
    assert not Cursor.changes


def test_no_warp_when_row_is_not_visible_even_after_scroll():
    view, tree = _mock_view()
    tree.visualItemRect = lambda item: Rect(0, 500, 240, 30)
    view.schedule_bookmark_pointer_follow(tree.row)
    FakeTimer.pending.pop()()
    assert not Cursor.changes


def test_settings_menu_and_initialization_safety_are_wired():
    app = (SRC / 'app.py').read_text(encoding='utf-8')
    view = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'self.bookmark_pointer_follow_action.setCheckable(True)' in app
    assert "self.settings.setValue('bookmark_pointer_follow', self.bookmark_pointer_follow)" in app
    assert 'self.bookmark_pointer_follow_action.triggered.connect(self.set_bookmark_pointer_follow)' in app
    assert "if getattr(self.launcher, 'bookmark_pointer_follow', False):" in view
    assert "getattr(self, 'right', None) is not None" in view  # before right constructed
    assert 'self.schedule_bookmark_pointer_follow(item)' in view
    assert 'self._bookmark_warp_global = None' in view


def test_gear_switch_persists_setting_and_cancels_pending_warp():
    code = (SRC / 'app.py').read_text(encoding='utf-8')
    module = ast.parse(code)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'set_bookmark_pointer_follow')
    env = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), '<actual Launcher>', 'exec'), env)
    class Settings:
        def __init__(self): self.values = {}; self.synced = False
        def setValue(self, k, v): self.values[k] = v
        def sync(self): self.synced = True
    status = SimpleNamespace(canceled=False)
    status.cancel_bookmark_pointer_follow = lambda: setattr(status, 'canceled', True)
    obj = SimpleNamespace(settings=Settings(), expanded_view=status, bookmark_pointer_follow=True)
    env['set_bookmark_pointer_follow'](obj, False)
    assert obj.bookmark_pointer_follow is False
    assert obj.settings.values['bookmark_pointer_follow'] is False
    assert obj.settings.synced and status.canceled
