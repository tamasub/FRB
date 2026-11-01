"""Filesystem roots remain read-only and follow the Files first column."""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_files_exp_roots import registered_folder_roots, subdirectories


def test_matches_rendered_first_column_order_and_labels_without_deduplication():
    rows = [
        {'title': 'PC', 'item_kind': 'category', '_system_drives_root': True},
        {'title': 'ダウンロード', 'item_kind': 'directory',
         'launch_browse_target': '%USERPROFILE%\\Downloads'},
        {'title': 'もう一つの入口', 'item_kind': 'directory',
         'launch_browse_target': '%USERPROFILE%\\Downloads'},
        {'title': 'No Folder', 'item_kind': 'command', 'launch_browse_target': 'C:\\'},
        {'title': 'Category', 'item_kind': 'category'},
    ]
    expanded = lambda value: value.replace('%USERPROFILE%', 'C:\\Users\\Me')
    result = registered_folder_roots(rows, expanded)
    assert [row['label'] for row in result] == ['PC', 'ダウンロード', 'もう一つの入口']
    assert result[0] == {'label': 'PC', 'path': None, 'pc': True}
    assert result[1]['path'] == result[2]['path'] == 'C:\\Users\\Me\\Downloads'


def test_blank_invalid_and_failing_expand_are_ignored():
    rows = [
        {'item_kind': 'directory', 'title': 'Empty', 'launch_browse_target': ''},
        {'item_kind': 'directory', 'title': 'Wrong', 'launch_browse_target': None},
        {'item_kind': 'directory', 'title': 'Bad', 'launch_browse_target': '%bad%'},
        {'item_kind': 'directory', 'title': 'Good', 'launch_browse_target': '/tmp'},
    ]
    def expander(value):
        if value == '%bad%':
            raise ValueError('unsupported')
        return value
    assert registered_folder_roots(rows, expander) == [
        {'label': 'Good', 'path': '/tmp', 'pc': False}]


def test_subdirectories_only_enumerates_immediate_directories_sorted(tmp_path):
    (tmp_path / 'Zeta').mkdir()
    (tmp_path / 'alpha').mkdir()
    (tmp_path / 'A_file.md').write_text('content', encoding='utf-8')
    (tmp_path / 'alpha' / 'nested').mkdir()
    assert subdirectories(str(tmp_path)) == [
        ('alpha', str(tmp_path / 'alpha')),
        ('Zeta', str(tmp_path / 'Zeta')),
    ]
    assert subdirectories(str(tmp_path / 'alpha')) == [
        ('nested', str(tmp_path / 'alpha' / 'nested'))]


def test_missing_and_unreadable_directories_are_safe(tmp_path):
    assert subdirectories(str(tmp_path / 'missing')) == []
    assert subdirectories('') == []


def test_files_preview_does_not_write_or_navigate():
    src = (ROOT / 'src' / 'remote_files_explorer.py').read_text('utf-8')
    ast.parse(src)
    for forbidden in ('go_to_directory(', 'set_current_directory(',
                      'os.remove(', 'os.rename(', 'subprocess.', 'shutil.',
                      'self.tree.setDragDropMode('):
        assert forbidden not in src
    assert 'launcher._remote_files_first_column_rows()' in (
        ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
    assert 'launcher.expander().expand' in (
        ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
