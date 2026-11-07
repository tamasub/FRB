"""SMART rod v0.1 regression: no Qt/Windows required for geometry checks."""
import ast
import math
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_smart_model import smart_vertical_step
from mouse_pointer_rod_model import rod_endpoint


def initial(origin=(80, 176), pointer=(120, 35), length=420):
    radius = math.dist(origin, pointer)
    return rod_endpoint(origin, ((pointer[0]-origin[0])/radius,
                                 (pointer[1]-origin[1])/radius), length)


def assert_collinear(origin, result):
    ax, ay = result.tip[0]-origin[0], result.tip[1]-origin[1]
    bx, by = result.cursor[0]-origin[0], result.cursor[1]-origin[1]
    assert abs(ax*by-ay*bx) < 1e-5
    assert 0 < math.hypot(bx, by) <= result.length + 1e-7


def test_vertical_up_down_and_fast_stay_at_exact_same_x():
    origin, old_cursor = (80, 176), (120, 35)
    old_tip = initial(origin, old_cursor)
    for vertical in [-15, -60, 15, 60]:
        result = smart_vertical_step(origin, old_tip, old_cursor, vertical,
                                     (0, 0, 200, 113), (60, 54, 100, 108))
        assert result is not None
        assert math.isclose(result.tip[0], old_tip[0], abs_tol=1e-8)
        assert math.isclose(result.tip[1], old_tip[1]+vertical, abs_tol=1e-8)
        assert_collinear(origin, result)
        x, y = result.cursor
        assert 3 <= x <= 197 and 3 <= y <= 110
        assert not (57 <= x <= 103 and 51 <= y <= 111)


def test_hitting_top_pad_edge_stops_cleanly_not_jump_to_button():
    origin, cursor = (80, 176), (80, 5)
    tip = initial(origin, cursor, length=600)
    # Cursor can remain on the vertical ray above the centre button.
    result = smart_vertical_step(origin, tip, cursor, -1000,
                                 (0, 0, 200, 113), (60, 54, 100, 108),
                                 max_length=650)
    assert result is not None
    assert result.length <= 650+1e-7
    assert result.tip[1] < tip[1]
    assert result.tip[1] > tip[1] - 1000
    assert_collinear(origin, result)


def test_block_when_no_valid_aiming_ray_or_tip_shorter_than_blue():
    origin = (80, 176)
    # Aiming to the left of blue, with an old pointer unrelated to this ray.
    result = smart_vertical_step(origin, (-200, 20), (20, 20), -30,
                                 (0, 0, 200, 113), (60, 54, 100, 108))
    assert result is None
    # If the rod tip ends below the blue area, the real cursor cannot be
    # both inside blue and between origin and tip. Must not warp out of pad.
    assert smart_vertical_step(origin, (80, 156), (80, 20), 10,
                               (0, 0, 200, 113), (60, 54, 100, 108)) is None


def test_central_pad_exclusion_when_ray_passes_through_grigri():
    origin, old_cursor = (80, 176), (80, 20)
    old_tip = initial(origin, old_cursor)
    res = smart_vertical_step(origin, old_tip, old_cursor, -15,
                              (0, 0, 200, 113), (60, 54, 100, 108))
    assert res is not None
    assert res.cursor[1] < 51  # must be above the wheel, not inside it
    assert_collinear(origin, res)


def test_zero_step_or_no_progress_returns_none():
    tip = initial()
    assert smart_vertical_step((80, 176), tip, (120, 35), 0,
                               (0, 0, 200, 113)) is None
    assert smart_vertical_step((80, 176), tip, (120, 35), -15,
                               (0, 0, 200, 113), max_length=80) is None


def extract_method(path, cls, name, extra_globals=None):
    module = ast.parse((ROOT / 'src' / path).read_text('utf8'))
    klass = next(c for c in module.body if isinstance(c, ast.ClassDef) and c.name == cls)
    method = next(f for f in klass.body if isinstance(f, ast.FunctionDef) and f.name == name)
    namespace = dict(extra_globals or {})
    exec(compile(ast.Module(body=[method], type_ignores=[]), path, 'exec'), namespace)
    return namespace[name]


def test_smart_setting_persists_and_notifies_remote():
    setter = extract_method('app.py', 'Launcher', 'set_mouse_pointer_rod_smart_mode')
    saved = {}
    remote = NS(set_mouse_pointer_rod_smart_mode=Mock())
    obj = NS(mouse_pointer_rod_smart_mode=False,
             settings=NS(setValue=lambda key, value: saved.__setitem__(key,value), sync=Mock()),
             mouse_pointer_rod_smart_action=NS(setChecked=Mock()),
             remote_window=remote, footer=NS(setText=Mock()))
    setter(obj, True)
    assert saved == {'experiment_mouse_pointer_rod_smart': True}
    remote.set_mouse_pointer_rod_smart_mode.assert_called_with(True)
    setter(obj, False)
    assert saved['experiment_mouse_pointer_rod_smart'] is False
    remote.set_mouse_pointer_rod_smart_mode.assert_called_with(False)
    src = (ROOT / 'src' / 'app.py').read_text('utf8')
    assert "'experiment_mouse_pointer_rod_smart', 'false'" in src
    assert '実験：スマート マウス差し棒（上下追従）' in src


def test_smart_cursor_adapter_detects_failed_warp_and_restores():
    from mouse_pointer_rod_smart_cursor import move_smart_cursor
    class Point:
        def __init__(self,x,y): self.x,self.y=x,y
        def __sub__(self,o): return Point(self.x-o.x,self.y-o.y)
        def manhattanLength(self): return abs(self.x)+abs(self.y)
    class Cursor:
        p = Point(10,10)
        @classmethod
        def pos(cls): return cls.p
        @classmethod
        def setPos(cls,p): cls.p=p
    assert move_smart_cursor(Cursor, Point(20,40))
    assert Cursor.p.x == 20
    class Refusing(Cursor):
        @classmethod
        def setPos(cls,p): pass
    assert not move_smart_cursor(Refusing, Point(30,45))


def test_original_mode_does_not_auto_move_physical_cursor():
    src = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf8')
    fn = extract_method('mouse_pointer_rod.py', 'MousePointerRodPad', 'adjust_length',
                        {'length_after_wheel': __import__('mouse_pointer_rod_model').length_after_wheel})
    obj = NS(_enabled=True, _smart_mode=False, _length=420,
             refresh_position=Mock(), _smart_adjust_vertical=Mock())
    fn(obj, 1)
    assert obj._length == 435
    obj._smart_adjust_vertical.assert_not_called()
    obj._smart_mode=True
    fn(obj, 1, fast=True)
    obj._smart_adjust_vertical.assert_called_once_with(1, fast=True)
    assert obj._length == 435


def test_wheel_click_adapter_stays_independent_of_smart_mode():
    app = (ROOT/'src'/'app.py').read_text('utf8')
    pad = (ROOT/'src'/'mouse_pointer_rod.py').read_text('utf8')
    assert 'self._dispatch_windows_click(action, remote, launcher)' in pad
    assert 'self._windows_click_mode = bool(enabled)' in pad
    assert "'experiment_mouse_pointer_rod_windows', 'false'" in app
    assert 'def set_mouse_pointer_rod_smart_mode' in app

class FakePoint:
    def __init__(self,x,y): self._x,self._y=int(x),int(y)
    def x(self): return self._x
    def y(self): return self._y
    def __sub__(self,other): return FakePoint(self._x-other._x,self._y-other._y)
    def manhattanLength(self): return abs(self._x)+abs(self._y)
    def __eq__(self,other): return isinstance(other,FakePoint) and (self._x,self._y)==(other._x,other._y)


class FakeCursor:
    point = FakePoint(120,35)
    accepts_warp = True
    @classmethod
    def pos(cls): return cls.point
    @classmethod
    def setPos(cls,p):
        if cls.accepts_warp: cls.point=p


class FakeRect:
    def __init__(self, left, top, right, bottom):
        self.bounds=(left,top,right,bottom)
    def left(self): return self.bounds[0]
    def top(self): return self.bounds[1]
    def right(self): return self.bounds[2]
    def bottom(self): return self.bounds[3]


def test_production_smart_handler_warps_cursor_and_preserves_tip_x():
    from mouse_pointer_rod_model import NORMAL_WHEEL_STEP_PX,FAST_WHEEL_STEP_PX
    from mouse_pointer_rod_model import rod_endpoint
    FakeCursor.point=FakePoint(120,35)
    FakeCursor.accepts_warp=True
    handler=extract_method('mouse_pointer_rod.py','MousePointerRodPad',
                           '_smart_adjust_vertical',dict(QCursor=FakeCursor,
                           QPoint=FakePoint, rod_endpoint=rod_endpoint,
                           NORMAL_WHEEL_STEP_PX=NORMAL_WHEEL_STEP_PX,
                           FAST_WHEEL_STEP_PX=FAST_WHEEL_STEP_PX))
    base_tip=initial()
    radius=math.dist((80,176),(120,35))
    obj=NS(_enabled=True, _length=420,
           _direction=((120-80)/radius, (35-176)/radius),
           _wheel_pad=NS(geometry=lambda:FakeRect(60,54,100,108)),
           _cursor_on_blue=lambda:True,
           origin_local=lambda:(80,176),
           mapFromGlobal=lambda p:p, mapToGlobal=lambda p:p,
           width=lambda:201, height=lambda:114,
           _in_blue=lambda p:0<=p.x()<201 and 0<=p.y()<114 and not (60<=p.x()<=100 and 54<=p.y()<=108),
           refresh_position=Mock(),_smart_expected_cursor=None)
    handler(obj, 1)
    updated_tip=rod_endpoint((80,176),obj._direction,obj._length)
    assert math.isclose(updated_tip[0],base_tip[0],abs_tol=1e-6)
    assert math.isclose(updated_tip[1],base_tip[1]-15,abs_tol=1e-6)
    assert obj._smart_expected_cursor == FakeCursor.pos()
    assert (FakeCursor.pos().x(),FakeCursor.pos().y()) != (120,35)
    # Integral OS coordinates only allow rounding to the new exact ray.
    cr=FakeCursor.pos()
    ray_error=abs((updated_tip[0]-80)*(cr.y()-176)-(updated_tip[1]-176)*(cr.x()-80))/obj._length
    assert ray_error<=0.8
    handler(obj,-1,fast=True)
    next_tip=rod_endpoint((80,176),obj._direction,obj._length)
    assert math.isclose(next_tip[0],base_tip[0],abs_tol=1e-6)
    assert math.isclose(next_tip[1],base_tip[1]+45,abs_tol=1e-6)
    previous_tip=next_tip
    FakeCursor.accepts_warp=False
    handler(obj,1,fast=True)
    assert rod_endpoint((80,176),obj._direction,obj._length)==previous_tip
    FakeCursor.accepts_warp=True
