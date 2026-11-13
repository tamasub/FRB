"""Six-point 2026-10-25 FRB Launch fix regression tests (no Qt required)."""
import ast
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import file_index
from context_menu_actions import sort_browser_entries
from filesystem_visibility import is_hidden_attribute

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf8')


def extract_method(name, scope):
    module = ast.parse(APP)
    launcher = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    target = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = dict(scope)
    exec(compile(ast.Module(body=[target], type_ignores=[]), str(ROOT / 'src/app.py'), 'exec'), scope)
    return scope[name]


def test_folder_only_index_excludes_files_and_excluded_subtrees(tmp_path):
    root = tmp_path / 'workspace'
    (root / 'project' / 'src').mkdir(parents=True)
    (root / 'project' / 'src' / 'main.py').write_text('test')
    (root / 'project' / 'readme.md').write_text('test')
    (root / 'build' / 'cache').mkdir(parents=True)
    options = file_index.load_options(tmp_path / 'not_there.json')
    options['index_target'] = 'folders'
    db = tmp_path / 'index.db'
    result = file_index.refresh_index(db, [str(root)], options)
    assert result['count'] == 3
    assert set(r['name'] for r in file_index.search_index(db, 'project')) == {'project', 'src'}
    assert file_index.search_index(db, 'readme.md') == []
    assert file_index.search_index(db, 'build') == []
    assert all(r['extension'] == '' for r in file_index.search_index(db, 'workspace'))
    # Changed index mode has its own digest and rebuilds the same root.
    assert file_index.refresh_index(db, [str(root)], options)['changed_roots'] == []
    old_mode = {**options, 'index_target': 'files'}
    assert file_index.refresh_index(db, [str(root)], old_mode)['changed_roots'] == [str(root)]
    assert file_index.search_index(db, 'readme.md')[0]['extension'] == '.md'
    assert file_index.refresh_index(db, [str(root)], options)['changed_roots'] == [str(root)]
    assert file_index.search_index(db, 'readme.md') == []


def test_hidden_attribute_filters_browser_and_index(tmp_path):
    root = tmp_path / 'root'
    (root / 'visible' / 'inside').mkdir(parents=True)
    (root / 'hidden' / 'secret').mkdir(parents=True)
    (root / 'visible' / 'hiddenchild').mkdir()
    (root / 'visible' / '.normal-dotfile').write_text('dot')
    (root / 'visible' / 'hidden.txt').write_text('hide')
    from filesystem_visibility import is_hidden_attribute as real_hidden
    def hidden(path):
        return Path(path).name in {'hidden', 'hiddenchild', 'hidden.txt'}
    # Module imports aliases at load time: inject into both callers.
    with patch('file_index.is_hidden_attribute', side_effect=hidden), patch('context_menu_actions.is_hidden_attribute', side_effect=hidden):
        options = file_index.load_options(tmp_path / 'missing.json')
        options['index_target'] = 'folders'
        db = tmp_path / 'idx.db'
        file_index.refresh_index(db, [str(root)], options)
        names = {x['name'] for x in file_index.search_index(db, str(root.name))}
        assert 'hidden' not in names
        assert 'hiddenchild' not in names
        assert 'secret' not in names
        assert 'inside' in names
        listed = [x.name for x in sort_browser_entries(root / 'visible')]
        assert 'hiddenchild' not in listed and 'hidden.txt' not in listed
        assert '.normal-dotfile' in listed
    with patch('file_index.is_hidden_attribute', side_effect=hidden):
        scanned = file_index._root_scan(str(root / 'hidden'), options)
        assert scanned['count'] == 0


def test_multi_selection_copy_path_and_name_are_newline_delimited(tmp_path):
    first, second = tmp_path / 'a.txt', tmp_path / 'folder'
    first.write_text('a');second.mkdir()
    clipboard = Mock()
    handler = extract_method('perform_filesystem_batch_action', {
        'Path': Path, 'QApplication': SimpleNamespace(clipboard=lambda: clipboard),
    })
    receiver = SimpleNamespace(_clear_previous_paste_feedback=Mock(),footer=Mock(),error=Mock())
    handler(receiver, 'copy_full_path', [first, second])
    clipboard.setText.assert_called_with(str(first) + '\n' + str(second))
    handler(receiver, 'copy_file_name', [first, second])
    clipboard.setText.assert_called_with('a.txt\nfolder')
    receiver.error.assert_not_called()


def test_single_delete_keeps_guard_until_after_modal_and_ui_refresh(tmp_path):
    path=tmp_path/'item.txt';path.write_text('temporary')
    callbacks=[]
    class Message:
        class StandardButton:
            Yes=1;No=2
        @staticmethod
        def question(*args):return 1
    handler=extract_method('perform_filesystem_context_action', {
        'Path':Path, 'QMessageBox':Message,
        'QTimer':SimpleNamespace(singleShot=lambda ms,fn:callbacks.append((ms,fn))),
        'move_to_recycle_bin':Mock(side_effect=lambda _:path.unlink()),
    })
    view=SimpleNamespace(isVisible=lambda:True, current_directory=lambda:str(tmp_path),refresh_middle=Mock())
    recipient=SimpleNamespace(
        error=Mock(),footer=Mock(),hover_timer=Mock(),
        _directory_menu_for_path=Mock(return_value=None),
        _launch_context_menu=None,expanded_view=view,
        file_index_settings={'enabled':False},file_index_busy=False,
        _clear_previous_paste_feedback=Mock())
    handler(recipient,'delete',str(path),'file')
    assert recipient._filesystem_dialog_depth==1
    assert [ms for ms,_ in callbacks]==[900,0]
    callbacks[1][1]();view.refresh_middle.assert_called_once()
    callbacks[0][1]();assert recipient._filesystem_dialog_depth==0


def test_config_and_context_menu_spacing():
    options=json.loads((ROOT/'config/file_index_options.json').read_text(encoding='utf8'))
    assert options['index_target']=='both'
    style=(ROOT/'src/launch_appearance.py').read_text(encoding='utf8')
    assert 'CONTEXT_MENU_SPACING_QSS' in style and 'margin-left:4px' in style
    assert "('copy_full_path', 'フルパスのコピー')" in APP
    assert "('copy_file_name', 'ファイル名のコピー')" in APP
    assert 'FrameEdgeCursorResetFilter' in APP


def test_windows_hidden_attribute_bit_without_hiding_dot_names():
    from types import SimpleNamespace
    with patch('filesystem_visibility.os.stat', return_value=SimpleNamespace(st_file_attributes=2)):
        assert is_hidden_attribute(r'C:\data\normal.txt')
    with patch('filesystem_visibility.os.stat', return_value=SimpleNamespace(st_file_attributes=0)):
        assert not is_hidden_attribute(r'C:\data\.visible-dotfile')
