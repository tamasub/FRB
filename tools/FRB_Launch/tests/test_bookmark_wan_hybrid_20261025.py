"""Bookmark WAN native-scroll/edge-follow/hover regression (Qt-free)."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from expanded_view_model import root_wheel_target
from wheel_adaptive import wheel_steps, can_follow_at_edge


def method(name, cls='ExpandedLauncherView', filename='expanded_view.py'):
    code = ast.parse((SRC / filename).read_text(encoding='utf-8'))
    klass = next(n for n in code.body if isinstance(n, ast.ClassDef) and n.name == cls)
    func = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])),
                   filename, 'exec')


class P:
    def __init__(self, x, y): self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y


class Cursor:
    loc = P(20, 50)
    @classmethod
    def pos(cls): return cls.loc


class Timer:
    future = []
    @classmethod
    def singleShot(cls, n, cb): cls.future.append(cb)


class HoverTimer:
    def __init__(self): self.started = []; self.stopped = 0; self.active = False
    def start(self, delay): self.started.append(delay); self.active = True
    def stop(self): self.stopped += 1; self.active = False
    def isActive(self): return self.active


class Bar:
    def __init__(self, maximum): self.max = maximum
    def minimum(self): return 0
    def maximum(self): return self.max


class Viewport:
    def rect(self): return self
    def contains(self, pos): return 0 <= pos.x() < 200 and 0 <= pos.y() < 150
    def mapFromGlobal(self, pos): return pos


class Tree:
    def __init__(self, maxscroll=0):
        self.rows = [{'item_kind': x} for x in ['category', 'command', 'category', 'command', 'directory']]
        self.cur = self.rows[0]
        self.bar = Bar(maxscroll)
        self.hovered = 1
        self.focus_count = 0
        self.adaptive_wheel_callback = None
    def topLevelItemCount(self): return len(self.rows)
    def topLevelItem(self, n): return self.rows[n]
    def currentItem(self): return self.cur
    def indexOfTopLevelItem(self, item):
        return next((i for i, row in enumerate(self.rows) if row is item), -1)
    def setCurrentItem(self, item): self.cur = item
    def itemAt(self, pos): return self.rows[self.hovered] if self.hovered is not None else None
    def verticalScrollBar(self): return self.bar
    def viewport(self): return Viewport()
    def setFocus(self, reason): self.focus_count += 1


class World:
    pressed = 0
    @classmethod
    def mouseButtons(cls): return cls.pressed


class Event:
    def __init__(self, angle=-120, pixels=0, mods=0):
        self.angle, self.pixels, self.mods = angle, pixels, mods
    def angleDelta(self): return P(0, self.angle)
    def pixelDelta(self): return P(0, self.pixels)
    def modifiers(self): return self.mods


qt = SimpleNamespace(
    MouseButton=SimpleNamespace(NoButton=0),
    KeyboardModifier=SimpleNamespace(NoModifier=0),
    FocusReason=SimpleNamespace(MouseFocusReason=0))
env = dict(Qt=qt, QApplication=World, QCursor=Cursor, QTimer=Timer,
           wheel_steps=wheel_steps, can_follow_at_edge=can_follow_at_edge,
           root_wheel_target=root_wheel_target)
for name in ('wheel_bookmarks_at_edge', 'sync_bookmark_hover_from_cursor',
             'request_bookmark_hover', 'open_bookmark_hover',
             'hover_bookmark_first_level', 'cancel_bookmark_hover', 'set_bookmark_wan'):
    exec(method(name), env)


class Demo:
    __test__ = False
    def __init__(self, maxscroll=0):
        self.right = SimpleNamespace(tree=Tree(maxscroll))
        self.launcher = SimpleNamespace(bookmark_wan_enabled=True, bookmark_pointer_follow=True,
                                        menu=None, close_cascade_for_main_interaction=self.close_cascade)
        self._wheel_bookmark_delta = 0
        self._bookmark_edge_follow_active = False
        self._bookmark_follow_pending = None
        self._bookmark_scroll_hover_scheduled = False
        self._bookmark_hover_item = None
        self._bookmark_hover_timer = HoverTimer()
        self.followed = []
        self.expanded = []
        self.closed = 0
    def isVisible(self): return True
    def schedule_bookmark_pointer_follow(self, item):
        self._bookmark_follow_pending = item
        self.followed.append(item)
    def cancel_bookmark_pointer_follow(self): self._bookmark_follow_pending = None
    def row_data(self, item): return item
    def choose_bookmark(self, item, col): self.expanded.append(item)
    def close_cascade(self): self.closed += 1

for name in ('wheel_bookmarks_at_edge', 'sync_bookmark_hover_from_cursor',
             'request_bookmark_hover', 'open_bookmark_hover',
             'hover_bookmark_first_level', 'cancel_bookmark_hover', 'set_bookmark_wan'):
    setattr(Demo, name, env[name])


def setup_function():
    Timer.future = []
    Cursor.loc = P(20, 50)
    World.pressed = 0


def test_normal_scroll_preserves_pointer_and_uses_hover_after_scrolling():
    demo = Demo(100)
    tree = demo.right.tree
    assert demo.wheel_bookmarks_at_edge(Event(), 10, 40) is False
    assert not demo.followed
    assert len(Timer.future) == 1
    tree.hovered = 2
    Timer.future.pop()()
    assert tree.currentItem() is tree.rows[2]
    assert demo._bookmark_hover_timer.started == [230]
    assert demo.expanded == []
    demo.open_bookmark_hover()
    assert demo.expanded == [tree.rows[2]]


def test_no_scrollbar_selects_and_follows_but_doesnt_expand_until_hover_settles():
    demo = Demo()
    assert demo.wheel_bookmarks_at_edge(Event(), 0, 0)
    tree = demo.right.tree
    assert tree.currentItem() is tree.rows[2]
    assert demo.followed == [tree.rows[2]]
    assert not demo.expanded
    tree.hovered = 2
    demo.open_bookmark_hover()
    assert demo.expanded == [tree.rows[2]]


def test_end_of_scroll_then_reverse_restores_native_flow():
    demo = Demo(120)
    assert demo.wheel_bookmarks_at_edge(Event(), 120, 120)
    assert len(demo.followed) == 1
    assert not demo.wheel_bookmarks_at_edge(Event(angle=120), 120, 95)
    assert demo._bookmark_follow_pending is None


def test_zero_mid_scroll_is_not_cursor_follow():
    demo = Demo(120)
    assert not demo.wheel_bookmarks_at_edge(Event(), 50, 50)
    assert not demo.followed


def test_hovering_url_never_opens_it_and_dismisses_stale_folder():
    demo = Demo()
    item = demo.right.tree.rows[1]
    demo.hover_bookmark_first_level(item, 0)
    assert demo.right.tree.currentItem() is item
    assert not demo.expanded
    demo.open_bookmark_hover()
    assert demo.closed == 1
    assert not demo.expanded


def test_hover_must_still_match_pointer_after_scroll():
    demo = Demo()
    item = demo.right.tree.rows[2]
    demo.request_bookmark_hover(item)
    demo.right.tree.hovered = 3
    demo.open_bookmark_hover()
    assert not demo.expanded


def test_mouse_drag_and_modifiers_do_not_move_pointer():
    demo = Demo()
    assert not demo.wheel_bookmarks_at_edge(Event(mods=1), 0, 0)
    World.pressed = 1
    assert not demo.wheel_bookmarks_at_edge(Event(), 0, 0)
    assert not demo.followed


def test_wan_toggle_preserves_the_old_first_level_follow_handler():
    demo = Demo()
    demo.set_bookmark_wan(True)
    assert demo.right.tree.adaptive_wheel_callback == demo.wheel_bookmarks_at_edge
    demo.set_bookmark_wan(False)
    assert demo.right.tree.adaptive_wheel_callback is None
    view = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'and not getattr(self.launcher, \'bookmark_wan_enabled\', True)' in view
    assert 'self.wheel_bookmarks_first_level(event)' in view


def test_gear_setting_persists_ab_toggle():
    saved = {}
    obj = SimpleNamespace(bookmark_wan_enabled=False,
        settings=SimpleNamespace(setValue=lambda k, v: saved.update({k: v}), sync=lambda: saved.update({'sync': True})),
        expanded_view=SimpleNamespace(set_bookmark_wan=lambda state: saved.update({'view': state})))
    method_env = {}
    exec(method('set_bookmark_wan_enabled', cls='Launcher', filename='app.py'), method_env)
    method_env['set_bookmark_wan_enabled'](obj, True)
    assert saved == {'bookmark_wan_enabled': True, 'sync': True, 'view': True}
    code = (SRC / 'app.py').read_text(encoding='utf-8')
    assert 'self.bookmark_wan_action.triggered.connect(self.set_bookmark_wan_enabled)' in code


def test_scope_only_bookmark_and_native_before_fallback():
    view = (SRC / 'expanded_view.py').read_text(encoding='utf-8')
    code = view[view.index('class _SeparatedFileTree'):view.index('class _BreadcrumbSurface')]
    assert code.index('super().wheelEvent(event)') < code.index('callback(event, before, scrollbar.value())')
    assert 'self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge' in view
    assert 'self.right.tree.itemEntered.connect(self.hover_bookmark_first_level)' in view
    # Files first column adopts WAN in the next experience experiment.
    assert 'self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge' in view
    assert 'self.right.tree.verticalScrollBar().installEventFilter(self)' not in view


def test_follow_off_still_advances_with_repeated_wheel_steps():
    demo = Demo()
    demo.launcher.bookmark_pointer_follow = False
    tree = demo.right.tree
    assert demo.wheel_bookmarks_at_edge(Event(), 0, 0)
    assert tree.currentItem() is tree.rows[2]
    assert demo.wheel_bookmarks_at_edge(Event(), 0, 0)
    assert tree.currentItem() is tree.rows[3]
    assert not demo.followed
