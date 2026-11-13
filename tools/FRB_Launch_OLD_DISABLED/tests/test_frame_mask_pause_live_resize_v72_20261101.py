"""v72: outer window mask is suspended during live LIGHT resize only.

Extract real Launcher event methods into a Qt-free test subclass to validate
state transitions. This does not replace a Windows+DWM visual check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(APP)
LAUNCHER = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
METHODS = {node.name: node for node in LAUNCHER.body if isinstance(node, ast.FunctionDef)}


def extract(names, env, superclass=object):
    """Build a subclass from actual Launcher methods, preserving super()."""
    cls = ast.ClassDef(name='Probe', bases=[ast.Name(id='FakeBase', ctx=ast.Load())],
                       keywords=[], body=[METHODS[name] for name in names], decorator_list=[])
    scope = {'FakeBase': superclass, **env}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
                 '<Launcher methods>', 'exec'), scope)
    return scope['Probe']


def fake_window(probe_type, theme):
    win = probe_type()
    win.__dict__.update(Fake(theme).__dict__)
    return win


class Base:
    def mousePressEvent(self, event):
        pass
    def mouseReleaseEvent(self, event):
        pass
    def resizeEvent(self, event):
        pass


class Fake:
    def __init__(self, theme):
        self.color_theme = theme
        self._frame_resize_mask_suspended = False
        self._size_drag = None
        self.hover_timer = NS(stop=Mock())
        self.menu = None
        self.view_mode = 'expanded'
        self.expanded_view = NS(_workspace_mode='files', web_view=None,
                                favorite_popup=NS(isVisible=lambda: False))
        self.clearMask = Mock()
        self.update_window_shape = Mock()
        self.update = Mock()
        self.close_cascade_for_main_interaction = Mock()
        self.geometry = lambda: 'original'
        self.resize_edge = lambda pos: 'right'
        self.save_window_size = Mock()
        self.can_save_normal_window_geometry = lambda: False
        self.isVisible = lambda: False


def mouse_event():
    return NS(button=lambda: 1, position=lambda: 'here',
              globalPosition=lambda: NS(toPoint=lambda: 'cursor'), accept=Mock())


ENV = {'Qt': NS(MouseButton=NS(LeftButton=1, RightButton=2)),
       'theme_family': lambda name: name}


def test_light_resize_removes_mask_and_reapplies_after_release():
    Probe = extract(('mousePressEvent', 'mouseReleaseEvent'), ENV, Base)
    win = fake_window(Probe, 'light')
    win.mousePressEvent(mouse_event())
    assert win._frame_resize_mask_suspended is True
    win.clearMask.assert_called_once()
    win.update.assert_called_once()
    assert win._size_drag[0] == 'right'
    win.mouseReleaseEvent(mouse_event())
    assert win._frame_resize_mask_suspended is False
    win.update_window_shape.assert_called_once()
    assert win.update.call_count == 2
    win.save_window_size.assert_called_once()


def test_dark_resize_retains_original_rounded_mask_behavior():
    Probe = extract(('mousePressEvent', 'mouseReleaseEvent'), ENV, Base)
    win = fake_window(Probe, 'dark')
    win.mousePressEvent(mouse_event())
    assert win._frame_resize_mask_suspended is False
    win.clearMask.assert_not_called()
    win.mouseReleaseEvent(mouse_event())
    win.update_window_shape.assert_not_called()


def test_resize_event_skips_shape_updates_while_suspended():
    Probe = extract(('resizeEvent',), {}, Base)
    win = fake_window(Probe, 'light')
    win._frame_resize_mask_suspended = True
    win.resizeEvent(object())
    win.update_window_shape.assert_not_called()
    win._frame_resize_mask_suspended = False
    win.resizeEvent(object())
    win.update_window_shape.assert_called_once()


def test_outer_frame_paints_newly_exposed_pixels_in_light_theme():
    paint = ast.get_source_segment(APP, METHODS['paintEvent'])
    assert "if getattr(self, '_frame_resize_mask_suspended', False):" in paint
    assert 'painter.fillRect(self.rect(), QColor(fill))' in paint
    assert paint.index('painter.fillRect(self.rect(), QColor(fill))') < paint.index('painter.drawRoundedRect(outer,')
