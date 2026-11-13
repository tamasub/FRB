"""Settings → バージョン情報: menu lifetime and non-grabbing Qt.Tool regression.

Pure/mocked tests work without PySide6. Windows GUI must still accept the
actual Settings → About → Close/Copy → Tray Exit interaction.
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


class FakeTimer:
    callbacks = []

    @staticmethod
    def singleShot(delay, callback):
        assert delay == 0
        FakeTimer.callbacks.append(callback)


clipboard = SimpleNamespace(setText=Mock())


def method(name):
    launcher_class = next(x for x in ast.parse(APP).body
                          if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    fn = next(x for x in launcher_class.body
              if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = {'APP_ABOUT_TEXT': APP_ABOUT_TEXT, 'APP_VERSION': APP_VERSION,
          'QMessageBox': SimpleNamespace(StandardButton=SimpleNamespace(Yes=10)),
          'QApplication': SimpleNamespace(clipboard=lambda: clipboard),
          'QTimer': FakeTimer, 'QMenu': object}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'app.py', 'exec'), ns)
    return ns[name]


start_about = method('show_version_information')
finish_about = method('_show_version_information_after_menu_close')


def fake_launcher(result=2, children=None):
    """Track the ordering: menus must close before guard-bearing dialog."""
    events = []
    menu = SimpleNamespace(
        close=Mock(side_effect=lambda: events.append('menu.close')),
        hide=Mock(side_effect=lambda: events.append('menu.hide')),
        findChildren=Mock(return_value=children or []))
    launcher = SimpleNamespace(theme_menu=menu)
    def ask(*args, **kwargs):
        events.append('dialog.open')
        return result
    launcher.ask_remote_confirmation = Mock(side_effect=ask)
    launcher._show_version_information_after_menu_close = lambda: finish_about(launcher)
    FakeTimer.callbacks.clear()
    clipboard.setText.reset_mock()
    return launcher, events


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


def test_about_closes_settings_before_starting_input_guard_and_can_copy():
    child = SimpleNamespace(isVisible=lambda: True, close=Mock())
    launcher, events = fake_launcher(result=10, children=[child])
    start_about(launcher)
    assert events == ['menu.close', 'menu.hide']
    child.close.assert_called_once_with()
    assert launcher.ask_remote_confirmation.call_count == 0
    assert launcher._version_information_pending is True
    assert len(FakeTimer.callbacks) == 1
    FakeTimer.callbacks.pop()()
    assert events == ['menu.close', 'menu.hide', 'dialog.open']
    launcher.ask_remote_confirmation.assert_called_once_with(
        'バージョン情報', APP_ABOUT_TEXT,
        yes_text='バージョンをコピー', no_text='閉じる', information=True)
    clipboard.setText.assert_called_once_with('0.9.0')
    assert launcher._version_information_pending is False


def test_version_dialog_close_does_not_copy_or_change_settings():
    launcher, events = fake_launcher(result=2)
    start_about(launcher)
    FakeTimer.callbacks.pop()()
    assert events == ['menu.close', 'menu.hide', 'dialog.open']
    clipboard.setText.assert_not_called()
    assert launcher._version_information_pending is False


def test_repeat_trigger_does_not_schedule_multiple_dialogs():
    launcher, events = fake_launcher()
    start_about(launcher)
    start_about(launcher)
    assert len(FakeTimer.callbacks) == 1
    assert events == ['menu.close', 'menu.hide']
    FakeTimer.callbacks.pop()()
    assert launcher._version_information_pending is False


def test_pending_guard_clears_even_if_dialog_raises():
    launcher, events = fake_launcher()
    launcher.ask_remote_confirmation.side_effect = RuntimeError('dialog failed')
    start_about(launcher)
    try:
        FakeTimer.callbacks.pop()()
    except RuntimeError as exc:
        assert str(exc) == 'dialog failed'
    else:
        raise AssertionError('expected exception')
    assert launcher._version_information_pending is False


def test_remote_selector_is_not_bypassed_for_about_dialog():
    assert 'information=information)' in APP
    assert 'QMessageBox.Icon.Information if information else' in CONFIRM
    assert 'self._remote_confirmation = confirmation' in APP
    assert 'confirmation.remote_command(command)' in APP
    # Existing tray Exit remains bound to Launcher.quit, not About.
    assert "traymenu.addSeparator(); traymenu.addAction('終了', self.quit)" in APP
