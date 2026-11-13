"""FRB Launch release-menu behavior; no PySide6 needed for contract logic."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text('utf-8')
ROD = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')


def method(name):
    launcher = next(x for x in ast.parse(APP).body
                    if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    fn = next(x for x in launcher.body
              if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'app.py', 'exec'), ns)
    return ns[name]


class FakeLauncher:
    _sync_mouse_pointer_rod_menu = method('_sync_mouse_pointer_rod_menu')
    select_mouse_pointer_rod_choice = method('select_mouse_pointer_rod_choice')
    set_mouse_pointer_rod_mode = method('set_mouse_pointer_rod_mode')
    set_mouse_pointer_rod_windows_mode = method('set_mouse_pointer_rod_windows_mode')
    set_mouse_pointer_rod_smart_mode = method('set_mouse_pointer_rod_smart_mode')

    def __init__(self, enabled=False, windows=False, smart=False):
        self.mouse_pointer_rod_mode = enabled
        self.mouse_pointer_rod_windows_mode = windows
        self.mouse_pointer_rod_smart_mode = smart
        self.saved = {}
        self.settings = NS(setValue=lambda k, v: self.saved.__setitem__(k, v), sync=Mock())
        self.remote_window = NS(
            set_mouse_pointer_rod_enabled=Mock(),
            set_mouse_pointer_rod_windows_mode=Mock(),
            set_mouse_pointer_rod_smart_mode=Mock())
        self.footer = NS(setText=Mock())
        self.mouse_pointer_rod_choice_actions = {
            key: NS(setChecked=Mock()) for key in ('off', 'direct', 'windows')}
        self.mouse_pointer_rod_smart_action = None


def test_public_labels_are_plain_and_meaningful():
    assert "'Launchを隠す'" in APP
    assert "'Files Listでフォルダーを開く操作'" in APP
    assert "'シングルクリック'" in APP
    assert "'リモコンウィンドウを1.5列に表示'" in APP
    assert "self.mouse_pointer_rod_menu = self.theme_menu.addMenu(" in APP
    assert "'ワープ差し棒 ～ぐりぐりスピナー～（上下追従）'" in APP
    assert "'使用しない'" in APP
    assert "'Files List / Exp を直接選択'" in APP
    assert "'Windowsマウス方式'" in APP
    assert "'ワープ差し棒 ～ぐりぐりスピナー～（上下追従）'" in APP
    for text in ('（従来）', '実験：'):
        assert text not in APP
    assert '  実験' not in ROD
    assert 'Windows実験：' not in ROD


def test_choice_exclusivity_and_persistence():
    app = FakeLauncher()
    app.select_mouse_pointer_rod_choice('direct')
    assert (app.mouse_pointer_rod_mode, app.mouse_pointer_rod_windows_mode) == (True, False)
    assert app.saved['experiment_mouse_pointer_rod'] is True
    assert app.saved['experiment_mouse_pointer_rod_smart'] is True
    app.remote_window.set_mouse_pointer_rod_enabled.assert_called_with(True)
    app.mouse_pointer_rod_choice_actions['direct'].setChecked.assert_called_with(True)
    app.select_mouse_pointer_rod_choice('windows')
    assert (app.mouse_pointer_rod_mode, app.mouse_pointer_rod_windows_mode) == (True, True)
    assert app.saved['experiment_mouse_pointer_rod_windows'] is True
    app.remote_window.set_mouse_pointer_rod_windows_mode.assert_called_with(True)
    app.mouse_pointer_rod_choice_actions['windows'].setChecked.assert_called_with(True)
    app.select_mouse_pointer_rod_choice('off')
    assert (app.mouse_pointer_rod_mode, app.mouse_pointer_rod_windows_mode) == (False, False)
    app.remote_window.set_mouse_pointer_rod_enabled.assert_called_with(False)
    app.mouse_pointer_rod_choice_actions['off'].setChecked.assert_called_with(True)
    assert app.mouse_pointer_rod_smart_action is None


def test_existing_settings_are_preserved_and_warp_remains_separate():
    app = FakeLauncher(enabled=True, windows=True, smart=True)
    app._sync_mouse_pointer_rod_menu()
    app.mouse_pointer_rod_choice_actions['windows'].setChecked.assert_called_with(True)
    assert app.mouse_pointer_rod_smart_mode is True
    app.select_mouse_pointer_rod_choice('off')
    assert app.mouse_pointer_rod_smart_mode is True
    app.select_mouse_pointer_rod_choice('direct')
    assert app.mouse_pointer_rod_smart_mode is True
    assert app.mouse_pointer_rod_smart_mode is True
    app.select_mouse_pointer_rod_choice('windows')
    app.select_mouse_pointer_rod_choice('direct')
    assert app.saved['experiment_mouse_pointer_rod_windows'] is False
    app.select_mouse_pointer_rod_choice('bogus')
    assert (app.mouse_pointer_rod_mode, app.mouse_pointer_rod_windows_mode) == (True, False)


def test_internal_warp_setter_does_not_alter_click_adapter():
    app = FakeLauncher(enabled=True, windows=True)
    app.set_mouse_pointer_rod_smart_mode(True)
    assert app.mouse_pointer_rod_smart_mode is True
    assert (app.mouse_pointer_rod_mode, app.mouse_pointer_rod_windows_mode) == (True, True)
    assert app.saved == {'experiment_mouse_pointer_rod_smart': True}
    app.remote_window.set_mouse_pointer_rod_smart_mode.assert_called_once_with(True)


def test_submenu_wiring_and_old_keys_not_migrated():
    assert 'self.mouse_pointer_rod_choice_group.setExclusive(True)' in APP
    assert 'self.select_mouse_pointer_rod_choice(key)' in APP
    for key in ('experiment_mouse_pointer_rod', 'experiment_mouse_pointer_rod_windows',
                'experiment_mouse_pointer_rod_smart'):
        assert repr(key) in APP
    # Windows-click and Y-follow remain separate internal values, not menu controls.
    assert 'self.mouse_pointer_rod_smart_action = None' in APP
    assert 'self.mouse_pointer_rod_smart_action.triggered.connect(' not in APP
