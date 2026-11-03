"""Bookmark WAN/hybrid + embedded header alignment, Qt-free regression tests.

Exercises wheel behavior with fake Qt coordinates; Windows PySide6 GUI remains
an explicit manual acceptance step.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1] / 'src'
BOOKMARK = (ROOT / 'browser_bookmark_bar.py').read_text(encoding='utf-8')
EXPANDED = (ROOT / 'expanded_view.py').read_text(encoding='utf-8')
EXP = (ROOT / 'remote_files_explorer.py').read_text(encoding='utf-8')


def extract(source, cls, method, globals_=None):
    module = ast.parse(source)
    c = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name == method)
    scope = globals_ or {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<test-method>', 'exec'), scope)
    return scope[method]


class P:
    def __init__(self, x, y=10): self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def toPoint(self): return self
    def __eq__(self, other): return isinstance(other, P) and (self.x(),self.y()) == (other.x(),other.y())


class Rect:
    def __init__(self, left, right): self.left, self.right = left, right
    def contains(self, p): return self.left <= p.x() < self.right and 0 <= p.y() < 40
    def center(self): return P((self.left + self.right)//2)


class CoordHost:
    def __init__(self, left=0): self.left=left
    def mapToGlobal(self, pos): return P(pos.x()+self.left, pos.y())
    def mapFromGlobal(self, pos): return P(pos.x()-self.left, pos.y())
    def rect(self): return Rect(0, 400)


class Button(CoordHost):
    def __init__(self, left):
        super().__init__(left)
        self.props={}
        self._style=NS(unpolish=lambda b:None,polish=lambda b:None)
    def isVisible(self): return True
    def rect(self): return Rect(0, 40)
    def geometry(self): return Rect(self.left, self.left+40)
    def setProperty(self,k,v): self.props[k]=v
    def style(self): return self._style


class Bar:
    def __init__(self,value=0, maximum=100): self.v=value; self.end=maximum
    def value(self): return self.v
    def minimum(self): return 0
    def maximum(self): return self.end
    def setValue(self,v): self.v=max(0,min(self.end,v))


class Timer:
    def __init__(self): self.stopped=0;self.started=0
    def start(self): self.started+=1
    def stop(self): self.stopped+=1


class Event:
    def __init__(self,angle, x=45, mods=0):
        self.angle=angle; self.x=x;self.mods=mods;self.accepted=False
    def modifiers(self): return self.mods
    def angleDelta(self): return P(0,self.angle)
    def pixelDelta(self): return P(0,0)
    def position(self): return P(self.x)
    def accept(self): self.accepted=True
    def ignore(self): self.accepted=False


class Cursor:
    pos_value = P(45)
    moved = []
    @classmethod
    def pos(cls): return cls.pos_value
    @classmethod
    def setPos(cls, p): cls.moved.append(p);cls.pos_value=p


qt=NS(KeyboardModifier=NS(NoModifier=0), MouseButton=NS(NoButton=0))
application=NS(mouseButtons=lambda:0)
scope={'Qt':qt, 'QApplication':application,'QCursor':Cursor}
wheel=extract(BOOKMARK,'HorizontalBookmarkBar','_scroll_wheel',scope)
lookup=extract(BOOKMARK,'HorizontalBookmarkBar','_button_under_global',scope)
settle=extract(BOOKMARK,'HorizontalBookmarkBar','_settle_wheel_current',scope)
follow=extract(BOOKMARK,'HorizontalBookmarkBar','_follow_wheel_pointer',scope)
select=extract(BOOKMARK,'HorizontalBookmarkBar','_set_wheel_current',scope)


class Demo(CoordHost):
    def __init__(self,scroll=20,end=100):
        super().__init__()
        self.scrollbar=Bar(scroll,end)
        self._buttons=[Button(i*45) for i in range(4)]
        self.bookmark_strip_inner=CoordHost()
        self._viewport=CoordHost()
        self._wheel_current=None
        self._wheel_edge_active=False
        self._wheel_pointer=None
        self._wheel_settle_timer=Timer()
        self.pointer_follow_enabled=lambda:False
        self.opened=[]
    def horizontalScrollBar(self):return self.scrollbar
    def viewport(self):return self._viewport
    def isVisible(self):return True
    _scroll_wheel=wheel
    _button_under_global=lookup
    _settle_wheel_current=settle
    _follow_wheel_pointer=follow
    _set_wheel_current=select
    def _open_bookmark_bar_row(self,row):self.opened.append(row)
    def _open_folder(self,row,button):self.opened.append(row)


def test_scroll_then_settle_highlights_pointer_target_without_opening():
    Cursor.pos_value=P(45)
    Cursor.moved=[]
    d=Demo(scroll=20,end=300)
    evt=Event(-120)
    d._scroll_wheel(evt)
    assert evt.accepted and d.scrollbar.value()==105
    assert d._wheel_current is None  # scroll does not immediately activate
    assert d._wheel_settle_timer.started == 1
    d._settle_wheel_current()
    assert d._wheel_current is d._buttons[1]
    assert d.opened==[] and Cursor.moved==[]


def test_at_edge_wheel_moves_bookmark_current_and_pointer_when_enabled():
    Cursor.pos_value=P(55)
    Cursor.moved=[]
    d=Demo(scroll=100,end=100)
    d.pointer_follow_enabled=lambda:True
    evt=Event(-120,x=55)
    d._scroll_wheel(evt)
    assert d._wheel_current is d._buttons[2]
    assert d._wheel_edge_active
    assert Cursor.moved[-1]==P(110)
    assert not d.opened
    # A second notch goes to the next button using the existing current.
    d._scroll_wheel(Event(-120,x=110))
    assert d._wheel_current is d._buttons[3]
    assert not d.opened
    # Hard stop: never wrap to the first button.
    d._scroll_wheel(Event(-120,x=155))
    assert d._wheel_current is d._buttons[3]


def test_wheel_ignored_with_modifier_without_warp_or_menu():
    Cursor.pos_value=P(45);Cursor.moved=[]
    d=Demo(scroll=100,end=100)
    d._scroll_wheel(Event(-120,mods=1))
    assert d._wheel_current is None and Cursor.moved==[] and d.opened==[]


def test_header_matches_search_height_without_changing_independent_exp():
    align=extract(EXPANDED,'ExpandedLauncherView','_align_embedded_exp_header')
    class Header:
        def __init__(self):self.h=28;self.updated=[]
        def height(self):return self.h
        def minimumHeight(self):return self.h
        def setFixedHeight(self,n):self.updated.append(n);self.h=n
    h=Header()
    search=NS(sizeHint=lambda:NS(height=lambda:37),height=lambda:37,isVisible=lambda:True)
    obj=NS(middle_search_bar=search,embedded_files_exp=NS(exp_header=h))
    align(obj)
    assert h.updated==[37]
    align(obj)
    assert h.updated==[37] # repeated layout event must not trigger a loop
    assert 'self._embedded' in EXP and 'self.exp_header = header' in EXP
    assert "self.middle_search_bar.installEventFilter(self)" in EXPANDED


def test_both_browser_modes_use_one_pointer_preference():
    assert "web.bookmark_strip.pointer_follow_enabled = (" in EXPANDED
    assert "external_bar.pointer_follow_enabled = (" in EXPANDED
    assert "getattr(self.launcher, 'pointer_warp_enabled', True)" in EXPANDED
