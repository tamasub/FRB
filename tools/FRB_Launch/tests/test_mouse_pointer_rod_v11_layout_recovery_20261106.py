"""v1.1 recovery: direct layout + detached origin, Qt-free source and logic checks."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT/'src/launch_remote.py').read_text('utf-8')
ROD = (ROOT/'src/mouse_pointer_rod.py').read_text('utf-8')


def method(name):
    cls = next(item for item in ast.parse(ROD).body
               if isinstance(item, ast.ClassDef) and item.name == 'MousePointerRodPad')
    node = next(item for item in cls.body
                if isinstance(item, ast.FunctionDef) and item.name == name)
    env = {'QPoint': lambda x,y: (x,y)}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'rod.py','exec'),env)
    return env[name]


def test_visual_order_blue_band_green_status_and_no_intervening_blue():
    parts = [
        'root.addWidget(self.pointer_rod)',
        'root.addWidget(self.up_band)',
        'root.addWidget(self.pointer_rod_origin)',
        'root.addWidget(status_frame)',
    ]
    starts = [REMOTE.index(part) for part in parts]
    assert starts == sorted(starts)
    assert "self.pointer_rod.set_origin_marker(self.pointer_rod_origin)" in REMOTE
    assert 'self.pointer_rod_origin = MousePointerRodOrigin(self)' in REMOTE


def test_green_marker_is_sibling_not_blue_and_only_visible_in_experiment():
    assert 'class MousePointerRodOrigin(QWidget):' in ROD
    assert "self.setObjectName('mousePointerRodOrigin')" in ROD
    assert 'self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)' in ROD
    assert 'origin.setVisible(enabled)' in REMOTE
    assert 'PAD_HEIGHT = 114' in ROD
    assert 'self.height() - pad.height() - 4' in ROD


def test_aim_angle_uses_lower_marker_not_blue_bottom():
    origin_local = method('origin_local')
    origin_global = method('origin_global')
    marker = NS(isVisible=lambda:True,origin_global=lambda:(500,800))
    fake = NS(_origin_marker=marker,
              mapFromGlobal=lambda point:NS(x=lambda:point[0]-400,
                                            y=lambda:point[1]-600),
              width=lambda:178,height=lambda:114, BASE_BOTTOM_MARGIN=19)
    assert origin_local(fake) == (100.,200.)  # below the 114px blue surface
    assert origin_global(fake) == (500,800)
    fake._origin_marker = None
    assert origin_local(fake) == (89.,95.)  # fallback for standalone preview


def test_control_boundaries_and_hover_remain_v09():
    assert 'self._in_blue(self.mapFromGlobal(QCursor.pos()))' in ROD
    assert 'self._wheel_pad.geometry().contains(local_point)' in ROD
    assert 'HOVER_REVEAL_MS = 250' in ROD
    assert 'self._dispatch_tip_action(\'double\' if self._double_pending else \'select\')' in ROD
    assert "if obj is getattr(self, 'pointer_rod', None):" in REMOTE
    assert 'self.pad.wheelEvent(event)' in REMOTE
    for prohibited in ('SetCursorPos', 'SendInput(', 'QCursor.setPos('):
        assert prohibited not in ROD
