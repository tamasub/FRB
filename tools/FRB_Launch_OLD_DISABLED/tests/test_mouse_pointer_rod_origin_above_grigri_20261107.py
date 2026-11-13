"""Smart Rod pivot relocation: static contracts + Qt-free geometry.

No OS mouse injection is needed to verify positioning and tip calculations.
"""
import ast
import math
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text('utf8')
ROD = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf8')


def _method(class_name, name, namespace=None):
    cls = next(n for n in ast.parse(ROD).body if isinstance(n, ast.ClassDef)
               and n.name == class_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name == name)
    env = dict(namespace or {})
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'rod.py', 'exec'), env)
    return env[name]


class Obj:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.xpos, self.ypos = -100, -100
    def width(self): return self.w
    def height(self): return self.h
    def move(self, x, y): self.xpos, self.ypos = x, y
    def y(self): return self.ypos


def test_layout_moves_physical_marker_inside_blue_above_grigri():
    assert 'PAD_HEIGHT = 144' in ROD
    assert 'self.pointer_rod_origin = MousePointerRodOrigin(self.pointer_rod)' in REMOTE
    assert 'root.addWidget(self.pointer_rod_origin)' not in REMOTE
    assert 'root.addWidget(self.pointer_rod)' in REMOTE
    assert 'root.addWidget(self.up_band)' in REMOTE
    assert REMOTE.index('root.addWidget(self.pointer_rod)') < REMOTE.index('root.addWidget(self.up_band)')
    assert 'self.pointer_rod.set_origin_marker(self.pointer_rod_origin)' in REMOTE
    assert 'origin.setVisible(enabled)' in REMOTE
    assert 'WA_TransparentForMouseEvents' in ROD


def test_button_and_pivot_share_center_and_marker_is_just_above_button():
    button = Obj(68, 46)
    marker = Obj(22, 22)
    model = NS(width=lambda:174, height=lambda:144,
               _wheel_pad=button, _origin_marker=marker,
               ORIGIN_GAP_ABOVE_GRIGRI=5)
    position_origin = _method('MousePointerRodPad', '_position_origin_marker')
    model._position_origin_marker = lambda: position_origin(model)
    position_button = _method('MousePointerRodPad', '_position_wheel_pad')
    position_button(model)
    assert (button.xpos, button.ypos) == (53, 94)
    assert (marker.xpos, marker.ypos) == (76, 67)
    assert marker.xpos + marker.width()/2 == button.xpos + button.width()/2 == 87
    assert marker.ypos + marker.height() + 5 == button.ypos
    assert marker.ypos >= 61  # leave space for small 10px operation captions


def test_origin_geometry_is_real_marker_center_not_old_below_band():
    origin_local = _method('MousePointerRodPad', 'origin_local',
                           {'QPoint': lambda x, y:(x,y)})
    origin_global = _method('MousePointerRodPad', 'origin_global',
                            {'QPoint': lambda x, y:(x,y)})
    marker = NS(isVisible=lambda:True, origin_global=lambda:(487, 267))
    obj = NS(_origin_marker=marker,
             mapFromGlobal=lambda pt:NS(x=lambda:pt[0]-400, y=lambda:pt[1]-200),
             mapToGlobal=lambda pt:(pt[0]+400,pt[1]+200),
             width=lambda:174, height=lambda:144, BASE_BOTTOM_MARGIN=66)
    assert origin_local(obj) == (87.,67.)
    assert origin_global(obj) == (487,267)
    obj._origin_marker = None
    assert origin_local(obj) == (87.,78.)  # standalone/no-marker fallback only


def test_smart_vertical_follows_new_pivot_without_losing_x_or_collinearity():
    import sys
    sys.path.insert(0, str(ROOT / 'src'))
    from mouse_pointer_rod_smart_model import smart_vertical_step
    from mouse_pointer_rod_model import rod_endpoint
    origin=(87,78)
    cursor=(122,40)
    dx,dy=(cursor[0]-origin[0],cursor[1]-origin[1])
    n=math.hypot(dx,dy)
    tip=rod_endpoint(origin,(dx/n,dy/n),420)
    for step in (-15, 15, -60, 60):
        res=smart_vertical_step(origin,tip,cursor,step,
                                (0,0,173,143),(53,94,121,140))
        assert res is not None
        assert abs(res.tip[0]-tip[0]) < 1e-6
        assert abs(res.tip[1]-tip[1]-step) < 1e-6
        cx,cy=res.cursor
        assert 3 <= cx <= 170 and 3 <= cy <= 140
        assert not (50 <= cx <= 124 and 91 <= cy <= 143)
        rx,ry=(res.tip[0]-origin[0],res.tip[1]-origin[1])
        px,py=(cx-origin[0],cy-origin[1])
        assert abs(rx*py-ry*px)<1e-5
        assert 0 < math.hypot(px,py) <= res.length


def test_length_and_windows_click_modes_still_share_one_origin():
    assert 'return rod_endpoint(self.origin_global(), self._direction, self._length)' in ROD
    assert 'origin = self.origin_local()' in ROD
    assert 'self._dispatch_windows_click(action, remote, launcher)' in ROD
    assert 'self._smart_expected_cursor = new_global' in ROD
    assert 'self._in_blue(new_local)' in ROD
    assert 'self._position_origin_marker()' in ROD
