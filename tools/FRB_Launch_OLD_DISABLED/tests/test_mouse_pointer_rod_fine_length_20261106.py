"""Mouse Pointer Rod v0.8: blue hold-fast, native ぐりぐり ownership (Qt-free)."""
from pathlib import Path
import ast
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_model import (
    DEFAULT_LENGTH, MIN_LENGTH, MAX_LENGTH, NORMAL_WHEEL_STEP_PX,
    FAST_WHEEL_STEP_PX, length_after_wheel, direction_from_pointer,
)


def extract_method(path, klass_name, method_name, env):
    tree = ast.parse((ROOT / path).read_text('utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), 'exec'), env)
    return env[method_name]


def test_gear_is_15_normal_60_held_and_length_bounds_hold():
    assert (NORMAL_WHEEL_STEP_PX, FAST_WHEEL_STEP_PX) == (15, 60)
    assert length_after_wheel(420, 1) == 435
    assert length_after_wheel(420, -1) == 405
    assert length_after_wheel(420, 1, fast=True) == 480
    assert length_after_wheel(420, -2, fast=True) == 300
    assert length_after_wheel(420, 0, fast=True) == 420
    assert length_after_wheel(MIN_LENGTH, -999, fast=True) == MIN_LENGTH
    assert length_after_wheel(MAX_LENGTH, 999) == MAX_LENGTH


def test_real_aim_motion_never_changes_length_or_gear():
    events=[]
    rod=NS(_enabled=True, _length=DEFAULT_LENGTH, _direction=(0,-1),
           _wheel_pad=None, origin_local=lambda:(60,120),
           _in_blue=lambda p: True,
           _sync_hover=lambda: None,
           refresh_position=lambda:events.append('refresh'))
    move=extract_method('src/mouse_pointer_rod.py','MousePointerRodPad','mouseMoveEvent',
                        dict(direction_from_pointer=direction_from_pointer))
    def at(x,y):
        return NS(position=lambda:NS(x=lambda:x, y=lambda:y,
                   toPoint=lambda:(x,y)), accept=lambda:events.append('accept'))
    for x,y in [(60,119),(60,110),(60,30),(80,5),(110,80)]:
        move(rod,at(x,y))
        assert rod._length == 420
    assert events==['refresh','accept']*5


def test_adjust_length_switches_only_when_explicit_fine_modifier_active():
    rod=NS(_enabled=True, _length=420, refresh_position=Mock())
    adjust=extract_method('src/mouse_pointer_rod.py','MousePointerRodPad','adjust_length',
                          dict(length_after_wheel=length_after_wheel))
    adjust(rod,1)
    assert rod._length == 435
    adjust(rod,-1,fast=True)
    assert rod._length == 375
    adjust(rod,2,fast=True)
    assert rod._length == 495
    adjust(rod,-1)
    assert rod._length == 480
    rod._enabled=False
    adjust(rod,5,fast=True)
    assert rod._length == 480


def test_native_wheelpad_still_emits_navigation_even_while_rod_enabled():
    wheel=extract_method('src/launch_remote.py','WheelPad','wheelEvent',{})
    rod=NS(_enabled=True, adjust_length=Mock())
    remote=NS(pointer_rod=rod, scroll_pad=None,
              adjust_background_opacity_from_wheel=lambda e:False)
    commands=NS(emit=Mock())
    pad=NS(parentWidget=lambda:remote, _angle_remainder=0,
           _pixel_remainder=0, command=commands)
    def wheel_event(delta):
        return NS(angleDelta=lambda:NS(y=lambda:delta),
                  pixelDelta=lambda:NS(y=lambda:0),accept=Mock())
    wheel(pad,wheel_event(120))
    wheel(pad,wheel_event(-120))
    assert [c.args for c in commands.emit.call_args_list] == [('UP',), ('DOWN',)]
    rod.adjust_length.assert_not_called()


def test_native_wheelpad_long_press_not_disabled_in_rod_mode():
    method=extract_method('src/launch_remote.py','WheelPad','_show_target_menu',{})
    preview=NS(present=Mock())
    pad=NS(_pressed=True,_dragged=False,_drag_start_pos=(5,5),
           _target_allowed=lambda:True,_target_preview=preview,
           _target_entries=('EXP','LIST'),_target_choice=None,
           _target_menu_open=False)
    method(pad)
    assert pad._target_menu_open
    preview.present.assert_called_once()


def test_distance_does_not_appear_in_gear_or_angle_storage():
    model=(ROOT/'src/mouse_pointer_rod_model.py').read_text('utf-8')
    src=(ROOT/'src/mouse_pointer_rod.py').read_text('utf-8')
    assert 'wheel_step_for_distance' not in model
    assert '_pointer_radius' not in src
    assert 'length_after_wheel(self._length, steps, fast=fast)' in src
    assert '通常：{NORMAL_WHEEL_STEP_PX}px' in src
    assert '押下：{FAST_WHEEL_STEP_PX}px' in src
    assert not any(tok in src for tok in ['SendInput','SetCursorPos','pyautogui.click'])
