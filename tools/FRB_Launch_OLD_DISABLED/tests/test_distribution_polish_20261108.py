"""2026-11-08 public-release polish: Qt-free regression coverage.

Windows mouse grabs, real foreground transitions and Studio WebView must be
confirmed manually on the target Windows 11 machine.
"""
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rod_foreground import foreground_owned_by_process

APP = (ROOT / 'src/app.py').read_text('utf-8')
ROD = (ROOT / 'src/mouse_pointer_rod.py').read_text('utf-8')
SHURIKEN = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
STUDIO_CSS = (ROOT.parent / 'studio/wwwroot/css/studio-presentation.css').read_text('utf-8')


def isolate(source, classname, method, env=None):
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == classname)
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'isolated', 'exec'), scope)
    return scope[method]


def test_files_exp_always_first_column_and_old_experiments_unregistered():
    assert 'self.files_root_hidden_mode = True\n        self.files_exp_embedded_mode = True' in APP
    assert "self.files_root_hidden_action = self.theme_menu.addAction" not in APP
    assert "self.files_exp_embedded_action = self.theme_menu.addAction" not in APP
    assert "self.settings.remove(retired_key)" in APP


def test_foreground_gate_same_foreign_unknown_and_exception():
    f = foreground_owned_by_process
    assert f(get_foreground=lambda: 55, get_pid=lambda hwnd: 1212, own_pid=1212) is True
    assert f(get_foreground=lambda: 55, get_pid=lambda hwnd: 3434, own_pid=1212) is False
    assert f(get_foreground=lambda: 0, get_pid=lambda hwnd: 1212, own_pid=1212) is False
    def fail(hwnd):
        raise OSError('window exited')
    assert f(get_foreground=lambda: 55, get_pid=fail, own_pid=1212) is False


def test_rod_aim_and_native_click_suppressed_when_foreground_is_foreign():
    cursor = isolate(ROD, 'MousePointerRodPad', '_cursor_on_blue')
    probe = NS(_enabled=True, isVisible=lambda: True,
               _launch_has_foreground=lambda: False,
               mapFromGlobal=Mock(side_effect=AssertionError('should not map cursor')))
    assert cursor(probe) is False
    probe.mapFromGlobal.assert_not_called()
    watcher = isolate(ROD, 'MousePointerRodPad', '_watch_foreground')
    probe._cancel_pending_native_click = Mock()
    probe._stop_aiming = Mock()
    watcher(probe)
    probe._cancel_pending_native_click.assert_called_once()
    probe._stop_aiming.assert_called_once()
    dispatch = isolate(ROD, 'MousePointerRodPad', '_dispatch_tip_action')
    probe._dispatch_windows_click = Mock()
    assert dispatch(probe, 'select') is False
    probe._dispatch_windows_click.assert_not_called()


def test_pointer_menus_connect_to_shared_grigri_adapter():
    timer_callbacks = []
    class FakeSignal:
        def __init__(self): self.callbacks = []
        def connect(self, cb): self.callbacks.append(cb)
        def emit(self):
            for cb in self.callbacks: cb()
    menu = NS(aboutToShow=FakeSignal())
    adapter = Mock(return_value=True)
    owner = NS(_enable_remote_context_wheel_for_menu=adapter)
    wire = isolate(APP, 'Launcher', '_wire_hybrid_context_menu',
                   {'QTimer': NS(singleShot=lambda ms, cb: timer_callbacks.append(cb))})
    wire(owner, menu)
    wire(owner, menu)
    assert len(menu.aboutToShow.callbacks) == 1  # idempotent
    menu.aboutToShow.emit()
    assert len(timer_callbacks) == 1
    timer_callbacks.pop()()
    adapter.assert_called_once_with(menu)
    for marker in ('self._wire_hybrid_context_menu(self.theme_menu)',
                   'self._wire_hybrid_context_menu(menu)',
                   'launcher._wire_hybrid_context_menu(self.more_menu)'):
        assert marker in APP or marker in (ROOT / 'src/launch_remote.py').read_text('utf-8')


def test_menu_cursor_starts_at_first_selectable_action():
    text = (ROOT / 'src/remote_context_wheel.py').read_text('utf-8')
    assert 'current = preferred if preferred in items else items[0]' in text
    assert 'if self._selected in items' in text


def test_shuriken_theme_keeps_original_light_and_has_dark_colors():
    assert "self.set_theme(current_theme)" in SHURIKEN
    assert "dark = self._theme == 'dark'" in SHURIKEN
    assert "painter.setBrush(QColor('#ffffff'))" in SHURIKEN
    assert "painter.setBrush(QColor('#aed2a0'))" in SHURIKEN
    assert "QColor('#eff7f2' if dark else '#254c35')" in SHURIKEN
    assert 'preview.set_theme(theme)' in (ROOT / 'src/launch_remote.py').read_text('utf-8')


def test_studio_dark_help_body_not_just_question_mark():
    assert 'studio-smart-search-help-panel' in STUDIO_CSS
    assert 'data-studio-theme="dark"' in STUDIO_CSS
    assert 'data-studio-theme="launch-dark"' in STUDIO_CSS
    assert '#searchSection .studio-smart-search-help-panel :is(h1,h2,h3,h4,h5,h6,p,li,th,td)' in STUDIO_CSS
    assert 'color:#e5ebf3' in STUDIO_CSS
    assert '#searchSection .studio-smart-search-help-panel :is(code,code.md-inline-code)' in STUDIO_CSS
