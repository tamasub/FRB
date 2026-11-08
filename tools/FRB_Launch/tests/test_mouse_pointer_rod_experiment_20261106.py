"""Qt-free contract checks for the opt-in Mouse Pointer Rod aim-only test."""
from pathlib import Path
import ast
import math
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_model import (
    DEFAULT_LENGTH, MAX_LENGTH, MIN_LENGTH,
    NORMAL_WHEEL_STEP_PX, FAST_WHEEL_STEP_PX,
    direction_from_pointer, length_after_wheel, rod_endpoint,
)


def test_wheel_step_and_clamping():
    assert DEFAULT_LENGTH == 420
    assert (NORMAL_WHEEL_STEP_PX,FAST_WHEEL_STEP_PX) == (15,60)
    assert length_after_wheel(420, 1) == 435
    assert length_after_wheel(420, 1, fast=True) == 480
    assert length_after_wheel(420, -2, fast=True) == 300
    assert length_after_wheel(MIN_LENGTH, -200, fast=True) == MIN_LENGTH
    assert length_after_wheel(MAX_LENGTH, 200) == MAX_LENGTH
    assert length_after_wheel(420, 0) == 420


def test_angle_only_depends_on_pointer_relative_to_origin_not_velocity():
    up_right = direction_from_pointer((100, 220), (160, 140))
    assert math.isclose(up_right[0], 0.6)
    assert math.isclose(up_right[1], -0.8)
    # Moving the whole Remote window preserves the same relative angle.
    assert direction_from_pointer((500, 600), (560, 520)) == up_right
    assert direction_from_pointer((100, 220), (100, 220), up_right) == up_right
    assert direction_from_pointer((100, 220), (70, 220)) == (-1.0, 0.0)


def test_endpoint_follows_length_and_angle_not_app_specific_widgets():
    direction = direction_from_pointer((100, 220), (160, 140))
    assert rod_endpoint((100, 220), direction, 500) == (400.0, -180.0)
    assert rod_endpoint((200, 220), direction, 500) == (500.0, -180.0)
    assert rod_endpoint((100, 220), direction, 100) == (160.0, 140.0)


def test_settings_toggle_is_opt_in_persisted_and_reversible():
    src = (ROOT / 'src' / 'app.py').read_text('utf-8')
    assert "'experiment_mouse_pointer_rod', 'false'" in src
    # Public menu now exposes three exclusive modes under one submenu.
    assert "self.theme_menu.addMenu('マウス差し棒')" in src
    assert "self.mouse_pointer_rod_choice_group.setExclusive(True)" in src
    assert "self.select_mouse_pointer_rod_choice(key)" in src
    launcher = next(n for n in ast.parse(src).body
                    if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    setter = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'set_mouse_pointer_rod_mode')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[setter], type_ignores=[])),
                 'app.py', 'exec'), scope)
    store = {}
    settings = NS(setValue=lambda k, v: store.__setitem__(k, v), sync=Mock())
    remote = NS(set_mouse_pointer_rod_enabled=Mock())
    fake = NS(settings=settings, remote_window=remote,
              mouse_pointer_rod_action=NS(setChecked=Mock()),
              footer=NS(setText=Mock()), mouse_pointer_rod_mode=False)
    scope['set_mouse_pointer_rod_mode'](fake, True)
    assert store == {'experiment_mouse_pointer_rod': True}
    remote.set_mouse_pointer_rod_enabled.assert_called_with(True)
    scope['set_mouse_pointer_rod_mode'](fake, False)
    assert store == {'experiment_mouse_pointer_rod': False}
    remote.set_mouse_pointer_rod_enabled.assert_called_with(False)


def test_wheelpad_and_blue_surface_have_separate_wheel_ownership():
    remote = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
    rod = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')
    assert 'self.pad.wheelEvent(event)' in remote
    assert "if obj is getattr(self, 'pointer_rod', None):" in remote
    assert 'self.adjust_length(steps, fast=fast)' in rod
    assert 'self.command.emit(direction)' in remote
    assert 'root.addWidget(self.pointer_rod)' in remote
    assert 'self.pointer_rod.set_mode_enabled(enabled)' in remote
    assert 'self.pad.setParent(self.pointer_rod)' in remote
    assert 'self.pad.setParent(self)' in remote


def test_desktop_overlay_does_not_inject_mouse_or_intercept_input():
    source = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')
    assert 'Qt.WindowType.WindowTransparentForInput' in source
    assert 'Qt.WidgetAttribute.WA_TransparentForMouseEvents' in source
    assert 'self.setMouseTracking(True)' in source
    assert 'self._direction = direction_from_pointer(' in source
    assert 'rod_endpoint(self.origin_global()' in source
    assert 'event.accept()' in source
    for prohibited in ('SendInput', 'mouse_event(', 'SetCursorPos', 'QCursor.setPos',
                       'win32api.mouse_event', 'pyautogui.click'):
        assert prohibited not in source


def test_real_wheelpad_method_keeps_normal_scroll_in_both_modes():
    source = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
    klass = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef)
                 and n.name == 'WheelPad')
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'wheelEvent')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 'launch_remote.py', 'exec'), scope)

    class Event:
        def __init__(self, delta):
            self.delta = delta
            self.accepted = False
        def angleDelta(self):
            return NS(y=lambda: self.delta)
        def pixelDelta(self):
            return NS(y=lambda: 0)
        def accept(self):
            self.accepted = True

    for enabled in (True, False):
        rod = NS(_enabled=enabled, adjust_length=Mock())
        remote = NS(pointer_rod=rod, scroll_pad=None,
                    adjust_background_opacity_from_wheel=lambda ev: False)
        pad = NS(parentWidget=lambda: remote,
                 _angle_remainder=0, _pixel_remainder=0,
                 command=NS(emit=Mock()))
        event = Event(120)
        scope['wheelEvent'](pad, event)
        assert event.accepted
        rod.adjust_length.assert_not_called()
        pad.command.emit.assert_called_once_with('UP')


def test_effective_remote_move_handler_refreshes_rod_anchor():
    remote = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
    cls = next(n for n in ast.parse(remote).body if isinstance(n, ast.ClassDef)
               and n.name == 'LaunchRemote')
    moves = [n for n in cls.body if isinstance(n, ast.FunctionDef)
             and n.name == 'moveEvent']
    assert moves  # Later duplicate definitions override earlier definitions.
    final_move = ast.get_source_segment(remote, moves[-1])
    assert 'rod.refresh_position()' in final_move
    hides = [n for n in cls.body if isinstance(n, ast.FunctionDef)
             and n.name == 'hideEvent']
    final_hide = ast.get_source_segment(remote, hides[-1])
    assert 'rod.hide_overlay()' in final_hide
