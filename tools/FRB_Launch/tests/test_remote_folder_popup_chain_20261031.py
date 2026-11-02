"""Regression: the Remote folder browser augments the existing blank menu.

These headless contract tests intentionally avoid a PySide6 dependency. The
Windows Qt submenu crossing must also be verified manually in the app.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1] / 'src'
APP = (ROOT / 'app.py').read_text(encoding='utf-8')
FOLDER = (ROOT / 'remote_folder_menu.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'launch_remote.py').read_text(encoding='utf-8')


def _method(source, cls, name, ns):
    tree = ast.parse(source)
    cls_node = next(node for node in tree.body
                    if isinstance(node, ast.ClassDef) and node.name == cls)
    func = next(node for node in cls_node.body
                if isinstance(node, ast.FunctionDef) and node.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])),
                 '<test-extracted-method>', 'exec'), ns)
    return ns[name]


def test_hover_children_use_shared_compact_tool_window_semantics():
    # The former native QMenu chain swallowed mouse clicks. Reuse the tool
    # popup engine from Compact, which already supports file contexts.
    body = ast.parse(APP)
    menu_class = next(node for node in body.body if isinstance(node, ast.ClassDef)
                      and node.name == 'RemoteFolderCascade')
    assert isinstance(menu_class.bases[0], ast.Name)
    assert menu_class.bases[0].id == 'CascadeMenu'
    assert "RemoteFolderCascade if getattr(m, 'remote_folder_navigation', False)" in APP


def test_band_keeps_new_command_while_original_menu_builder_is_reused():
    assert "self.command.emit('REMOTE_CURRENT_FOLDER_MENU')" in REMOTE
    show = _method(APP, 'Launcher', 'show_remote_current_folder_menu',
                   {'Path': Path, 'QCursor': SimpleNamespace(pos=lambda: 'pointer')})
    launcher = SimpleNamespace(
        remote_window=SimpleNamespace(isVisible=lambda: True),
        expanded_view=SimpleNamespace(isVisible=lambda: True,
                                      _workspace_mode='files',
                                      current_directory=lambda: str(ROOT)),
        close_remote_folder_menu=Mock(),
        show_expanded_background_paste_menu=Mock())
    show(launcher)
    launcher.close_remote_folder_menu.assert_called_once()
    launcher.show_expanded_background_paste_menu.assert_called_once_with(
        'pointer', remote_folder_list=True)


def test_background_menu_adds_shared_cascade_remote_before_existing_actions():
    method = next(node for node in next(node for node in ast.parse(APP).body
                   if isinstance(node, ast.ClassDef) and node.name == 'Launcher').body
                   if isinstance(node, ast.FunctionDef)
                   and node.name == 'show_expanded_background_paste_menu')
    assert 'remote_folder_list' in [arg.arg for arg in method.args.kwonlyargs]
    source = ast.get_source_segment(APP, method)
    assert 'self.expanded_view.add_lane_new_submenu(menu)' in source
    for action in ('open_explorer', 'open_terminal', 'copy_path',
                   'copy_cloud_link', 'properties'):
        assert action in source
    assert "RemoteFolderActionsMenu(parent=self, launcher=self) if remote_folder_list else QMenu(self)" in source
    assert "folder_list_action = menu.addAction('Filesリスト')" in source
    assert 'menu.openers[folder_list_action]' in source
    assert source.index("folder_list_action = menu.addAction") < source.index('self.expanded_view.add_lane_new_submenu(menu)')
    assert source.index("folder_list_action = menu.addAction") < source.index('folder_action.setIconVisibleInMenu(True)')


def test_existing_files_blank_command_remains_available():
    assert "if command == 'BACKGROUND_CONTEXT_MENU':" in APP
    assert 'self.show_expanded_background_paste_menu(QCursor.pos())' in APP


def test_remote_folder_click_refreshes_files_without_stealing_menu_focus():
    """Only the Remote popup entry point opts out of main-window focus."""
    import os
    method = _method((ROOT / 'expanded_view.py').read_text(encoding='utf-8'),
                     'ExpandedLauncherView', 'go_to_directory',
                     {'os': os, 'normalized_directory': str,
                      'directory_row': lambda p: {'title': p}})
    remote = SimpleNamespace(isVisible=lambda: True, set_area=Mock())
    launcher = SimpleNamespace(remote_window=remote,
                               remote_focus_area=Mock(), _remote_area='files')
    view = SimpleNamespace(path=[], refresh_middle=Mock(),
                           focus_panel=Mock(), middle=object(), launcher=launcher)
    assert method(view, str(ROOT), preserve_remote_popup=True)
    view.refresh_middle.assert_called_once()
    view.focus_panel.assert_not_called()
    launcher.remote_focus_area.assert_not_called()
    assert launcher._remote_area == 'directory'
    remote.set_area.assert_called_once_with('directory')

    view.refresh_middle.reset_mock()
    view.focus_panel.reset_mock()
    remote.set_area.reset_mock()
    assert method(view, str(ROOT))
    view.focus_panel.assert_called_once_with(view.middle)
    launcher.remote_focus_area.assert_called_once_with('directory')
    remote.set_area.assert_not_called()


def test_navigating_from_files_externally_closes_remote_folder_menu():
    method = _method(APP, 'Launcher', 'on_files_directory_changed', {'os': __import__('os')})
    launcher = SimpleNamespace(_remote_folder_root_menu=object(),
                               _remote_folder_source_path=__import__('os').path.normcase(
                                   __import__('os').path.normpath('/old')),
                               _remote_folder_navigation=False,
                               close_remote_folder_menu=Mock())
    method(launcher, '/new')
    launcher.close_remote_folder_menu.assert_called_once()
    launcher.close_remote_folder_menu.reset_mock()
    launcher._remote_folder_navigation = True
    method(launcher, '/next')
    launcher.close_remote_folder_menu.assert_not_called()
