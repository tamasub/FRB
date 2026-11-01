"""v81: normal Browser Bookmarks shares Remote's new/current-tab semantics.

Qt-free executable contracts cover the real routing methods.  The two
PySide6 buttons and their QSS are additionally source-checked in CI.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from webview_routes import bookmark_web_url
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def method(src, cls, name, scope=None):
    parsed = ast.parse(src)
    klass = next(v for v in parsed.body if isinstance(v, ast.ClassDef) and v.name == cls)
    node = next(v for v in klass.body if isinstance(v, ast.FunctionDef) and v.name == name)
    env = dict(scope or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<v81>', 'exec'), env)
    return env[name]


class Button:
    def __init__(self):
        self.checked = None
        self.text = None
        self.tooltip = None

    def setChecked(self, checked): self.checked = checked
    def setText(self, text): self.text = text
    def setToolTip(self, tooltip): self.tooltip = tooltip


def test_segmented_buttons_are_mutually_exclusive_and_announce_the_target():
    view = NS(bookmark_new_tab_button=Button(), bookmark_current_tab_button=Button())
    choose = method(EXP, 'ExpandedLauncherView', 'select_bookmark_tab')
    choose(view, True)
    assert view.bookmark_new_tab is True
    assert view.bookmark_new_tab_button.checked and not view.bookmark_current_tab_button.checked
    assert view.bookmark_new_tab_button.text == '✓ 新規タブ'
    assert view.bookmark_current_tab_button.text == 'カレントタブ'
    choose(view, False)
    assert view.bookmark_new_tab is False
    assert view.bookmark_current_tab_button.checked and not view.bookmark_new_tab_button.checked
    assert view.bookmark_current_tab_button.text == '✓ カレントタブ'
    assert view.bookmark_current_tab_button.tooltip == '選択中：カレントタブ'


def bookmark(url='https://example.org/frb'):
    return {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': url,
         'launch_browser': 'chrome', 'launch_browser_profile': 'Default'}]}


def test_first_column_click_uses_new_tab_and_current_tab():
    choose = method(EXP, 'ExpandedLauncherView', 'choose_bookmark',
                    {'bookmark_web_url': bookmark_web_url})
    for new_tab, expected in ((True, {'new_tab': True}), (False, {})):
        row = bookmark()
        web = Mock(return_value=True)
        view = NS(bookmark_new_tab=new_tab,
                  row_data=lambda _: row, is_bookmark_row=lambda _: True,
                  _web_selection_timer=NS(stop=Mock()),
                  show_web_url=web, launcher=NS(open_target=Mock()))
        choose(view, object(), 0)
        web.assert_called_once_with('https://example.org/frb', **expected)
        view.launcher.open_target.assert_not_called()


def test_nested_cascade_uses_same_destination_as_first_column():
    route = method(APP, 'Launcher', 'open_bookmark_web_view',
                   {'bookmark_web_url': bookmark_web_url})
    for new_tab, expected in ((True, {'new_tab': True}), (False, {})):
        web = Mock(return_value=True)
        view = NS(bookmark_new_tab=new_tab, isVisible=Mock(return_value=True),
                  is_bookmark_row=Mock(return_value=True), show_web_url=web)
        launcher = NS(webview_settings={'mode': 'embedded'}, expanded_view=view)
        assert route(launcher, bookmark()) is True
        web.assert_called_once_with('https://example.org/frb', **expected)


def test_external_or_unrelated_action_does_not_open_embedded_tab():
    route = method(APP, 'Launcher', 'open_bookmark_web_view',
                   {'bookmark_web_url': bookmark_web_url})
    web = Mock()
    view = NS(bookmark_new_tab=True, isVisible=lambda: True,
              is_bookmark_row=lambda _: True, show_web_url=web)
    launcher = NS(webview_settings={'mode': 'external'}, expanded_view=view)
    assert route(launcher, bookmark()) is False
    launcher.webview_settings['mode'] = 'embedded'
    assert route(launcher, {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Run', 'launch_target': 'cmd.exe'}]}) is False
    web.assert_not_called()


def test_normal_bookmark_ui_below_header_and_not_in_file_workspace():
    assert 'self.bookmark_new_tab = True' in EXP
    assert "QPushButton('新規タブ', self.bookmark_tab_target_bar)" in EXP
    assert "QPushButton('カレントタブ', self.bookmark_tab_target_bar)" in EXP
    assert 'self.right.layout_box.insertWidget(1, self.bookmark_tab_target_bar)' in EXP
    assert "self.launcher.webview_settings.get('mode') == 'embedded'" in EXP
    assert 'self.select_bookmark_tab(True)' in EXP
    assert 'Qt.FocusPolicy.NoFocus' in EXP
    assert 'QPushButton#expandedBookmarkTabChoice:checked' in EXP
    assert "'#d6e7f8' if light else '#345d7a'" in EXP
    assert 'self.right.hide()  # Bookmarks belong to Browser, never Files.' in EXP


def test_remote_browser_has_its_own_independent_destination():
    assert 'menu.remote_bookmark_new_tab = True' in APP
    assert "new_tab = getattr(root, 'remote_bookmark_new_tab', True)" in APP
    assert 'show_web_url(url, new_tab=new_tab)' in APP
