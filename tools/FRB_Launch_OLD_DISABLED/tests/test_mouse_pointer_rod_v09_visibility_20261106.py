"""v0.9: delayed, unobtrusive Mouse Pointer Rod visibility contract.

Qt-independent unit tests execute production handlers (AST extraction) against
small fakes. Visual appearance and native child-entry require Windows smoke tests.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
ROD = ROOT / 'src' / 'mouse_pointer_rod.py'


def actual_method(name, klass='MousePointerRodPad', scope=None):
    tree = ast.parse(ROD.read_text('utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {} if scope is None else scope
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'mouse_pointer_rod.py', 'exec'), scope)
    return scope[name]


def test_hover_delay_is_250ms_and_repeated_motion_does_not_restart_timer():
    src = ROD.read_text('utf-8')
    assert 'HOVER_REVEAL_MS = 250' in src
    assert 'WHEEL_EMPHASIS_MS = 650' in src
    assert 'self._hover_timer.setSingleShot(True)' in src
    assert 'self._hover_timer.timeout.connect(self._show_after_hover)' in src

    fake_cursor = NS(pos=lambda: (60, 50))
    hover = actual_method('_sync_hover', scope={
        'QCursor': fake_cursor,
        'direction_from_pointer': lambda a, b, before: (0, -1),
    })
    timer = NS(start=Mock(), stop=Mock())
    rod = NS(_aim_hovering=False, _aim_visible=False,
             _hover_timer=timer, HOVER_REVEAL_MS=250,
             _direction=(1, 0),
             _cursor_on_blue=lambda: True,
             mapFromGlobal=lambda _: NS(x=lambda:50, y=lambda:30),
             origin_local=lambda:(50, 160),
             _stop_aiming=Mock())
    hover(rod)
    hover(rod)
    assert rod._aim_hovering
    assert rod._direction == (0, -1)
    timer.start.assert_called_once_with(250)
    assert not rod._aim_visible
    rod._stop_aiming.assert_not_called()


def test_timer_shows_only_while_still_hovering_over_blue():
    reveal = actual_method('_show_after_hover')
    rod = NS(_aim_hovering=True, _aim_visible=False,
             _cursor_on_blue=lambda: True,
             refresh_position=Mock(), _stop_aiming=Mock())
    reveal(rod)
    assert rod._aim_visible
    rod.refresh_position.assert_called_once()
    rod._aim_visible = False
    rod._cursor_on_blue = lambda: False
    reveal(rod)
    assert not rod._aim_visible
    rod._stop_aiming.assert_called_once()
    assert rod.refresh_position.call_count == 1


def test_leaving_blue_cancels_both_timers_and_hides_overlay():
    stop = actual_method('_stop_aiming')
    overlay = NS(set_emphasis=Mock())
    hover_timer = NS(stop=Mock())
    wheel_timer = NS(stop=Mock())
    rod = NS(_hover_timer=hover_timer, _wheel_emphasis_timer=wheel_timer,
             _aim_hovering=True, _aim_visible=True, _overlay=overlay,
             hide_overlay=Mock())
    stop(rod)
    assert not rod._aim_hovering and not rod._aim_visible
    hover_timer.stop.assert_called_once()
    wheel_timer.stop.assert_called_once()
    rod.hide_overlay.assert_called_once()
    overlay.set_emphasis.assert_called_once_with(False)


def test_wheel_reveals_immediately_and_is_briefly_emphasized():
    on_wheel = actual_method('_show_on_wheel')
    end_emphasis = actual_method('_end_wheel_emphasis')
    overlay = NS(set_emphasis=Mock())
    rod = NS(_aim_hovering=False, _aim_visible=False,
             _cursor_on_blue=lambda: True, _sync_hover=Mock(),
             _hover_timer=NS(stop=Mock()),
             _wheel_emphasis_timer=NS(start=Mock()),
             WHEEL_EMPHASIS_MS=650, _overlay=overlay,
             refresh_position=Mock())
    on_wheel(rod)
    assert rod._aim_hovering and rod._aim_visible
    rod.refresh_position.assert_called_once()
    rod._hover_timer.stop.assert_called_once()
    overlay.set_emphasis.assert_called_with(True)
    rod._wheel_emphasis_timer.start.assert_called_once_with(650)
    end_emphasis(rod)
    overlay.set_emphasis.assert_called_with(False)


def test_remote_refresh_cannot_revive_overlay_when_inactive_or_away():
    class FakeOverlay:
        def __init__(self, parent):
            raise AssertionError('inactive refresh must not create overlay')
    refresh = actual_method('refresh_position', scope={'MousePointerRodOverlay': FakeOverlay})
    rod = NS(_enabled=True, _aim_visible=False,
             isVisible=lambda: True,
             _cursor_on_blue=lambda: True)
    refresh(rod)
    rod._aim_visible = True
    rod._cursor_on_blue=lambda: False
    rod._stop_aiming=Mock()
    refresh(rod)
    rod._stop_aiming.assert_called_once()


def test_central_grigri_is_excluded_and_cannot_steal_native_commands():
    in_blue = actual_method('_in_blue')
    class Rect:
        def __init__(self, owner): self.owner = owner
        def contains(self, point): return self.owner(point)
    rod=NS(rect=lambda:Rect(lambda pt:0<=pt[0]<200 and 0<=pt[1]<180),
           _wheel_pad=NS(geometry=lambda:Rect(lambda pt:70<=pt[0]<130 and 60<=pt[1]<120)))
    assert in_blue(rod, (20, 40))
    assert not in_blue(rod, (100, 90))
    assert not in_blue(rod, (250, 90))
    src = ROD.read_text('utf-8')
    assert 'pad.installEventFilter(self)' in src
    assert 'self._stop_aiming()' in src
    assert 'if event.type() == QEvent.Type.Enter:' in src
    assert "self._dispatch_tip_action('double' if self._double_pending else 'select')" in src
    assert 'self.adjust_length(steps, fast=fast)' in src
    for forbidden in ('SetCursorPos', 'SendInput(', 'QCursor.setPos('):
        assert forbidden not in src


def test_overlay_uses_soft_line_with_visible_tip_not_fully_opaque():
    source = ROD.read_text('utf-8')
    assert 'line_alpha = 130 if self._emphasized else 72' in source
    assert 'QColor(46, 106, 215, 190)' in source
    assert 'QColor(50, 111, 223, 200)' in source
    assert 'Qt.WindowType.WindowTransparentForInput' in source
    assert 'Qt.WidgetAttribute.WA_TransparentForMouseEvents' in source


def test_mode_toggle_resets_hover_and_never_instantly_shows_overlay():
    toggle = actual_method('set_mode_enabled', scope={'QTimer':NS(singleShot=Mock())})
    callbacks=[]
    class Timer:
        @staticmethod
        def singleShot(ms, callback):
            callbacks.append((ms, callback))
    toggle = actual_method('set_mode_enabled', scope={'QTimer':Timer})
    rod=NS(_enabled=False, _double_pending=True,
           _left_pressed=True, _wheel_during_press=True,
           setVisible=Mock(), _stop_aiming=Mock(), _sync_hover=Mock())
    toggle(rod,True)
    assert rod._enabled and not rod._left_pressed and not rod._double_pending
    rod.setVisible.assert_called_with(True)
    rod._stop_aiming.assert_called_once()
    assert callbacks==[(0,rod._sync_hover)]
    toggle(rod,False)
    assert not rod._enabled
    rod.setVisible.assert_called_with(False)
    assert len(callbacks)==1  # no delayed activation on disable
    assert rod._stop_aiming.call_count==2


def test_remote_hide_cancels_pending_hover_not_only_overlay_paint():
    source = (ROOT/'src'/'launch_remote.py').read_text('utf-8')
    cls = next(n for n in ast.parse(source).body
               if isinstance(n, ast.ClassDef) and n.name=='LaunchRemote')
    hides = [n for n in cls.body if isinstance(n, ast.FunctionDef)
             and n.name=='hideEvent']
    final_hide = ast.get_source_segment(source,hides[-1])
    assert 'rod._stop_aiming()' in final_hide
    assert 'rod.hide_overlay()' in final_hide
