"""Compact mode WAN: actual-scroll switching, safe follow, and current fill.

Qt-independent behavioral tests run the production Launcher methods extracted
from source; Windows/PySide6 visual smoke testing is still required.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from menu_wheel import wheel_motion, wheel_neighbor
from wheel_adaptive import can_follow_at_edge
from bookmark_cursor_follow import cursor_target


def extract(filename, cls_name, fn, symbols):
    path = ROOT / 'src' / filename
    module = ast.parse(path.read_text(encoding='utf-8'))
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == fn)
    scope = dict(symbols)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 str(path), 'exec'), scope)
    return scope[fn]


class Point:
    def __init__(self, x, y):
        self._x, self._y = int(x), int(y)
    def x(self):
        return self._x
    def y(self):
        return self._y
    def __eq__(self, other):
        return isinstance(other, Point) and (self._x, self._y) == (other._x, other._y)


class Rect:
    def __init__(self, left, top, width, height):
        self.l, self.t, self.w, self.h = left, top, width, height
    def contains(self, p):
        return self.l <= p.x() < self.l+self.w and self.t <= p.y() < self.t+self.h
    def left(self): return self.l
    def top(self): return self.t
    def width(self): return self.w
    def height(self): return self.h


class Viewport:
    def __init__(self, width=180, height=80):
        self.w, self.h = width, height
    def mapFromGlobal(self, p): return p
    def mapToGlobal(self, p): return p
    def rect(self): return Rect(0, 0, self.w, self.h)
    def width(self): return self.w
    def height(self): return self.h


class Bar:
    def __init__(self, maximum=2): self.mx = maximum
    def minimum(self): return 0
    def maximum(self): return self.mx


class Item:
    def __init__(self, index, kind='command'):
        self.index = index
        self.kind = kind
    def isHidden(self): return False
    def isDisabled(self): return False
    def data(self, *args): return {'item_kind': self.kind}


class Tree:
    def __init__(self, kinds, viewport_height=80, scroll_max=2):
        self.items = [Item(i, kind) for i, kind in enumerate(kinds)]
        self.selected = self.items[0]
        self._viewport = Viewport(height=viewport_height)
        self.scroll_offset = 0
        self.bar = Bar(scroll_max)
        self.visual = False
        self.scroll_to = []
    def isVisible(self): return True
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, i): return self.items[i]
    def currentItem(self): return self.selected
    def setCurrentItem(self, item): self.selected = item
    def scrollToItem(self, item): self.scroll_to.append(item.index)
    def viewport(self): return self._viewport
    def verticalScrollBar(self): return self.bar
    def itemAt(self, pos):
        if not self._viewport.rect().contains(pos): return None
        index = self.scroll_offset + pos.y()//20
        return self.items[index] if 0 <= index < len(self.items) else None
    def set_wheel_current_visual(self, active=True): self.visual = bool(active)
    def visualItemRect(self, item):
        return Rect(0, (item.index-self.scroll_offset)*20, 180, 20)


class Timer:
    def __init__(self): self.stopped=0;self.started=[]
    def stop(self): self.stopped += 1
    def start(self, ms): self.started.append(ms)


class Wheel:
    def __init__(self, angle=-120, modifiers=0):
        self.angle=angle;self.mods=modifiers
    def modifiers(self): return self.mods
    def angleDelta(self): return SimpleNamespace(y=lambda:self.angle)
    def pixelDelta(self): return SimpleNamespace(y=lambda:0)


CURSOR = [Point(55,30)]
QUEUED = []
QT = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
    MouseButton=SimpleNamespace(NoButton=0),
    ItemDataRole=SimpleNamespace(UserRole=42))
APP = SimpleNamespace(mouseButtons=lambda:0)
QCURSOR = SimpleNamespace(pos=lambda:CURSOR[0],setPos=lambda p: CURSOR.__setitem__(0,p))
QTIMER = SimpleNamespace(singleShot=lambda ms, callback: QUEUED.append(callback))
SYMBOLS = dict(Qt=QT, QApplication=APP, QCursor=QCURSOR, QPoint=Point,
               QTimer=QTIMER, wheel_motion=wheel_motion, wheel_neighbor=wheel_neighbor,
               can_follow_at_edge=can_follow_at_edge, cursor_target=cursor_target)


class UI:
    wheel_classic_menu = extract('app.py','Launcher','wheel_classic_menu',SYMBOLS)
    schedule_classic_wheel_pointer_follow = extract('app.py','Launcher','schedule_classic_wheel_pointer_follow',SYMBOLS)
    follow_classic_wheel_pointer = extract('app.py','Launcher','follow_classic_wheel_pointer',SYMBOLS)
    def __init__(self, kinds=None, height=80, mx=2):
        self.view_mode='classic'
        self.list=Tree(kinds or ['command']*6, height,mx)
        self.menu=None
        self.hover_timer=Timer()
        self.pending_menu_item=None
        self.data={'launch_hover_delay_ms':250}
        self.opened=[]
        self.activated=[]
    def cascade(self, row, selected, mode):
        self.opened.append((row['item_kind'], selected.index, mode))
    def activate(self, row):
        self.activated.append(row)


def reset():
    CURSOR[0] = Point(55,30)
    QUEUED.clear()


def test_scroll_flow_keeps_cursor_still_and_fills_real_hovered_current():
    reset()
    ui=UI(['category','command','category','command','category','command'])
    ui.list.scroll_offset=1
    assert ui.wheel_classic_menu(Wheel(), 0, 1)
    assert ui.list.currentItem().index == 2
    assert ui.list.visual
    assert CURSOR[0] == Point(55,30)
    assert not QUEUED
    assert ui.hover_timer.started == [250]
    assert not ui.opened  # A folder is previewed only after hover settles.
    assert not ui.activated


def test_scroll_end_transfers_from_target_flow_to_cursor_follow():
    reset()
    ui=UI()
    ui.list.scroll_offset=2
    assert ui.wheel_classic_menu(Wheel(), 2, 2)
    assert ui.list.currentItem().index == 4  # pointer starts on row 3
    assert ui.list.visual
    assert len(QUEUED)==1
    QUEUED.pop(0)()
    assert CURSOR[0] == Point(55,49)  # row-centre follows Qt pixel geometry
    assert not ui.activated
    assert ui.wheel_classic_menu(Wheel(), 2, 2)
    assert ui.list.currentItem().index == 5
    QUEUED.pop(0)()
    assert CURSOR[0] == Point(55,69)
    assert ui.wheel_classic_menu(Wheel(), 2, 2)
    assert ui.list.currentItem().index == 5
    assert not QUEUED


def test_zero_scroll_range_still_wheel_navigates_short_list():
    reset()
    CURSOR[0]=Point(55,10)
    ui=UI(['command','command','command'], height=80, mx=0)
    assert ui.wheel_classic_menu(Wheel(), 0, 0)
    assert ui.list.currentItem().index==1
    QUEUED.pop(0)()
    assert CURSOR[0]==Point(55,29)


def test_no_warp_when_cursor_moved_after_wheel():
    reset()
    ui=UI()
    ui.list.scroll_offset=2
    ui.wheel_classic_menu(Wheel(), 2, 2)
    CURSOR[0]=Point(60,35)
    QUEUED.pop(0)()
    assert CURSOR[0]==Point(60,35)


def test_no_follow_with_partial_scroll_remaining_away_from_edge():
    reset()
    ui=UI(mx=4)
    assert not ui.wheel_classic_menu(Wheel(), 2, 2)
    assert not QUEUED
    assert ui.list.currentItem().index==0


def test_follow_returns_to_flow_when_scroll_becomes_possible():
    reset()
    ui=UI()
    ui.list.scroll_offset=2
    ui.wheel_classic_menu(Wheel(),2,2)
    QUEUED.pop(0)()
    assert ui._classic_wheel_edge_active
    ui.list.scroll_offset=1
    assert ui.wheel_classic_menu(Wheel(angle=120),2,1)
    assert not ui._classic_wheel_edge_active
    assert ui.list.currentItem().index==3 # cursor y49 -> row2+scroll1


def test_nested_folder_previews_are_not_commands():
    reset()
    ui=UI(['category']*6)
    ui.list.scroll_offset=2
    assert ui.wheel_classic_menu(Wheel(),2,2)
    assert ui.opened==[('category',4,'keyboard')]
    assert not ui.activated


def test_pointer_outside_list_does_not_get_warped():
    reset()
    CURSOR[0]=Point(220,40)
    ui=UI()
    ui.list.scroll_offset=2
    assert not ui.wheel_classic_menu(Wheel(),2,2)
    assert not QUEUED


def test_scrollbar_movement_is_observed_after_native_scroll_not_intercepted():
    app=(ROOT/'src/app.py').read_text(encoding='utf-8')
    tree=(ROOT/'src/reorder_widgets.py').read_text(encoding='utf-8')
    assert 'super().wheelEvent(event)' in tree
    assert 'self.launcher.wheel_classic_menu(event, before, bar.value())' in tree
    assert 'event.accept()' in tree
    assert "not getattr(self.list, 'adaptive_compact_wheel', False)" in app
    assert 'self._wheel_nav_current = False' in tree
    assert 'focused=self.grid_has_focus() or self._wheel_nav_current' in tree
    assert 'self.list.set_wheel_current_visual(False)' in app
