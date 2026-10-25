"""WAN Files middle-column tests, executable without PySide6/Windows.

Only no-scroll native events may trigger cursor-follow. All other panes keep
existing dispatch; navigating a file must not open its parent directory.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_view_model import root_wheel_target
from wheel_adaptive import wheel_steps, can_follow_at_edge


def test_real_scroll_never_follows_cursor_and_precision_does_not_warp_midrange():
    assert not can_follow_at_edge(7, 9, 0, 10, 1)
    assert not can_follow_at_edge(7, 7, 0, 10, 1)
    assert not can_follow_at_edge(7, 7, 0, 10, -1)
    assert can_follow_at_edge(10, 10, 0, 10, 1)
    assert can_follow_at_edge(0, 0, 0, 10, -1)


def test_no_scrollbar_all_visible_follow_both_directions():
    assert can_follow_at_edge(0, 0, 0, 0, 1)
    assert can_follow_at_edge(0, 0, 0, 0, -1)


def test_wheel_precision_and_multiple_notches():
    delta = 0
    for _ in range(3):
        delta, steps = wheel_steps(delta, -30)
        assert steps == 0
    delta, steps = wheel_steps(delta, -30)
    assert (delta, steps) == (0, 1)
    assert wheel_steps(0, 240) == (0, -2)
    assert wheel_steps(0, 0, -40) == (0, 1)


def extract_handler(name):
    p = ROOT / 'src/expanded_view.py'
    source = ast.parse(p.read_text(encoding='utf8'))
    view = next(n for n in source.body if isinstance(n, ast.ClassDef)
                and n.name == 'ExpandedLauncherView')
    method = next(n for n in view.body if isinstance(n, ast.FunctionDef) and n.name == name)
    wrapper = ast.ClassDef(name='DemoHandler', bases=[], keywords=[],
                           body=[method], decorator_list=[])
    return compile(ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[])), str(p), 'exec')


class Coord:
    def __init__(self, x, y): self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y


class Mouse:
    current = Coord(20, 20)
    moves = []
    @classmethod
    def pos(cls): return cls.current
    @classmethod
    def setPos(cls, target):
        cls.moves.append((target.x(), target.y()))
        cls.current = target


class Event:
    def __init__(self, degrees=-120, pixels=0, mods=0):
        self.degrees, self.pixels, self.mods = degrees, pixels, mods
    def modifiers(self): return self.mods
    def angleDelta(self): return Coord(0, self.degrees)
    def pixelDelta(self): return Coord(0, self.pixels)


class Bar:
    def __init__(self, minimum=0, maximum=0):
        self.lo, self.hi = minimum, maximum
    def minimum(self): return self.lo
    def maximum(self): return self.hi


class Viewport:
    def rect(self): return self
    def contains(self, pos): return 0 <= pos.x() < 200 and 0 <= pos.y() < 200
    def mapFromGlobal(self, pt): return pt
    def mapToGlobal(self, pt): return pt
    def width(self): return 200
    def height(self): return 200


class Entry:
    def __init__(self, name): self.name = name
    def __repr__(self): return repr(self.name)
    def __eq__(self, other): return self.name == (other.name if isinstance(other, Entry) else other)
    def setSelected(self, selected): self.is_selected = selected


class Tree:
    def __init__(self, size=5, hovered=1, maximum=0):
        self.items = [Entry(f'item-{i}') for i in range(size)]
        self.current = self.items[0] if self.items else None
        self.hovered = hovered
        self.focuses = []
        self.bar = Bar(0, maximum)
        self.selected = []
    def selectedItems(self): return self.selected
    def clearSelection(self):
        for item in self.selected: item.setSelected(False)
        self.selected.clear()
    def state(self): return 'ready'
    def topLevelItemCount(self): return len(self.items)
    def currentItem(self): return self.current
    def itemAt(self, pos): return self.items[self.hovered] if self.items and self.hovered is not None else None
    def indexOfTopLevelItem(self, item): return self.items.index(item) if item in self.items else -1
    def topLevelItem(self, index): return self.items[index]
    def setCurrentItem(self, item): self.current = item
    def setFocus(self, reason): self.focuses.append(reason)
    def verticalScrollBar(self): return self.bar
    def viewport(self): return Viewport()
    def isVisible(self): return True
    def visualItemRect(self, item):
        idx = self.indexOfTopLevelItem(item)
        return SimpleNamespace(left=lambda: 0, top=lambda: idx * 20,
                               width=lambda: 200, height=lambda: 20)


class World:
    calls = []
    buttons = 0
    @classmethod
    def mouseButtons(cls): return cls.buttons


q = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                    MouseButton=SimpleNamespace(NoButton=0),
                    FocusReason=SimpleNamespace(MouseFocusReason='mouse'))
a = SimpleNamespace(State=SimpleNamespace(EditingState='editing'))
qtimer = SimpleNamespace(singleShot=lambda ms, cb: World.calls.append(cb))
namespace = dict(Qt=q, QAbstractItemView=a, QApplication=World,
                 QTimer=qtimer, QCursor=Mouse, QPoint=Coord,
                 wheel_steps=wheel_steps, can_follow_at_edge=can_follow_at_edge,
                 root_wheel_target=root_wheel_target,
                 cursor_target=lambda size, rect, x: (x, rect[1]+rect[3]//2))
exec(extract_handler('wheel_middle_at_edge'), namespace)
Edge = namespace['DemoHandler']
exec(extract_handler('follow_middle_pointer'), namespace)
Follow = namespace['DemoHandler']


class Demo(Edge, Follow):
    __test__ = False
    def __init__(self, size=5, hovered=1, max_scroll=0):
        self.middle = SimpleNamespace(tree=Tree(size, hovered, max_scroll))
        self._wheel_middle_delta = 0
        self._middle_follow_pending = None
        self._middle_follow_scheduled = False
        self._middle_warp_global = None
        self.events = []
    def isVisible(self): return True
    def choose_middle(self, *a): self.events.append('folder-open')
    def activate_row(self, *a): self.events.append('activation')


def setup_function():
    Mouse.current = Coord(20, 20)
    Mouse.moves = []
    World.calls = []
    World.buttons = 0


def test_native_flow_does_not_change_selection_or_cursor():
    demo = Demo(max_scroll=100)
    assert demo.wheel_middle_at_edge(Event(), 10, 30) is False
    assert demo.middle.tree.current == 'item-0'
    assert Mouse.moves == []
    assert World.calls == []


def test_no_scrollbar_uses_hovered_row_and_moves_cursor_after_wheel():
    demo = Demo(hovered=2)
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert demo.middle.tree.current == 'item-3'
    assert demo.middle.tree.current.is_selected
    assert demo.events == []
    assert len(World.calls) == 1
    World.calls.pop()()
    assert Mouse.moves == [(20, 70)]
    assert demo._middle_warp_global == (20, 70)


def test_at_scroll_bottom_follow_and_upward_flow_restored():
    demo = Demo(hovered=3, max_scroll=120)
    assert demo.wheel_middle_at_edge(Event(), 120, 120)
    assert demo.middle.tree.current == 'item-4'
    assert demo.wheel_middle_at_edge(Event(degrees=120), 120, 85) is False
    assert demo._middle_follow_pending is None


def test_do_not_switch_to_follow_on_midrange_zero_delta():
    demo = Demo(hovered=1, max_scroll=120)
    assert demo.wheel_middle_at_edge(Event(), 50, 50) is False
    assert demo.middle.tree.current == 'item-0'


def test_navigation_clamps_and_never_opens_folder():
    demo = Demo(size=5, hovered=4)
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert demo.middle.tree.current == 'item-0'
    assert Mouse.moves == []
    assert not demo.events


def test_modifiers_or_mouse_drag_do_not_warp():
    demo = Demo()
    assert not demo.wheel_middle_at_edge(Event(mods=1), 0, 0)
    World.buttons = 1
    assert not demo.wheel_middle_at_edge(Event(), 0, 0)
    assert not World.calls


def test_real_widget_runs_native_wheel_before_edge_callback_and_only_middle_is_bound():
    text = (ROOT / 'src/expanded_view.py').read_text(encoding='utf8')
    tree = text[text.index('class _SeparatedFileTree'):text.index('class _BreadcrumbSurface')]
    assert tree.index('super().wheelEvent(event)') < tree.index('callback(event, before, scrollbar.value())')
    assert 'self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge' in text
    assert 'self.left.tree.adaptive_wheel_callback = ' not in text
    assert 'self.right.tree.adaptive_wheel_callback = ' not in text
    assert 'self.middle.tree.viewport().installEventFilter(self)' not in text
    assert 'self.choose_middle(item, 0)' not in text[text.index('def wheel_middle_at_edge'):text.index('def follow_middle_pointer')]
    assert 'is_warp_generated_mouse_move((position.x(), position.y()), warp)' in text


def test_precision_wheel_accumulates_at_end_without_premature_cursor_motion():
    demo = Demo(hovered=1)
    for _ in range(3):
        assert demo.wheel_middle_at_edge(Event(degrees=-30), 0, 0)
    assert demo.middle.tree.current == 'item-0'
    assert not World.calls
    assert demo.wheel_middle_at_edge(Event(degrees=-30), 0, 0)
    assert demo.middle.tree.current == 'item-2'
    assert len(World.calls) == 1


def test_existing_multiselection_survives_adaptive_navigation():
    demo = Demo(hovered=2)
    tree = demo.middle.tree
    tree.selected = [tree.items[0], tree.items[1]]
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert tree.current == 'item-3'
    assert tree.selected == [tree.items[0], tree.items[1]]
    assert not demo.events
