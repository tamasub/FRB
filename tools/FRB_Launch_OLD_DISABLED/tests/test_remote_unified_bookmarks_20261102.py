"""Regression contracts for 2026-11-02 Remote / Browser layout change.

GUI painting and Win32 activation still require the user's Windows machine.
"""
import ast
from pathlib import Path
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src'


def source(name):
    return (SRC / name).read_text(encoding='utf-8')


def method_body(file, klass, method):
    tree = ast.parse(source(file))
    owner = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == klass)
    func = next(x for x in owner.body if isinstance(x, ast.FunctionDef) and x.name == method)
    return ast.unparse(func)


def test_inline_exp_does_not_create_close_or_home_controls():
    code = method_body('remote_files_explorer.py', 'RemoteFilesExplorer', '__init__')
    assert 'if not self._embedded:' in code
    assert "close_button = QPushButton('×', header)" in code
    assert 'self.home_button.hide()' in code
    assert 'header_row.addWidget(close_button)' in code


def test_remote_files_exp_replaces_files_button_and_targets_workspace():
    code = method_body('launch_remote.py', 'LaunchRemote', '__init__')
    assert "'WORKSPACE_FILES', width=85" in code
    assert 'self.files_button = self.files_exp_button' in code
    assert 'row_workspaces.addWidget(self.files_exp_button)' in code
    assert "self._button('Files'," not in code
    assert 'root.addWidget(self.files_exp_button)' not in code


def test_remote_position_persisted_and_restored_in_every_mode():
    show = method_body('launch_remote.py', 'LaunchRemote', 'show_at')
    hide = method_body('launch_remote.py', 'LaunchRemote', 'hideEvent')
    assert "settings.value('remote_last_position')" in show
    assert 'QApplication.screenAt(point)' in show
    assert 'saved if isinstance(saved, QPoint)' in show
    assert "settings.setValue('remote_last_position', self.pos())" in hide
    # No invisible-mode switch or grid snap in the desktop-open path.
    assert 'align_with_files_grid' not in method_body('app.py', 'Launcher', 'show_remote_at')


def test_current_folder_hit_area_is_double_height_and_grey():
    assert 'self.setFixedHeight(46)' in method_body('launch_remote.py', 'UpDoubleClickBand', '__init__')
    assert 'border:1px solid #a5adb0' in source('launch_remote.py')
    assert 'REMOTE_FOLDER_DESELECT' in source('launch_remote.py')
    assert "self.command.emit('FOLDER_UP')" in source('launch_remote.py')


def test_remote_and_launch_use_same_outside_dismiss_flag():
    app_state = method_body('app.py', 'Launcher', 'app_state')
    assert "if getattr(self, 'dismiss_on_outside_click', True):" in app_state
    assert 'hide_remote()' in app_state
    flags = method_body('launch_remote.py', 'LaunchRemote', 'sync_window_mode')
    assert 'dismiss_on_outside_click' in flags
    assert 'Qt.WindowType.Window' in flags
    assert 'Qt.WindowType.Tool' in flags
    assert 'self.remote_window.sync_window_mode()' not in source('launch_web_view.py')


def test_bookmark_bar_is_shared_by_embedded_and_external_modes():
    view = source('expanded_view.py')
    web = source('launch_web_view.py')
    assert 'self.bookmark_strip = HorizontalBookmarkBar(self)' in web
    assert 'self._external_bookmark_strip = HorizontalBookmarkBar(self._browser_empty_page)' in view
    assert 'self.refresh_horizontal_bookmarks()' in view
    assert 'visible_bookmark_children(root, self.launcher.children)' in view
    assert 'new_tab=self.bookmark_new_tab' in method_body('expanded_view.py', 'ExpandedLauncherView', 'open_horizontal_bookmark')
    assert 'visible = False' in method_body('expanded_view.py', 'ExpandedLauncherView', 'set_browser_bookmarks_visible')


def test_nested_bookmark_folders_are_flattened_without_popups():
    # Updated contract: the horizontal strip is leaf-only and folder-menu-free.
    import sys
    sys.path.insert(0, str(SRC))
    from bookmark_bar_flatten import flatten_bookmark_rows
    root = {'item_id': 'r', 'title': 'root', 'item_kind': 'category'}
    folder = {'item_id': 'folder', 'title': 'Folder', 'item_kind': 'category'}
    url = {'item_id': 'url', 'title': 'Hello', 'item_kind': 'command'}
    child_map = {'r': [folder], 'folder': [root, url]}
    result = flatten_bookmark_rows([root], lambda row: child_map.get(row['item_id'], []))
    assert [row['title'] for row, _ in result] == ['Hello']
    assert result[0][1] == ('root', 'Folder')
