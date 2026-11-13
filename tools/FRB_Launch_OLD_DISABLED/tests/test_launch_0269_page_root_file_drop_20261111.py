"""Page-root LIST accepts external files; Files Exp ROOT stays directory-only.

This regression uses real source functions, isolated from Qt by extracting the
pure drop handler methods. It does not mutate user config or real files.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import (RegistrationError, eligible_parent,
                                      normalize_sources, records_for_sources)
from launch_virtual_tree import virtual_item_identity, virtual_studio_target


def _extract_method(filename, name, symbols):
    source = (ROOT / 'src' / filename).read_text(encoding='utf-8')
    tree = ast.parse(source)
    match = next(method for cls in tree.body if isinstance(cls, ast.ClassDef)
                 for method in cls.body if isinstance(method, ast.FunctionDef)
                 and method.name == name)
    module = ast.fix_missing_locations(ast.Module(body=[match], type_ignores=[]))
    env = dict(symbols)
    exec(compile(module, filename, 'exec'), env)
    return env[name]


def _page():
    return {'source': 'launch_json', 'kind': 'page', 'page_id': 'testwk',
            'item_id': '', 'node_id': 'page:testwk', 'runtime_catalog': ''}


def _folder():
    return {'source': 'launch_json', 'kind': 'folder', 'page_id': 'testwk',
            'item_id': 'aaa', 'node_id': 'item:testwk:aaa',
            'row': {'item_kind': 'category'}, 'runtime_catalog': ''}


def test_list_blank_space_of_page_accepts_file_folder_and_url(tmp_path):
    file = tmp_path / 'test.bat'
    file.write_text('@echo off', encoding='utf-8')
    folder = tmp_path / 'a_folder'
    folder.mkdir()
    function = _extract_method('expanded_view.py', '_middle_launch_drop_target', {
        'mime_sources': lambda mime: mime,
        'virtual_item_identity': virtual_item_identity,
    })
    node = _page()
    view = SimpleNamespace(
        _virtual_directory_node=node, _workspace_mode='files',
        middle=SimpleNamespace(tree=SimpleNamespace(itemAt=lambda point: None)),
        row_data=lambda item: None,
    )
    for value in (str(file), str(folder), 'https://example.com/page'):
        assert function(view, None, [{'value': value}])['page_id'] == 'testwk'
        assert function(view, None, [{'value': value}])['item_id'] == ''
    view._virtual_directory_node = _folder()
    assert function(view, None, [{'value': str(file)}])['item_id'] == 'aaa'
    view._virtual_directory_node = {'source': 'filesystem', 'kind': 'folder'}
    assert function(view, None, [{'value': str(file)}]) is False


def test_registration_handler_accepts_files_at_page_root_but_not_exp_root(tmp_path):
    file = tmp_path / 'sample.xlsx'
    file.write_bytes(b'sample')
    folder = tmp_path / 'folder'
    folder.mkdir()
    errors, calls = [], []
    page = {'page_id': 'testwk', 'enabled': True}
    system_page = {'page_id': 'system', 'enabled': True}
    items = [
        {'page_id': 'testwk', 'item_id': 'aaa', 'enabled': True,
         'item_kind': 'category'},
        {'page_id': 'system', 'item_id': 'folders', 'enabled': True,
         'item_kind': 'category'},
    ]
    handler = _extract_method('app.py', 'handle_launch_drop', {
        'mime_sources': lambda mime: mime,
        'normalize_sources': normalize_sources,
        'virtual_studio_target': virtual_studio_target,
        'eligible_parent': eligible_parent,
        'records_for_sources': records_for_sources,
        'RegistrationError': RegistrationError,
    })
    launcher = SimpleNamespace(
        pages=[page, system_page], authored_items=items,
        _files_exp_root_registration_target=lambda: ('system', 'folders'),
        _registration_commit=lambda pg, parent, rows: calls.append((pg, parent, rows)) or True,
        error=errors.append,
    )
    identity = _page()
    assert handler(launcher, identity, [{'value': str(file)}])
    assert calls[-1][:2] == ('testwk', '')
    assert calls[-1][2][0]['item_kind'] == 'command'
    other = tmp_path / '二つ目のファイル.md'
    other.write_text('test', encoding='utf-8')
    assert handler(launcher, identity, [{'value': str(file)}, {'value': str(other)}])
    assert calls[-1][:2] == ('testwk', '')
    assert len(calls[-1][2]) == 2
    assert all(row['item_kind'] == 'command' for row in calls[-1][2])
    assert handler(launcher, identity, [{'value': 'https://example.com/page'}])
    assert calls[-1][:2] == ('testwk', '')
    assert handler(launcher, identity, [{'value': str(folder)}])
    assert calls[-1][:2] == ('testwk', '')
    assert handler(launcher, _folder(), [{'value': str(file)}])
    assert calls[-1][:2] == ('testwk', 'aaa')
    before = len(calls)
    assert not handler(launcher, None, [{'value': str(file)}])
    assert len(calls) == before
    assert 'ルートには既存フォルダーだけ' in errors[-1]
    assert handler(launcher, None, [{'value': str(folder)}])
    assert calls[-1][:2] == ('system', 'folders')
    assert not handler(launcher, {'source':'filesystem','page_id':'testwk'},
                       [{'value':str(file)}])
    assert len(errors) == 2
