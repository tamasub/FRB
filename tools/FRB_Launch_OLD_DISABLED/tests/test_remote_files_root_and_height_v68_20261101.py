"""v68: Files-button roots reflect the real Files pane; Remote popup reach tripled.

These headless checks cover routing, state transitions and geometry. Actual
Windows/Qt repaint, hover, row popup placement still need manual validation.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(APP)


def method(klass, name, env=None):
    cls = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == klass)
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<extracted>', 'exec'), scope)
    return scope[name]


def source(klass, name):
    cls = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == klass)
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(APP, node)


def test_first_column_rows_are_exact_rendered_files_column_one_not_current_folder():
    roots = [{'title': 'PC', 'item_kind': 'category', '_system_drives_root': True},
             {'title': 'Downloads', 'item_kind': 'directory', 'launch_browse_target': 'C:/Users/Example/Downloads'},
             {'title': 'FRB Root', 'item_kind': 'directory', 'launch_browse_target': 'F:/FRB'}]
    tree = NS(topLevelItemCount=lambda: len(roots), topLevelItem=lambda i: roots[i])
    view = NS(left=NS(tree=tree), row_data=lambda item: item,
              current_directory=lambda: 'F:/FRB/Launch/src')
    fn = method('Launcher', '_remote_files_first_column_rows')
    assert fn(NS(expanded_view=view)) == roots
    assert roots[0]['_system_drives_root']
    fill = source('Launcher', 'fill_cascade')
    assert "parent.get('launch_source') == 'remote_files_roots'" in fill
    assert 'rows = self._remote_files_first_column_rows()' in fill
    assert "parent.get('_system_drives_root')" in fill
    assert 'rows = self.expanded_view.browser_rows(parent)' in fill


def test_regular_remote_folder_popup_keeps_its_current_folder_mode():
    fill = source('Launcher', 'fill_cascade')
    assert 'rows = self.displayed_children(parent)' in fill
    assert "self.fill_cascade(child, self._remote_folder_context(directory))" in source('Launcher', '_open_remote_folder_cascade')
    blank = source('Launcher', 'show_expanded_background_paste_menu')
    assert "folder_list_action = menu.addAction('Filesリスト')" in blank


def test_native_root_shortcut_folder_is_a_navigation_entry_without_private_file_marker():
    fn = method('RemoteFolderCascade', '_remote_entry')
    folder = {'item_kind': 'directory', 'launch_browse_target': '%USERPROFILE%\\Downloads'}
    assert fn(None, NS(data=lambda: folder)) is folder
    assert fn(None, NS(data=lambda: {'item_kind': 'category', '_system_drives_root': True})) is None
    assert fn(None, NS(data=lambda: {'item_kind': 'command', 'launch_browse_target': 'shell:Downloads'})) is None


def test_root_commit_preserves_first_column_while_blank_commit_rebases(tmp_path):
    directory = tmp_path / 'test-directory'
    directory.mkdir()
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              current_directory=lambda: directory, go_to_directory=Mock(return_value=True))
    root = NS(remote_files_roots=True, _remote_rebase=Mock())
    launcher = NS(expanded_view=view, _remote_folder_root_menu=root,
                  _remote_folder_navigation=False, _remote_folder_commit_pending=False)
    fn = method('RemoteFolderCascade', '_remote_commit_folder', {'Path': Path, 'os': os})
    fn(NS(launcher=launcher, remote_folder_root=root),
       {'item_kind': 'directory', 'launch_browse_target': str(directory)})
    view.go_to_directory.assert_called_once_with(str(directory), preserve_remote_popup=True)
    root._remote_rebase.assert_not_called()
    assert not launcher._remote_folder_navigation
    assert not launcher._remote_folder_commit_pending
    root.remote_files_roots = False
    fn(NS(launcher=launcher, remote_folder_root=root),
       {'item_kind': 'directory', 'launch_browse_target': str(directory)})
    root._remote_rebase.assert_not_called()  # Nested navigation opens to the right.


def test_click_root_switches_breadcrumb_and_opens_its_child_without_prior_hover(tmp_path):
    folder = tmp_path / 'sub'
    folder.mkdir()
    selected = object()
    opener = Mock()
    root = NS(remote_files_roots=True, _remote_rebase=Mock(),
              activeAction=lambda: selected, openers={selected: opener}, child=None)
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              current_directory=lambda: folder, go_to_directory=Mock(return_value=True))
    launcher = NS(expanded_view=view, _remote_folder_root_menu=root,
                  _remote_folder_navigation=False, _remote_folder_commit_pending=False)
    fn = method('RemoteFolderCascade', '_remote_commit_folder', {'Path': Path, 'os': os})
    # ``self is root`` matters for first-column click handling.
    root.launcher = launcher
    root.remote_folder_root = root
    fn(root, {'item_kind': 'directory', 'launch_browse_target': str(folder)})
    opener.assert_called_once_with('keyboard')
    root._remote_rebase.assert_not_called()
    view.go_to_directory.assert_called_once()


def test_files_root_popup_keeps_category_clicks_open_instead_of_dismissing():
    for name in ('mouseReleaseEvent', 'mouseDoubleClickEvent'):
        assert "getattr(self, 'remote_files_roots', False)" in source('CascadeMenu', name)
    # Child inherits the same Remote navigation engine and root pointer.
    fill = source('Launcher', 'fill_cascade')
    assert "RemoteFolderCascade if getattr(m, 'remote_folder_navigation', False)" in fill
    assert 'm.child.remote_folder_root = m.remote_folder_root or m' in fill


def test_bounds_triple_available_reach_and_clamp_to_actual_screen():
    fn = method('Launcher', '_remote_popup_vertical_bounds', {'QPoint': lambda x, y: (x, y)})
    remote = NS(isVisible=lambda: True,
                files_button=NS(mapToGlobal=lambda p: NS(y=lambda: 150)),
                mapToGlobal=lambda p: NS(y=lambda: 350), height=lambda: 350)
    top, bottom = fn(NS(remote_window=remote))
    # Files line 149, previous footer bottom 350, now spans 3x as far.
    assert (top, bottom) == (149, 149 + 3*(350-149))
    popup = source('CascadeMenu', 'popup')
    assert 'bound_top = max(rect.top(), bound_top)' in popup
    assert 'min(rect.bottom() + 1, bound_bottom)' in popup
    assert 'self._enable_scroll_tree(placement.height)' in popup
    assert "if hasattr(m, 'remote_popup_bounds'):" in source('Launcher','fill_cascade')
