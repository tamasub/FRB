"""v29: Remote ... exposes existing Launch settings/search+/breadcrumb heart.

Tests are AST-driven so they run on builders without the PySide6 GUI library.
Windows native popup positioning still needs a manual GUI smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def method(name):
    tree = ast.parse(APP)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                    and n.name == 'Launcher')
    node = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                and n.name == name)
    env = {'QTimer': SimpleNamespace(singleShot=lambda delay, cb: cb())}
    exec(compile(ast.fix_missing_locations(ast.Module([node], [])), 'app.py', 'exec'), env)
    return env[name]


def fixture(expanded=True, path='C:/Temp'):
    favorite = SimpleNamespace(isEnabled=lambda: bool(path), click=Mock(),
                               text=lambda: '💛')
    view = SimpleNamespace(isVisible=lambda: expanded,
                           current_directory=lambda: path,
                           favorite_save=favorite)
    remote = SimpleNamespace(more_button=object(), show_more_menu=Mock(),
                             set_favorite_action_available=Mock(),
                             update_more_menu_icons=Mock())
    window = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
                             remote_window=remote, expanded_view=view,
                             open_theme_menu_at=Mock(),
                             update_remote_more_menu=Mock(),
                             history_category_action=SimpleNamespace(trigger=Mock(), icon=Mock(return_value='plus-icon')),
                             theme_button=SimpleNamespace(icon=Mock(return_value='settings-icon')))
    return window


def test_header_more_button_and_three_actions_created_only_once():
    assert "self.more_button = self._button('…'" in REMOTE
    assert "head.addWidget(self.more_button)" in REMOTE
    assert 'self.more_menu = QMenu(self)' in REMOTE
    for label in ('設定', '検索履歴カテゴリーを追加', '現在のフォルダーをお気に入り登録'):
        assert f"addAction('{label}')" in REMOTE
    assert 'self.more_button.setFocusPolicy' not in REMOTE  # _button supplies NoFocus
    assert "'MORE_MENU'" in REMOTE
    assert 'self.more_menu.aboutToShow.connect(self.more_menu_opening.emit)' in REMOTE


def test_more_button_dispatch_opens_only_remote_menu():
    window = fixture()
    method('remote_command')(window, 'MORE_MENU')
    window.update_remote_more_menu.assert_called_once_with()
    window.remote_window.show_more_menu.assert_called_once_with()
    window.open_theme_menu_at.assert_not_called()


def test_setting_uses_existing_theme_menu_anchored_at_remote():
    window = fixture()
    method('remote_command')(window, 'REMOTE_SETTINGS')
    window.open_theme_menu_at.assert_called_once_with(window.remote_window.more_button)
    assert 'self.open_theme_menu_at(self.theme_button)' in APP
    assert 'self.theme_menu.popup(position)' in APP


def test_search_plus_uses_existing_category_action():
    window = fixture()
    method('remote_command')(window, 'REMOTE_CATEGORY_ADD')
    window.history_category_action.trigger.assert_called_once_with()
    assert 'self.history_category_action.triggered.connect(self.add_history_category)' in APP


def test_heart_uses_actual_breadcrumb_button_and_no_other_action():
    window = fixture(expanded=True, path='F:/FRB')
    method('remote_command')(window, 'REMOTE_FAVORITE_SAVE')
    window.expanded_view.favorite_save.click.assert_called_once_with()
    window = fixture(expanded=False)
    method('remote_command')(window, 'REMOTE_FAVORITE_SAVE')
    window.expanded_view.favorite_save.click.assert_not_called()
    window = fixture(path='')
    method('remote_command')(window, 'REMOTE_FAVORITE_SAVE')
    window.expanded_view.favorite_save.click.assert_not_called()
    assert 'self.favorite_save.clicked.connect(self.register_directory_favorite)' in (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_heart_disabled_when_no_valid_breadcrumb_path():
    update = method('update_remote_more_menu')
    enabled = fixture(expanded=True, path='F:/FRB')
    update(enabled)
    enabled.remote_window.set_favorite_action_available.assert_called_once_with(True)
    enabled.remote_window.update_more_menu_icons.assert_called_once_with('settings-icon', 'plus-icon', '💛')
    disabled = fixture(expanded=False, path='F:/FRB')
    update(disabled)
    disabled.remote_window.set_favorite_action_available.assert_called_once_with(False)
    absent = fixture(expanded=True, path='')
    update(absent)
    absent.remote_window.set_favorite_action_available.assert_called_once_with(False)


def test_remote_popup_is_clamped_near_more_button_and_uses_same_palette():
    assert 'self.more_button.mapToGlobal(' in REMOTE
    assert 'self.more_menu.popup(point)' in REMOTE
    assert "QMenu#remoteMoreMenu" in REMOTE
    assert "height=22, role='icon'" in REMOTE
    assert 'self.more_button.setObjectName(\'remoteMoreButton\')' in REMOTE
