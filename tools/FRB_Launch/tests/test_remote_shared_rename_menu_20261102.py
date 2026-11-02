"""Remote / Files Exp shared Rename regression tests (no PySide6 dependency).

Actual Windows popups, sizing and edit focus remain manual acceptance checks.
"""
import ast
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_actions import rename_file_or_folder
from context_menu_config import load_context_menus, visible_context_entries
from file_transfer_visual import path_key

APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')


def node(source, cls, method):
    klass = next(n for n in ast.parse(source).body
                 if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == method)


def method(source, cls, name, ns):
    env = dict(ns)
    exec(textwrap.dedent(ast.get_source_segment(source, node(source, cls, name))), env)
    return env[name]


def test_inline_editor_matches_tree_row_font_not_global_lineedit_font():
    klass = next(n for n in ast.parse(EXP).body
                 if isinstance(n, ast.ClassDef) and n.name == 'FilesExpRenameDelegate')
    assert klass.bases[0].id == 'QStyledItemDelegate'
    assert 'editor.setFont(option.font)' in EXP
    assert 'QFontInfo(option.font).pixelSize()' in EXP
    assert 'self.tree.setItemDelegate(FilesExpRenameDelegate(self.tree))' in EXP
    assert 'self.tree.setIndentation(18)' in EXP


def test_remote_blank_and_files_exp_share_exact_same_menu_definition():
    remote_blank = ast.get_source_segment(APP, node(APP, 'Launcher', 'show_remote_current_folder_menu'))
    exp_folder = ast.get_source_segment(APP, node(APP, 'Launcher', 'show_files_exp_folder_menu'))
    builder = ast.get_source_segment(APP, node(APP, 'Launcher', 'show_expanded_background_paste_menu'))
    assert 'show_expanded_background_paste_menu(' in remote_blank
    assert 'show_expanded_background_paste_menu(' in exp_folder
    assert 'visible_context_entries(definitions, folder_actions)' in builder
    assert "folder_actions.add('rename')" in builder
    assert 'files_exp_rename_target' not in builder.split('selected = visible_context_entries')[1].split('menu.setStyleSheet')[0]
    entries = load_context_menus(ROOT / 'config/context_menu_options.json')['folder']
    configured = [x['action_id'] for x in visible_context_entries(entries, {
        'open_explorer', 'open_terminal', 'copy_path', 'copy_cloud_link', 'rename', 'properties'
    }) if x.get('action_id')]
    assert configured[-2:] == ['rename', 'properties']


def test_folder_list_chevron_is_right_aligned_drawn_icon_not_text_suffix():
    builder = ast.get_source_segment(APP, node(APP, 'Launcher', 'show_expanded_background_paste_menu'))
    painter = ast.get_source_segment(APP, node(APP, 'RemoteFolderActionsMenu', 'paintEvent'))
    assert "menu.addAction('フォルダー・ファイルリスト')" in builder
    assert 'menu.folder_list_action = folder_list_action' in builder
    assert 'rect.right() - 15' in painter
    assert 'painter.fillPath(arrow, color)' in painter


def test_remote_cascade_calls_nonsearch_menu_and_dispatches_rename():
    source = ast.get_source_segment(APP, node(APP, 'RemoteFolderCascade', '_open_context_properties'))
    builder = ast.get_source_segment(APP, node(APP, 'Launcher', 'show_launch_context_menu'))
    assert 'force_search_context=False' in source
    assert "action_id == 'rename' and getattr(context_parent, 'remote_folder_navigation', False)" in builder
    assert 'self.rename_remote_cascade_entry(p, k)' in builder


def test_rename_file_in_remote_cascade_updates_disk_and_view(tmp_path):
    source = tmp_path / 'original.md'
    source.write_text('hi', encoding='utf-8')
    refresh = Mock()
    close = Mock()
    footer = Mock()
    view = NS(isVisible=lambda: True, current_directory=lambda: str(tmp_path),
              refresh_middle=refresh)
    fn = method(APP, 'Launcher', 'rename_remote_cascade_entry', {
        'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
        'QInputDialog': NS(getText=lambda *a, **k: ('changed.md', True)),
        'QTimer': NS(singleShot=lambda *a: None)})
    self = NS(close_remote_folder_menu=close, expanded_view=view,
              remote_window=None, footer=NS(setText=footer),
              file_index_settings={'enabled': False}, file_index_busy=False,
              error=Mock(), can_rename_remote_folder=lambda p: True)
    assert fn(self, str(source), 'file')
    assert not source.exists() and (tmp_path / 'changed.md').read_text() == 'hi'
    refresh.assert_called_once()
    close.assert_called_once()
    self.error.assert_not_called()


def test_rename_folder_in_remote_cascade_updates_breadcrumb_and_tree(tmp_path):
    folder = tmp_path / 'old'
    folder.mkdir()
    reflect = Mock()
    navigate = Mock()
    fn = method(APP, 'Launcher', 'rename_remote_cascade_entry', {
        'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
        'QInputDialog': NS(getText=lambda *a, **k: ('new', True)),
        'QTimer': NS(singleShot=lambda *a: None)})
    self = NS(close_remote_folder_menu=Mock(),
              remote_window=NS(files_exp_panel=NS(reflect_external_folder_rename=reflect)),
              can_rename_remote_folder=lambda p: True,
              on_files_exp_folder_renamed=navigate,
              file_index_settings={'enabled': False}, file_index_busy=False, error=Mock())
    assert fn(self, str(folder), 'folder')
    assert (tmp_path / 'new').is_dir() and not folder.exists()
    reflect.assert_called_once_with(folder, str(tmp_path / 'new'))
    navigate.assert_called_once_with(str(folder), str(tmp_path / 'new'))
    self.error.assert_not_called()


def test_cascade_rename_collision_keeps_original_and_reports_error(tmp_path):
    a, b = tmp_path / 'a', tmp_path / 'b'
    a.mkdir(); b.mkdir()
    fn = method(APP, 'Launcher', 'rename_remote_cascade_entry', {
        'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
        'QInputDialog': NS(getText=lambda *a, **k: ('b', True)),
        'QTimer': NS(singleShot=lambda *a: None)})
    self = NS(can_rename_remote_folder=lambda p: True, error=Mock())
    assert not fn(self, str(a), 'folder')
    assert a.is_dir() and b.is_dir()
    self.error.assert_called_once()


def test_rename_blank_menu_prefers_inline_if_selected_and_visible(tmp_path):
    folder = tmp_path / 'item'
    folder.mkdir()
    begin = Mock(return_value=True)
    panel = NS(isVisible=lambda: True, can_rename_folder=lambda p: True,
               begin_folder_rename=begin)
    fn = method(APP, 'Launcher', 'rename_remote_folder', {
        'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
        'QInputDialog': NS(getText=lambda *a, **k: (_ for _ in ()).throw(AssertionError('dialog should not show')))})
    holder = NS(remote_window=NS(files_exp_panel=panel),
                can_rename_remote_folder=lambda p: True)
    assert fn(holder, str(folder))
    begin.assert_called_once_with(str(folder))


def test_rename_current_remote_folder_dialog_when_no_exp_selection(tmp_path):
    folder = tmp_path / 'item'
    folder.mkdir()
    nav = Mock()
    fn = method(APP, 'Launcher', 'rename_remote_folder', {
        'Path': Path, 'rename_file_or_folder': rename_file_or_folder,
        'QInputDialog': NS(getText=lambda *a, **k: ('renamed', True))})
    holder = NS(remote_window=None, can_rename_remote_folder=lambda p: True,
                on_files_exp_folder_renamed=nav, error=Mock())
    assert fn(holder, str(folder))
    assert (tmp_path / 'renamed').is_dir()
    nav.assert_called_once_with(str(folder), str(tmp_path / 'renamed'))


def test_nonexistent_or_registered_root_cannot_be_renamed(tmp_path):
    dir0 = tmp_path / 'root'; dir0.mkdir()
    child = dir0 / 'child'; child.mkdir()
    def rows():
        return [{'item_kind': 'directory', 'title': 'Root', 'launch_browse_target': str(dir0)}]
    fn = method(APP, 'Launcher', 'can_rename_remote_folder', {'Path': Path, 'path_key': path_key})
    holder = NS(_remote_files_first_column_rows=rows,
                expander=lambda: NS(expand=lambda s: s))
    assert fn(holder, str(dir0)) is False
    assert fn(holder, str(child)) is True
    assert fn(holder, str(dir0 / 'missing')) is False
