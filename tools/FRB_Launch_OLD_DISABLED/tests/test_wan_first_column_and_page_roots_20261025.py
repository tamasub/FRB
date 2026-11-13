"""FRB Launch WAN expansion regression, Qt-free behavioral and source tests.

The actual methods are extracted from production source; fakes provide the Qt
API contract. Native Windows wheel routing still needs a desktop smoke test.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from expanded_view_model import root_wheel_target
from wheel_adaptive import wheel_steps, can_follow_at_edge


def production_method(name, klass='ExpandedLauncherView', file='expanded_view.py'):
    ast_tree = ast.parse((SRC / file).read_text('utf-8'))
    obj = next(c for c in ast_tree.body if isinstance(c, ast.ClassDef) and c.name == klass)
    node = next(f for f in obj.body if isinstance(f, ast.FunctionDef) and f.name == name)
    new = ast.ClassDef(name='Method', bases=[], keywords=[], body=[node], decorator_list=[])
    return compile(ast.fix_missing_locations(ast.Module(body=[new], type_ignores=[])), file, 'exec')


class Point:
    def __init__(self,x,y): self._x,self._y=x,y
    def x(self):return self._x
    def y(self):return self._y
    def __eq__(self,other):return isinstance(other,Point) and (self.x(),self.y())==(other.x(),other.y())
    def __iter__(self):return iter((self._x,self._y))


class Cursor:
    at=Point(20,50)
    moves=[]
    @classmethod
    def pos(cls):return cls.at
    @classmethod
    def setPos(cls,point):cls.at=point;cls.moves.append((point.x(),point.y()))


class Timer:
    queue=[]
    @classmethod
    def singleShot(cls,delay,callback):cls.queue.append(callback)


class App:
    buttons=0
    @classmethod
    def mouseButtons(cls): return cls.buttons


Qt=SimpleNamespace(
    KeyboardModifier=SimpleNamespace(NoModifier=0),
    MouseButton=SimpleNamespace(NoButton=0),
    FocusReason=SimpleNamespace(MouseFocusReason='mouse'))
ns=dict(Qt=Qt,QApplication=App,QCursor=Cursor,QTimer=Timer,QPoint=Point,
        wheel_steps=wheel_steps,can_follow_at_edge=can_follow_at_edge,
        root_wheel_target=root_wheel_target,
        cursor_target=lambda size, rect, x:(x,rect[1]+rect[3]//2))
for name in ('wheel_files_at_edge','sync_first_files_hover_from_cursor','follow_first_files_pointer',
             'schedule_root_pointer_follow','follow_root_pointer'):
    exec(production_method(name),ns)


class Rect:
    def __init__(self,x=0,y=0,width=200,height=120):self.x0,self.y0,self.w,self.h=x,y,width,height
    def contains(self,point):return self.x0<=point.x()<self.x0+self.w and self.y0<=point.y()<self.y0+self.h
    def left(self):return self.x0
    def top(self):return self.y0
    def width(self):return self.w
    def height(self):return self.h
    def right(self):return self.x0+self.w-1
    def bottom(self):return self.y0+self.h-1


class Viewport:
    def rect(self):return Rect()
    def mapFromGlobal(self,p):return p
    def mapToGlobal(self,p):return p
    def width(self):return 200
    def height(self):return 120


class Bar:
    def __init__(self,max_value):self.max_value=max_value
    def minimum(self):return 0
    def maximum(self):return self.max_value


class Tree:
    def __init__(self,max_scroll=0):
        self.items=list(range(6));self.cur=self.items[0];self.hovered=2
        self.bar=Bar(max_scroll);self.focuses=[];self.scrolled=[]
    def topLevelItemCount(self):return len(self.items)
    def currentItem(self):return self.cur
    def topLevelItem(self,n):return self.items[n]
    def indexOfTopLevelItem(self,item):return self.items.index(item) if item in self.items else -1
    def setCurrentItem(self,item):self.cur=item
    def itemAt(self,p):return self.items[self.hovered] if self.hovered is not None else None
    def viewport(self):return Viewport()
    def verticalScrollBar(self):return self.bar
    def scrollToItem(self,item):self.scrolled.append(item)
    def setFocus(self,reason):self.focuses.append(reason)
    def isVisible(self):return True
    def visualItemRect(self,item):return Rect(0,item*20,200,20)


class Demo:
    # Attach the real production methods to a minimal Qt-independent fixture.
    __test__ = False


for name in ('wheel_files_at_edge', 'sync_first_files_hover_from_cursor',
             'follow_first_files_pointer', 'schedule_root_pointer_follow',
             'follow_root_pointer'):
    env = ns.copy()
    exec(production_method(name), env)
    setattr(Demo, name, env['Method'].__dict__[name])


class World(Demo):
    __test__=False
    def __init__(self,max_scroll=0):
        self.left=SimpleNamespace(tree=Tree(max_scroll))
        self._wheel_files_delta=0
        self._files_edge_follow_active=False
        self._files_follow_pending=None
        self._files_follow_scheduled=False
        self._files_scroll_hover_scheduled=False
        self._files_warp_global=None
        self.previews=[]
        self.root_buttons=[]
        self._wheel_root_follow_pending=None
        self._wheel_root_follow_scheduled=False
    def isVisible(self):return True
    def choose_files(self,item,col):self.previews.append(item)


class Event:
    def __init__(self,angle=-120,pixels=0,mods=0):self.angle,self.pixels,self.mods=angle,pixels,mods
    def modifiers(self):return self.mods
    def angleDelta(self):return Point(0,self.angle)
    def pixelDelta(self):return Point(0,self.pixels)


def setup_function():
    Timer.queue=[];Cursor.at=Point(20,50);Cursor.moves=[];App.buttons=0


def run_deferred():
    while Timer.queue:
        Timer.queue.pop(0)()


def test_left_target_flow_scrolls_without_cursor_moving_and_previews_hover():
    w=World(max_scroll=100)
    assert w.wheel_files_at_edge(Event(),10,30) is False
    w.left.tree.hovered=3
    run_deferred()
    assert w.previews==[3]
    assert w.left.tree.currentItem()==3
    assert Cursor.moves==[]


def test_left_no_scrollbar_wheel_follows_and_previews():
    w=World()
    assert w.wheel_files_at_edge(Event(),0,0)
    assert w.previews==[3]
    assert w.left.tree.currentItem()==3
    assert w.left.tree.scrolled==[3]
    run_deferred()
    assert Cursor.moves==[(20,70)]
    assert w._files_warp_global==(20,70)


def test_left_continuous_edge_steps_start_from_current_not_old_hover():
    w=World()
    assert w.wheel_files_at_edge(Event(),0,0)
    assert w.wheel_files_at_edge(Event(),0,0)
    assert w.previews==[3,4]
    run_deferred()
    assert Cursor.moves==[(20,90)]


def test_left_reversed_direction_restores_scroll_mode():
    w=World(max_scroll=100)
    assert w.wheel_files_at_edge(Event(),100,100)
    assert w.previews==[3]
    assert w.wheel_files_at_edge(Event(angle=120),100,80) is False
    assert not w._files_edge_follow_active


def test_left_midrange_zero_change_does_not_jump():
    w=World(max_scroll=100)
    assert w.wheel_files_at_edge(Event(),50,50) is False
    assert w.previews==[]
    assert Cursor.moves==[]


def test_left_modifiers_prevent_follow():
    w=World()
    assert w.wheel_files_at_edge(Event(mods=1),0,0) is False
    App.buttons=1
    assert w.wheel_files_at_edge(Event(),0,0) is False
    assert w.previews==[]


class Button:
    def __init__(self,x=10):self.x=x
    def isVisible(self):return True
    def width(self):return 80
    def height(self):return 30
    def mapToGlobal(self,pt):return Point(self.x+pt.x(),10+pt.y())


class Toolbar:
    def viewport(self):return Viewport()


def test_root_wheel_pointer_follows_button_center_without_click():
    w=World();a,b=Button(10),Button(100)
    w.root_buttons=[a,b]
    w.toolbar_scroller=Toolbar()
    w.schedule_root_pointer_follow(b)
    w.schedule_root_pointer_follow(a)
    assert len(Timer.queue)==1
    run_deferred()
    assert Cursor.moves==[(50,25)]


def test_root_does_not_warp_after_cursor_leaves_strip():
    w=World();btn=Button(100)
    w.root_buttons=[btn];w.toolbar_scroller=Toolbar()
    w.schedule_root_pointer_follow(btn)
    Cursor.at=Point(250,50)
    run_deferred()
    assert Cursor.moves==[]


def test_source_wiring_and_no_auto_execution():
    view=(SRC/'expanded_view.py').read_text('utf-8')
    tabs=(SRC/'page_tab_focus.py').read_text('utf-8')
    assert 'self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge' in view
    assert 'and not self._files_first_wan_enabled' in view
    assert 'self.schedule_root_pointer_follow(button)' in view
    assert 'def wheelEvent(self, event):' in tabs
    assert 'super().wheelEvent(event)' in tabs
    assert 'QTimer.singleShot(0, self.follow_wheel_tab_pointer)' in tabs
    assert 'QCursor.setPos(destination)' in tabs
    assert 'self.choose_files(item, 0)' in view
    # All selection changes have no execute() or activate().
    source=ast.parse(view)
    cls=next(c for c in source.body if isinstance(c,ast.ClassDef) and c.name=='ExpandedLauncherView')
    for method in ('wheel_files_at_edge','sync_first_files_hover_from_cursor','follow_first_files_pointer','follow_root_pointer'):
        func=next(f for f in cls.body if isinstance(f,ast.FunctionDef) and f.name==method)
        code=ast.unparse(func)
        assert 'self.launcher.execute(' not in code
        assert 'self.launcher.activate(' not in code

# Simulate the Qt base class changing the Page on a wheel event. This proves
# the actual FocusPageTabBar override follows only wheel-originated changes.
class FakeQTabBar:
    def __init__(self):self.idx=0;self.visible=True;self.visited=[]
    def currentIndex(self):return self.idx
    def wheelEvent(self,event):
        self.idx=max(0,min(2,self.idx+(1 if event.angle<0 else -1)))
        self.visited.append(self.idx)
    def isVisible(self):return self.visible
    def count(self):return 3
    def mapFromGlobal(self,p):return p
    def mapToGlobal(self,p):return p
    def rect(self):return Rect(0,0,300,40)
    def tabRect(self,i):return Rect(100*i,0,100,40)


def test_page_tab_native_wheel_and_pointer_move_stay_in_sync():
    env=ns.copy()
    code=ast.parse((SRC/'page_tab_focus.py').read_text('utf-8'))
    cls=next(c for c in code.body if isinstance(c,ast.ClassDef) and c.name=='FocusPageTabBar')
    funcs=[f for f in cls.body if isinstance(f,ast.FunctionDef) and
           f.name in ('wheelEvent','follow_wheel_tab_pointer')]
    wrapped=ast.ClassDef(name='WheelTab',bases=[ast.Name(id='FakeQTabBar',ctx=ast.Load())],
                         keywords=[],body=funcs,decorator_list=[])
    env['FakeQTabBar']=FakeQTabBar
    exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapped],type_ignores=[])),
                 'page_tab_focus.py','exec'),env)
    widget=env['WheelTab']()
    Cursor.at=Point(50,20)
    widget.wheelEvent(Event())
    assert widget.idx==1
    run_deferred()
    assert Cursor.moves==[(147,20)]
    # Modifier: native action stays but no cursor motion from WAN enhancement.
    Cursor.moves=[]
    widget.wheelEvent(Event(mods=1))
    run_deferred()
    assert Cursor.moves==[]
