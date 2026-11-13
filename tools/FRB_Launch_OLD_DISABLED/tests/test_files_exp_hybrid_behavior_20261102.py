"""Behavioral, Qt-free test of the production Files Exp wheel methods.

Load the real FilesExpWheelTree AST under lightweight widget doubles so
we can verify scroll-before-follow without requiring a Windows GUI session.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from bookmark_cursor_follow import cursor_target
from wheel_adaptive import wheel_steps, can_follow_at_edge


class Point:
    def __init__(self, x=0, y=0): self.a, self.b = x, y
    def x(self): return self.a
    def y(self): return self.b
    def __eq__(self, other): return isinstance(other, Point) and (self.a, self.b) == (other.a, other.b)


class Rect:
    def __init__(self, x, y, w, h): self.x, self.y, self.w, self.h = x, y, w, h
    def contains(self, p): return self.x <= p.x() < self.x + self.w and self.y <= p.y() < self.y + self.h
    def left(self): return self.x
    def top(self): return self.y
    def width(self): return self.w
    def height(self): return self.h


class Cursor:
    point = Point(40, 35)
    moved = []
    @classmethod
    def pos(cls): return cls.point
    @classmethod
    def setPos(cls, p): cls.point = p; cls.moved.append(p)


class Timer:
    pending = []
    @classmethod
    def singleShot(cls, delay, callback): cls.pending.append(callback)


class Bar:
    def __init__(self): self.n = 0
    def value(self): return self.n
    def minimum(self): return 0
    def maximum(self): return 2


class Index:
    def __init__(self, row): self.row = row
    def isValid(self): return self.row >= 0
    def __eq__(self, other): return isinstance(other, Index) and self.row == other.row


class Viewport:
    def rect(self): return Rect(0, 0, 160, 120)
    def mapFromGlobal(self, p): return p
    def mapToGlobal(self, p): return p
    def width(self): return 160
    def height(self): return 120


class FakeTreeBase:
    def __init__(self, parent=None):
        self.bar = Bar()
        self.selected = Index(0)
        self.viewport_obj = Viewport()
        self.scroll_requested = 0
    def verticalScrollBar(self): return self.bar
    def viewport(self): return self.viewport_obj
    def wheelEvent(self, event):
        self.scroll_requested += 1
        direction = -1 if event.angleDelta().y() > 0 else 1
        self.bar.n = max(0, min(2, self.bar.n + direction))
    def currentIndex(self): return self.selected
    def setCurrentIndex(self, item): self.selected = item
    def indexAt(self, pos): return Index(self.bar.value())
    def indexBelow(self, idx): return Index(idx.row + 1 if idx.row < 4 else -1)
    def indexAbove(self, idx): return Index(idx.row - 1 if idx.row > 0 else -1)
    def scrollTo(self, *args): pass
    def isVisible(self): return True
    def visualRect(self, idx): return Rect(0, idx.row * 20, 150, 20)
    def model(self): return NS(index=lambda row, col: Index(row))


class Event:
    def angleDelta(self): return Point(0, -120)
    def pixelDelta(self): return Point()
    def modifiers(self): return 0


qt = NS(KeyboardModifier=NS(NoModifier=0), MouseButton=NS(NoButton=0))
view = NS(ScrollHint=NS(EnsureVisible=0))
app = NS(mouseButtons=lambda: 0)
module = ast.parse((SRC / 'remote_files_explorer.py').read_text('utf-8'))
source = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'FilesExpWheelTree')
source.bases = [ast.Name(id='FakeTreeBase', ctx=ast.Load())]
ns = dict(FakeTreeBase=FakeTreeBase, Qt=qt, QApplication=app,
          QCursor=Cursor, QTimer=Timer, QPoint=Point, QAbstractItemView=view,
          cursor_target=cursor_target, wheel_steps=wheel_steps, can_follow_at_edge=can_follow_at_edge)
exec(compile(ast.fix_missing_locations(ast.Module(body=[source], type_ignores=[])),
             'production_tree.py', 'exec'), ns)
FilesExpWheelTree = ns['FilesExpWheelTree']


def test_native_scroll_first_then_select_under_stationary_pointer():
    Cursor.point, Cursor.moved, Timer.pending = Point(40, 35), [], []
    tree = FilesExpWheelTree()
    tree.wheelEvent(Event())
    assert tree.scroll_requested == 1
    assert tree.bar.value() == 1
    assert tree.currentIndex() == Index(0)  # delayed to coalesce events
    assert Cursor.moved == []
    for callback in Timer.pending[:]: callback()
    assert tree.currentIndex() == Index(1)
    assert Cursor.moved == []  # normal scroll MUST NOT warp pointer


def test_at_real_end_follow_current_and_pointer_when_enabled():
    Cursor.point, Cursor.moved, Timer.pending = Point(40, 35), [], []
    tree = FilesExpWheelTree()
    tree.bar.n = 2
    tree.selected = Index(2)
    tree.wheelEvent(Event())
    assert tree.scroll_requested == 1
    assert tree.bar.value() == 2
    assert tree.currentIndex() == Index(3)  # edge-only current navigation
    for callback in Timer.pending[:]: callback()
    assert Cursor.moved and Cursor.moved[-1] == Point(40, 69)


def test_vdi_disables_cursor_warp_but_not_edge_navigation():
    Cursor.point, Cursor.moved, Timer.pending = Point(40, 35), [], []
    tree = FilesExpWheelTree()
    tree.pointer_follow_enabled = lambda: False
    tree.bar.n = 2
    tree.selected = Index(2)
    tree.wheelEvent(Event())
    assert tree.currentIndex() == Index(3)
    assert Cursor.moved == []
