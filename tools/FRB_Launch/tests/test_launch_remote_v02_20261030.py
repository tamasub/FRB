"""FRB Remote v0.2 semantic navigation, popup routing and theme integration."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_navigation import next_area, previous_area
from launch_appearance import theme_palette


def method(name):
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    constants = SimpleNamespace(FocusReason=SimpleNamespace(OtherFocusReason=1))
    env = {'previous_area': previous_area, 'next_area': next_area,
           'Qt': constants, 'move_tree_selection': Mock(),
           'QTimer': SimpleNamespace(singleShot=lambda delay, callback: None),
           'windows': SimpleNamespace(raise_normal_window=Mock(return_value=True)),
           'next_wrapped': lambda rows, current, step: rows[(rows.index(current)+step) % len(rows)]
                    if current in rows else rows[0 if step > 0 else -1],
           'QAbstractItemView': SimpleNamespace(ScrollHint=SimpleNamespace(EnsureVisible=0)),
           'ROLE_KIND': 32}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'app.py', 'exec'), env)
    return env[name], env


def base_window():
    return SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
                           expanded_view=SimpleNamespace(isVisible=lambda: True),
                           _remote_area='directory', _remote_popup_area=None,
                           _last_focus_area='directory',
                           remote_window=SimpleNamespace(set_area=Mock()),
                           show_history_popup=Mock(), hide_history_popup=Mock(),
                           focus_search=Mock(), hide_remote=Mock(),
                           remote_focus_area=Mock(), raise_=Mock(),
                           activateWindow=Mock(), dismiss_on_outside_click=True,
                           winId=lambda: 765)


def test_tab_and_backtab_are_symmetric_and_wrap():
    for expanded in (True, False):
        for area in ('search', 'pages', 'directory' if expanded else 'list'):
            assert previous_area(next_area(area, expanded=expanded), expanded=expanded) == area
            assert next_area(previous_area(area, expanded=expanded), expanded=expanded) == area
    cmd, _ = method('remote_command')
    win = base_window()
    cmd(win, 'BACKTAB')
    win.remote_focus_area.assert_called_once_with('files')


def test_search_history_button_uses_existing_popup_and_can_toggle():
    cmd, _ = method('remote_command')
    win = base_window()
    win.history_popup = SimpleNamespace(isVisible=lambda: True)
    cmd(win, 'SEARCH_HISTORY')
    win.show_history_popup.assert_called_once()
    assert win._remote_popup_area == 'search_history'
    win.remote_window.set_area.assert_called_with('search_history')
    cmd(win, 'SEARCH_HISTORY')
    win.hide_history_popup.assert_called_once()
    assert win._remote_popup_area is None


def test_folder_history_is_only_available_when_breadcrumb_is_visible():
    cmd, _ = method('remote_command')
    win = base_window()
    view = win.expanded_view
    view.favorite_popup = SimpleNamespace(isVisible=lambda: True)
    view.toggle_directory_favorites = Mock()
    view.hide_favorite_popup = Mock()
    cmd(win, 'FOLDER_HISTORY')
    view.toggle_directory_favorites.assert_called_once()
    assert win._remote_popup_area == 'folder_history'
    cmd(win, 'FOLDER_HISTORY')
    view.hide_favorite_popup.assert_called_once()
    view.isVisible = lambda: False
    cmd(win, 'FOLDER_HISTORY')
    assert view.toggle_directory_favorites.call_count == 1


def test_history_wheel_moves_selection_without_sending_keys():
    fn, env = method('remote_history_command')
    a, b, c = [SimpleNamespace(name=n) for n in ('a','b','c')]
    current = [b]
    tree = SimpleNamespace(currentItem=lambda: current[0],
                           setCurrentItem=lambda item: current.__setitem__(0, item),
                           scrollToItem=Mock())
    win = base_window()
    win._remote_popup_area = 'search_history'
    win.history_popup = SimpleNamespace(isVisible=lambda: True)
    win.history_choices = tree
    win.history_visible_rows = lambda: [a,b,c]
    win.history_row_clicked = Mock()
    fn(win, 'DOWN')
    assert current[0] is c
    fn(win, 'UP')
    assert current[0] is b
    fn(win, 'ENTER')
    win.history_row_clicked.assert_called_once_with(b, 0)
    assert win.hide_remote.call_count == 0


def test_folder_history_selects_row_by_existing_safe_callback():
    fn, env = method('remote_history_command')
    item = SimpleNamespace()
    tree = SimpleNamespace(currentItem=lambda: item, scrollToItem=Mock())
    view = SimpleNamespace(favorite_popup=SimpleNamespace(isVisible=lambda: True),
                           favorite_choices=tree, directory_favorite_clicked=Mock(),
                           hide_favorite_popup=Mock())
    win = base_window()
    win._remote_popup_area = 'folder_history'
    win.expanded_view = view
    fn(win, 'ENTER')
    view.directory_favorite_clicked.assert_called_once_with(item, 0)
    fn(win, 'LEFT')
    view.hide_favorite_popup.assert_called_once()


def test_remote_style_uses_catalog_and_updates_on_theme_change():
    text = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
    app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    for identifier in ('light','dark'):
        colors = theme_palette(identifier)
        for key in ('panel','text','selection','muted_text'):
            assert colors[key].startswith('#')
    assert 'self.apply_theme(launcher.color_theme)' in text
    assert 'self.remote_window.apply_theme(self.color_theme)' in app
    for command in ('BACKTAB','SEARCH_HISTORY','FOLDER_HISTORY'):
        assert f"'{command}'" in text
    for forbidden in ('SendKeys(', 'SendInput(', 'QKeyEvent('):
        assert forbidden not in text


def test_search_button_restores_main_window_and_native_search_focus():
    cmd, env = method('remote_command')
    win = base_window()
    win.dismiss_on_outside_click = False
    cmd(win, 'SEARCH')
    win.hide_remote.assert_called_once()
    win.raise_.assert_called_once()
    env['windows'].raise_normal_window.assert_called_once_with(765)
    win.activateWindow.assert_called_once()
    win.focus_search.assert_called_once()


def test_home_button_navigates_home_and_returns_remote_to_primary_area():
    cmd, _ = method('remote_command')
    view = SimpleNamespace(isVisible=lambda: True,
                           hide_favorite_popup=Mock(),
                           favorite_popup=SimpleNamespace(isVisible=lambda: False),
                           toggle_directory_favorites=Mock())
    win = base_window()
    win.expanded_view = view
    win.navigate_home = Mock()
    win._remote_popup_area = 'search_history'
    cmd(win, 'HOME')
    win.hide_history_popup.assert_called_once()
    win.navigate_home.assert_called_once()
    win.remote_focus_area.assert_called_once_with('roots')
    assert win._remote_popup_area is None
