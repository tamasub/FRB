"""Shared Compact/Remote filesystem engine regression tests, no Qt dependency.

Windows-specific QWidget popup positioning and actual event delivery still need
manual verification; these tests check all action dispatch boundaries in code.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(SOURCE)


def cls(name):
    return next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == name)


def method(klass, name, globals=None):
    node = next(n for n in cls(klass).body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(globals or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<extracted>', 'exec'), scope)
    return scope[name]


def test_compact_files_folder_hover_restored_even_if_files_pane_is_double_click():
    f = method('CascadeMenu', '_double_folder_mode')
    current = NS(launcher=NS(folder_open_mode='double'), compact_files_cascade=True)
    assert not f(current)
    normal = NS(launcher=NS(folder_open_mode='double'))
    assert f(normal)  # Non-Compact existing preference is unchanged.
    remote = NS(launcher=NS(folder_open_mode='double'), remote_folder_navigation=True)
    assert not f(remote)


def test_three_layer_compact_files_sets_flag_and_passes_it_to_children():
    launcher = method('Launcher', 'open_expanded_cascade')
    source = ast.get_source_segment(SOURCE, next(n for n in cls('Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'open_expanded_cascade'))
    assert 'self.menu.compact_files_cascade' in source
    fill = ast.get_source_segment(SOURCE, next(n for n in cls('Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'fill_cascade'))
    assert "m.child.compact_files_cascade = getattr(m, 'compact_files_cascade', False)" in fill
    assert "RemoteFolderCascade if getattr(m, 'remote_folder_navigation', False)" in fill
    assert "not getattr(menu, 'remote_folder_navigation', False)" in fill


def test_remote_and_compact_use_same_tool_column_engine():
    remote = cls('RemoteFolderCascade')
    assert isinstance(remote.bases[0], ast.Name)
    assert remote.bases[0].id == 'CascadeMenu'
    root_menu = ast.get_source_segment(SOURCE, next(n for n in cls('Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'show_expanded_background_paste_menu'))
    assert 'RemoteFolderActionsMenu(parent=self, launcher=self) if remote_folder_list else QMenu(self)' in root_menu
    assert "folder_list_action = menu.addAction('Filesリスト')" in root_menu
    assert 'self.expanded_view.add_lane_new_submenu(menu)' in root_menu
    assert "folder_actions.add('rename')" in root_menu


def test_remote_click_folder_commits_once_and_rebases_without_closing(tmp_path):
    folder = tmp_path / 'new'
    folder.mkdir()
    root = NS(_remote_rebase=Mock())
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              go_to_directory=Mock(return_value=True), current_directory=lambda: folder)
    launcher = NS(expanded_view=view, _remote_folder_root_menu=root,
                  _remote_folder_navigation=False, _remote_folder_commit_pending=False)
    current = NS(launcher=launcher, remote_folder_root=root)
    callback = method('RemoteFolderCascade', '_remote_commit_folder', {'Path': Path, 'os': os})
    callback(current, {'launch_browse_target': str(folder)})
    view.go_to_directory.assert_called_once_with(str(folder), preserve_remote_popup=True)
    root._remote_rebase.assert_not_called()  # The clicked parent column remains visible.
    assert not launcher._remote_folder_navigation
    assert not launcher._remote_folder_commit_pending


def test_remote_context_uses_regular_filesystem_menu_for_both_file_and_folder():
    context = NS(aboutToHide=NS(connect=Mock()))
    launcher = NS(isVisible=lambda: True, _launch_context_menu=context,
                  show_launch_context_menu=Mock(return_value=True))
    current = NS(launcher=launcher, _clear_context_highlight=Mock())
    callback = method('RemoteFolderCascade', '_open_context_properties')
    folder_row = {'item_kind':'directory', '_file':'C:/example'}
    callback(current, folder_row, (10, 20))
    launcher.show_launch_context_menu.assert_called_with(
        (10, 20), folder_row, context_parent=current, force_search_context=False)
    assert context.aboutToHide.connect.call_count == 1


def test_remote_file_click_is_select_only_and_double_click_executes():
    types = NS(LeftButton=1, RightButton=2)
    queue = []
    env = {'Qt': NS(MouseButton=types), 'QTimer': NS(singleShot=lambda _, f:queue.append(f))}
    press = method('RemoteFolderCascade', 'mousePressEvent', env)
    release = method('RemoteFolderCascade', 'mouseReleaseEvent', env)
    double = method('RemoteFolderCascade', 'mouseDoubleClickEvent', env)
    row = {'_file':'c:/tmp/example.txt', '_browse_file':'c:/tmp/example.txt', 'item_kind':'command'}
    action = NS(data=lambda: row)
    current = NS(_remote_entry=lambda a: row, _remote_pressed_action=None,
                 _remote_dbl_file=None, actionAt=lambda _:action, hover_timer=NS(stop=Mock()),
                 setActiveAction=Mock(), _remote_activate_file=Mock(), _remote_commit_folder=Mock())
    # Avoid base-class dispatch by supplying a valid row on each action.
    event = lambda: NS(button=lambda:1, position=lambda:NS(toPoint=lambda:(3,3)), accept=Mock())
    press(current, event()); release(current, event())
    assert not queue  # File single click does not execute.
    double(current, event()); release(current, event())
    assert len(queue) == 1
    queue.pop(0)()
    current._remote_activate_file.assert_called_once_with(row)


def test_remote_hover_keeps_existing_root_only_one_level_policy():
    source = ast.get_source_segment(SOURCE, next(n for n in cls('CascadeMenu').body
        if isinstance(n, ast.FunctionDef) and n.name == 'mouseMoveEvent'))
    assert "getattr(self, 'remote_folder_navigation', False)" in source
    assert "not self.hover_timer.isActive()" in source
    # Opening child menus uses exactly the same Compact openers and timing.
    assert 'self.hover_timer.start(int(self.launcher.data.get(' in source
