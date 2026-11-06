"""v0.8 ownership: blue aims/selects; central ぐりぐり keeps native commands.

Run without Qt (Windows/PySide6 interaction needs a real-device smoke test).
This calls production handlers extracted with AST, not mirrored algorithms.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_model import DEFAULT_LENGTH, length_after_wheel
from mouse_pointer_rod_direct import direct_files_action
from test_mouse_pointer_rod_direct_v06 import Point, harness


def _method(path, klass, name, globals_=None):
    src = (ROOT / path).read_text('utf-8')
    cls = next(n for n in ast.parse(src).body
               if isinstance(n, ast.ClassDef) and n.name == klass)
    fn = next(n for n in cls.body
              if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(globals_ or {})
    exec(compile(ast.Module(body=[fn], type_ignores=[]), path, 'exec'), scope)
    return scope[name]


class Containment:
    def __init__(self, contains=False):
        self.is_inside = contains
    def contains(self, point):
        return self.is_inside


def test_real_rod_wheel_changes_length_and_held_wheel_suppresses_click():
    Qt = NS(MouseButton=NS(LeftButton=1, RightButton=2))
    press = _method('src/mouse_pointer_rod.py', 'MousePointerRodPad',
                    'mousePressEvent', {'Qt':Qt})
    release = _method('src/mouse_pointer_rod.py', 'MousePointerRodPad',
                      'mouseReleaseEvent', {'Qt':Qt})
    wheel = _method('src/mouse_pointer_rod.py', 'MousePointerRodPad',
                    'wheelEvent', {'Qt':Qt})
    adjust = _method('src/mouse_pointer_rod.py', 'MousePointerRodPad',
                     'adjust_length', {'length_after_wheel':length_after_wheel})
    actions=[]
    rod=NS(_enabled=True, _length=DEFAULT_LENGTH,
           _wheel_angle_remainder=0, _wheel_pixel_remainder=0,
           _wheel_during_press=False, _left_pressed=False, _double_pending=False,
           _wheel_pad=NS(geometry=lambda:Containment(False)),
           rect=lambda:Containment(True),
           refresh_position=Mock(),
           _dispatch_tip_action=lambda op:actions.append(op),
           _show_on_wheel=Mock())
    rod.adjust_length=lambda steps,fast=False:adjust(rod,steps,fast=fast)
    evt = lambda b: NS(button=lambda:b,accept=Mock(),
                       position=lambda:NS(toPoint=lambda:(5,5)))
    wevt = lambda delta=120,buttons=0: NS(
        angleDelta=lambda:NS(y=lambda:delta),
        pixelDelta=lambda:NS(y=lambda:0),
        buttons=lambda:buttons, accept=Mock())
    wheel(rod, wevt())
    assert rod._length == 435
    press(rod, evt(1))
    wheel(rod, wevt())
    assert rod._length == 495  # held = 60px
    release(rod, evt(1))
    assert actions == []  # release after fast wheel must not select another row
    press(rod, evt(1))
    release(rod, evt(1))
    assert actions == ['select']


def test_real_rod_double_right_and_central_area_guard():
    Qt = NS(MouseButton=NS(LeftButton=1, RightButton=2))
    move = _method('src/mouse_pointer_rod.py','MousePointerRodPad',
                   'mouseMoveEvent', {'direction_from_pointer':
                                      __import__('mouse_pointer_rod_model').direction_from_pointer})
    double = _method('src/mouse_pointer_rod.py','MousePointerRodPad',
                     'mouseDoubleClickEvent', {'Qt':Qt})
    release = _method('src/mouse_pointer_rod.py','MousePointerRodPad',
                      'mouseReleaseEvent', {'Qt':Qt})
    context = _method('src/mouse_pointer_rod.py','MousePointerRodPad',
                      'contextMenuEvent', {'Qt':Qt})
    actions=[]
    rod=NS(_enabled=True, _direction=(0,-1), _length=420,
           origin_local=lambda:(80,170),
           refresh_position=Mock(),
           _wheel_pad=NS(geometry=lambda:Containment(True)),
           _double_pending=False,_wheel_during_press=False,
           _left_pressed=False,rect=lambda:Containment(True),
           _in_blue=lambda pt: not rod._wheel_pad.geometry().contains(pt),
           _stop_aiming=Mock(), _sync_hover=Mock(),
           _dispatch_tip_action=lambda op:actions.append(op))
    evt=NS(position=lambda:NS(x=lambda:100,y=lambda:30,toPoint=lambda:(100,30)),
           accept=Mock(),button=lambda:1)
    move(rod,evt)
    assert rod._direction == (0,-1) # central grigri holds the last angle
    assert rod._length == 420
    rod._wheel_pad = NS(geometry=lambda:Containment(False))
    move(rod,evt)
    assert rod._direction[0] > 0
    double(rod,evt)
    release(rod,evt)
    assert actions == ['double']
    context(rod,evt)
    assert actions == ['double'] # no right menu from blue surface


def test_direct_list_double_is_select_only_and_exp_double_toggles():
    launcher, list_tree, exp_tree = harness()
    launcher.expanded_view.activate_row=Mock()
    assert direct_files_action(launcher, (320,220), 'double', point_type=Point)
    assert list_tree.current is list_tree.item
    launcher.expanded_view.activate_row.assert_not_called()
    assert direct_files_action(launcher, (120,220), 'double', point_type=Point)
    assert exp_tree.expansions == ['expand']


def test_real_remote_mode_switch_reparents_single_existing_button():
    Qt=NS(AlignmentFlag=NS(AlignHCenter=0))
    QTimer=NS(singleShot=lambda delay, callback: None)
    setter=_method('src/launch_remote.py','LaunchRemote',
                   'set_mouse_pointer_rod_enabled', {'Qt':Qt,'QTimer':QTimer})

    class Root:
        def __init__(self):
            self.actions=[]
        def removeWidget(self, widget): self.actions.append(('remove', widget))
        def insertWidget(self, index, widget, stretch, align):
            self.actions.append(('insert', index, widget))
        def activate(self):pass
        def sizeHint(self):return NS(height=lambda:330)

    root=Root()
    rod=NS(set_wheel_pad=Mock(),set_mode_enabled=Mock(),refresh_position=Mock())
    pad=NS(_hide_target_menu=Mock(),_pressed=False,_drag_start_pos=None,
           _dragged=False,_ignore_double_release=False,
           setParent=Mock(),show=Mock(),hide=Mock(),setToolTip=Mock())
    win=NS(_pad_inside_rod=False, _pad_layout_index=4,
           pointer_rod=rod, pad=pad,layout=lambda:root,
           setMinimumHeight=Mock(),adjustSize=Mock(),
           _clamp_pointer_rod_to_screen=Mock())
    setter(win,True)
    assert win._pad_inside_rod
    assert root.actions[0] == ('remove',pad)
    pad.setParent.assert_called_with(rod)
    rod.set_wheel_pad.assert_called_with(pad)
    rod.set_mode_enabled.assert_called_with(True)
    setter(win,False)
    assert not win._pad_inside_rod
    pad.setParent.assert_called_with(win)
    assert root.actions[-1] == ('insert',4,pad)
    rod.set_wheel_pad.assert_called_with(None)
    rod.set_mode_enabled.assert_called_with(False)


def test_external_wheels_still_forward_to_native_pad():
    s=(ROOT/'src/launch_remote.py').read_text('utf-8')
    assert "if obj is getattr(self, 'pointer_rod', None):" in s
    assert 'self.pad.wheelEvent(event)' in s
    assert 'if (not self._pressed or self._dragged' in s
    assert 'self._target_hold_timer.timeout.connect(self._show_target_menu)' in s
    rod=(ROOT/'src/mouse_pointer_rod.py').read_text('utf-8')
    assert 'BASE_BOTTOM_MARGIN = 19' in rod
    assert 'def _position_wheel_pad(self)' in rod
    for tok in ('SendInput(', 'SetCursorPos(', 'QCursor.setPos('):
        assert tok not in rod
