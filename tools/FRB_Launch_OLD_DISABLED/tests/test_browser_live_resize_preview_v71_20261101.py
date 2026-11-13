"""v71: live resize keeps an opaque, light-mode screenshot over Chromium.

These tests intentionally avoid Windows/PySide6 dependencies. Real WebEngine
compositing must still be verified on Windows with a mouse drag.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
WEB = (ROOT / 'src/launch_web_view.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def source_method(source, klass, method):
    module = ast.parse(source)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == klass)
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)


def extracted(source, klass, name, values=None):
    node = source_method(source, klass, name)
    env = dict(values or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<extracted>', 'exec'), env)
    return env[name]


def test_drag_handle_has_normal_arrow_cursor_and_same_drag_filter():
    assert 'self.workspace_drag_handle.setCursor(Qt.CursorShape.ArrowCursor)' in EXP
    assert 'self.workspace_drag_handle.setCursor(Qt.CursorShape.SizeAllCursor)' not in EXP
    assert 'self.workspace_drag_handle.installEventFilter(' in EXP
    assert 'self.launcher._passive_header_drag)' in EXP


def test_frame_live_resize_hooks_surround_set_geometry():
    start = ast.get_source_segment(APP, source_method(APP, 'Launcher', 'mousePressEvent'))
    move = ast.get_source_segment(APP, source_method(APP, 'Launcher', 'mouseMoveEvent'))
    stop = ast.get_source_segment(APP, source_method(APP, 'Launcher', 'mouseReleaseEvent'))
    assert 'self._size_drag = (edge, event.globalPosition().toPoint(), self.geometry())' in start
    assert "self.expanded_view._workspace_mode == 'browser'" in start
    assert 'web.begin_live_resize()' in start
    assert 'self.setGeometry(*rect)' in move
    assert 'web.end_live_resize()' in stop


def test_web_preview_is_opaque_and_paints_old_pixels_without_scaling():
    init = ast.get_source_segment(WEB, source_method(WEB, '_ResizePreview', '__init__'))
    paint = ast.get_source_segment(WEB, source_method(WEB, '_ResizePreview', 'paintEvent'))
    assert 'WA_OpaquePaintEvent' in init
    assert 'WA_TransparentForMouseEvents' in init
    assert 'painter.fillRect(self.rect(), self._fill)' in paint
    assert 'painter.drawPixmap(0, 0, self._snapshot)' in paint
    assert 'scaled(' not in paint


def test_begin_preview_freezes_while_light_and_before_view_is_hidden():
    fn = extracted(WEB, 'LaunchWebView', 'begin_live_resize', {
        'theme_family': lambda x:x,
        'theme_palette': lambda x:{'panel':'#fcfffd'},
    })
    calls = []
    view = NS(isVisible=lambda: True, grab=lambda: calls.append('grab') or 'snapshot',
              hide=lambda: calls.append('hide'))
    overlay = NS(set_preview=lambda *args: calls.append(('preview', *args)),
                 show=lambda: calls.append('show'),
                 raise_=lambda: calls.append('raise'))
    owner = NS(_current_theme='light', _resize_preview_active=False,
               current_view=lambda: view,
               _resize_preview=overlay, _position_resize_preview=lambda: calls.append('position'))
    fn(owner)
    assert owner._resize_preview_active
    assert owner._resize_preview_view is view
    assert calls.index('grab') < calls.index('hide')
    assert ('preview', 'snapshot', '#fcfffd') in calls
    assert calls.index('hide') < calls.index('show')

    # Dark mode must leave the live Chromium surface untouched.
    owner._current_theme = 'dark'
    owner._resize_preview_active = False
    calls.clear()
    fn(owner)
    assert not calls


def test_finish_preview_restores_original_webview_and_removes_snapshot():
    fn = extracted(WEB, 'LaunchWebView', '_finish_live_resize')
    calls = []
    timer = NS(start=lambda n:calls.append(('start-repair', n)))
    view = NS(show=lambda:calls.append('show-web'),
              update=lambda:calls.append('update-web'),
              _resize_surface_timer=timer)
    preview = NS(hide=lambda:calls.append('hide-preview'),
                 clear_preview=lambda:calls.append('clear-snapshot'))
    owner = NS(_resize_preview_active=True, _resize_preview_view=view,
               current_view=lambda:view, _resize_preview=preview)
    fn(owner)
    assert not owner._resize_preview_active
    assert owner._resize_preview_view is None
    assert calls == ['show-web', 'update-web', ('start-repair', 160),
                     'hide-preview', 'clear-snapshot']


def test_web_tabs_repositions_preview_on_each_resize():
    src = ast.get_source_segment(WEB, source_method(WEB, '_WebTabs', 'resizeEvent'))
    assert 'owner._position_resize_preview()' in src
    src = ast.get_source_segment(WEB, source_method(WEB, 'LaunchWebView', '_position_resize_preview'))
    assert 'width = max(view.width(), self.tabs.width() - top_left.x() - 4)' in src
    assert 'height = max(view.height(), self.tabs.height() - top_left.y() - 4)' in src


def test_end_preview_uses_short_delay_not_per_move_reloading():
    src = ast.get_source_segment(WEB, source_method(WEB, 'LaunchWebView', 'end_live_resize'))
    assert 'self._resize_preview_finish_timer.start(170)' in src
    assert 'reload(' not in src
    src = ast.get_source_segment(WEB, source_method(WEB, 'LaunchWebView', 'begin_live_resize'))
    assert 'reload(' not in src
