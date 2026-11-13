"""v73 Remote ellipsis: Browser URL favorite delegates to existing address heart.

Qt-free regression coverage. Mouse hit-testing and QMenu painting require Windows.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def source_method(source, cls, name):
    tree = ast.parse(source)
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return node, ast.get_source_segment(source, node)


def method(source, cls, name, env=None):
    node, _ = source_method(source, cls, name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 f'<{cls}.{name}>', 'exec'), scope)
    return scope[name]


def test_browser_ellipsis_has_separate_address_favorite_and_existing_files_action():
    _, init = source_method(REMOTE, 'LaunchRemote', '__init__')
    assert "self.more_favorite_action = self.more_menu.addAction('現在のフォルダーをお気に入り登録')" in init
    assert "self.more_url_favorite_action = self.more_menu.addAction('現在のアドレスをお気に入り登録')" in init
    assert "self.command.emit('REMOTE_URL_FAVORITE_SAVE')" in init
    assert "self.command.emit('REMOTE_FAVORITE_SAVE')" in init
    assert 'self.more_menu.aboutToShow.connect(self.more_menu_opening.emit)' in init


def test_ellipsis_switches_visible_action_without_changing_files_menu():
    states = {name: [] for name in ('files', 'url', 'tab', 'category')}
    def action(name):
        return NS(setVisible=lambda value: states[name].append(value),
                  setEnabled=lambda value: None)
    menu = NS(more_favorite_action=action('files'),
              more_url_favorite_action=action('url'),
              more_new_tab_action=action('tab'),
              more_category_action=action('category'))
    fn = method(REMOTE, 'LaunchRemote', 'set_more_menu_mode')
    fn(menu, 'files')
    fn(menu, 'browser', can_add_tab=True)
    assert states['files'] == [True, False]
    assert states['url'] == [False, True]
    assert states['tab'] == [False, True]
    assert states['category'] == [True, False]


def test_browser_ellipsis_calls_same_heart_button_and_not_files_favorite():
    fn = method(APP, 'Launcher', 'remote_command')
    browser_heart = NS(isEnabled=lambda: True, click=Mock())
    files_heart = NS(isEnabled=lambda: True, click=Mock())
    view = NS(isVisible=lambda: True, _workspace_mode='browser',
              web_view_active=lambda: True,
              web_view=NS(favorite_save=browser_heart,
                          current_url_for_favorite=lambda: 'https://example.com/'),
              favorite_save=files_heart,
              current_directory=lambda: 'C:/projects')
    launcher = NS(isVisible=lambda: True, isMinimized=lambda: False,
                  expanded_view=view)
    fn(launcher, 'REMOTE_URL_FAVORITE_SAVE')
    browser_heart.click.assert_called_once_with()
    files_heart.click.assert_not_called()
    browser_heart.click.reset_mock()
    view._workspace_mode = 'files'
    fn(launcher, 'REMOTE_URL_FAVORITE_SAVE')
    browser_heart.click.assert_not_called()
    fn(launcher, 'REMOTE_FAVORITE_SAVE')
    files_heart.click.assert_called_once_with()


def test_browser_url_favorite_disabled_without_valid_live_page():
    fn = method(APP, 'Launcher', 'remote_command')
    heart = NS(isEnabled=lambda: True, click=Mock())
    view = NS(isVisible=lambda: True, _workspace_mode='browser',
              web_view_active=lambda: True,
              web_view=NS(favorite_save=heart,
                          current_url_for_favorite=lambda: ''))
    launcher = NS(isVisible=lambda: True, isMinimized=lambda: False,
                  expanded_view=view)
    fn(launcher, 'REMOTE_URL_FAVORITE_SAVE')
    heart.click.assert_not_called()
    view.web_view_active = lambda: False
    view.web_view.current_url_for_favorite = lambda: 'https://example.com/'
    fn(launcher, 'REMOTE_URL_FAVORITE_SAVE')
    heart.click.assert_not_called()


def test_browser_favorite_availability_is_refreshed_when_ellipsis_opens():
    fn = method(APP, 'Launcher', 'update_remote_more_menu')
    favorites = Mock()
    remote = NS(update_more_menu_icons=Mock(),
                set_favorite_action_available=Mock(),
                set_url_favorite_action_available=favorites,
                set_more_menu_mode=Mock())
    browser_heart = NS(isEnabled=lambda: True)
    view = NS(isVisible=lambda: True, _workspace_mode='browser',
              current_directory=lambda: 'F:/FRB',
              favorite_save=NS(isEnabled=lambda: True, text=lambda: '💛'),
              web_view_active=lambda: True,
              web_view=NS(favorite_save=browser_heart,
                          current_url_for_favorite=lambda: 'https://example.com/'))
    launcher = NS(remote_window=remote, expanded_view=view,
                  theme_button=NS(icon=lambda: 'settings-icon'),
                  history_category_action=NS(icon=lambda: 'category-icon'))
    fn(launcher)
    favorites.assert_called_once_with(True)
    remote.set_more_menu_mode.assert_called_once_with('browser', can_add_tab=True)
    favorites.reset_mock()
    view.web_view.current_url_for_favorite = lambda: ''
    fn(launcher)
    favorites.assert_called_once_with(False)


def test_browser_url_favorite_icon_uses_existing_gold_heart():
    _, icon_source = source_method(REMOTE, 'LaunchRemote', 'update_more_menu_icons')
    assert 'self.more_url_favorite_action.setIcon(remote_favorite_icon(favorite_heart))' in icon_source
    _, enabled = source_method(REMOTE, 'LaunchRemote', 'set_url_favorite_action_available')
    assert 'self.more_url_favorite_action.setEnabled(bool(available))' in enabled
