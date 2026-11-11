"""Settings → バージョン情報: pure contracts, GUI integration mocked.

Works without PySide6, so this remains runnable on non-Windows builders.
The final real Remote wheel input needs Windows GUI acceptance.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from app_version import APP_NAME, APP_VERSION, APP_PROJECT, APP_ABOUT_TEXT

APP = (ROOT / 'src' / 'app.py').read_text('utf-8')
CONFIRM = (ROOT / 'src' / 'remote_confirmation.py').read_text('utf-8')


def method(name):
    launcher = next(x for x in ast.parse(APP).body
                    if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    fn = next(x for x in launcher.body
              if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = {'APP_ABOUT_TEXT': APP_ABOUT_TEXT, 'APP_VERSION': APP_VERSION,
          'QMessageBox': SimpleNamespace(StandardButton=SimpleNamespace(Yes=10)),
          'QApplication': SimpleNamespace(clipboard=lambda: clipboard)}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'app.py', 'exec'), ns)
    return ns[name]


clipboard = SimpleNamespace(setText=Mock())


def test_single_version_source_and_no_extra_catchphrase():
    assert APP_NAME == 'FRB Launch'
    assert APP_VERSION == '0.9.0'
    assert APP_PROJECT == 'FRB Project'
    assert APP_ABOUT_TEXT.splitlines() == [APP_NAME, 'Version 0.9.0', APP_PROJECT]
    assert 'Keyboard-first' not in APP_ABOUT_TEXT


def test_settings_menu_has_about_last_and_existing_studio_entry_preserved():
    index = APP.index("self.theme_studio_action = self.theme_menu.addAction('メニュー設定 (FRB Studio)')")
    assert index < APP.index("self.theme_about_action = self.theme_menu.addAction('バージョン情報...')")
    assert 'self.theme_about_action.triggered.connect(self.show_version_information)' in APP
    assert 'self.theme_menu.addSeparator()' in APP[index:APP.index('self.tabs = FocusPageTabBar()', index)]


def test_version_dialog_uses_existing_remote_confirmation_and_copies_on_request():
    launcher = SimpleNamespace(ask_remote_confirmation=Mock(return_value=10))
    method('show_version_information')(launcher)
    launcher.ask_remote_confirmation.assert_called_once_with(
        'バージョン情報', APP_ABOUT_TEXT,
        yes_text='バージョンをコピー', no_text='閉じる', information=True)
    clipboard.setText.assert_called_with('0.9.0')


def test_version_dialog_close_does_not_copy_or_change_settings():
    clipboard.setText.reset_mock()
    launcher = SimpleNamespace(ask_remote_confirmation=Mock(return_value=2))
    method('show_version_information')(launcher)
    clipboard.setText.assert_not_called()


def test_remote_selector_is_not_bypassed_for_about_dialog():
    assert 'information=information)' in APP
    assert 'QMessageBox.Icon.Information if information else' in CONFIRM
    assert 'self._remote_confirmation = confirmation' in APP
    assert 'confirmation.remote_command(command)' in APP
