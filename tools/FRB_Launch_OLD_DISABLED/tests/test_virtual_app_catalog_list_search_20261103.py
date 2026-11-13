"""Virtual Windows > アプリ in Files List; actual catalog + alias search."""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

import installed_apps
from launch_virtual_tree import (virtual_launch_pages, virtual_list_rows,
                                 virtual_exp_folders, virtual_lookup_node,
                                 virtual_execution_row)
from middle_folder_filter import filter_sort_folder_rows


def sample():
    pages = [{'page_id': 'windows', 'title': 'Windows'}]
    authored = [
        {'page_id': 'windows', 'item_id': 'installed_apps', 'parent_item_id': '',
         'title': 'アプリ', 'enabled': True, 'item_kind': 'category',
         'sort_order': 40, 'launch_source': 'installed_apps'},
        {'page_id': 'windows', 'item_id': 'audio', 'parent_item_id': '',
         'title': '音声出力', 'enabled': True, 'item_kind': 'category', 'sort_order': 50},
        {'page_id': 'windows', 'item_id': 'sound', 'parent_item_id': 'audio',
         'title': 'サウンド', 'item_kind': 'command', 'enabled': True, 'sort_order': 10},
    ]
    config = {'items': authored, 'app_aliases': [
        {'kind': 'aumid', 'target': 'company.app!main', 'alias': '超高速メモ'}]}
    records = [
        {'name': 'Company Note', 'target': 'company.app!main', 'kind': 'aumid', 'icon_path': ''},
        {'name': 'Google Chrome', 'target': 'chrome.app!main', 'kind': 'aumid', 'icon_path': ''},
    ]
    runtime = installed_apps.attach(config, records)['items']
    return pages, authored, runtime


def app_folder():
    pages, authored, runtime = sample()
    folder = virtual_lookup_node(pages, authored, 'windows', 'installed_apps', runtime)
    return folder, authored, runtime


def test_apps_are_projected_into_list_under_authored_windows_app_category():
    folder, authored, runtime = app_folder()
    assert folder['kind'] == 'folder'
    rows = virtual_list_rows(folder)
    assert [r['title'] for r in rows] == ['Company Note', 'Google Chrome']
    assert all(r['_installed_app'] for r in rows)
    assert all(r['_launch_virtual_node']['runtime_catalog'] == 'installed_apps' for r in rows)
    assert all(r['item_kind'] == 'virtual_launch_file' for r in rows)
    assert all(not any(k in row for k in ('_browse_file', '_file', '_indexed_file')) for row in rows)
    assert all(r['launch_actions'][0]['launch_action_type'] == 'Open' for r in rows)
    # Generated executable leaves must never clutter Files Exp.
    assert virtual_exp_folders(folder) == []
    assert [n['title'] for n in virtual_exp_folders(virtual_launch_pages(
        [{'page_id': 'windows'}], authored, runtime)[0])] == ['アプリ', '音声出力']


def test_virtual_app_list_search_matches_name_default_alias_and_custom_alias():
    folder, _, _ = app_folder()
    rows = virtual_list_rows(folder)
    for query, expected in [
        ('Company', ['Company Note']),
        ('超高速メモ', ['Company Note']),
        ('クローム', ['Google Chrome']),
        ('Chrome', ['Google Chrome']),
        ('company 超高速', ['Company Note']),
        ('(クローム or 超高速メモ)', ['Company Note', 'Google Chrome']),
        ('not-found', []),
    ]:
        assert sorted(row['title'] for row in filter_sort_folder_rows(rows, query)) == sorted(expected), query


def test_non_virtual_physical_files_remain_filename_only():
    data = [{'title': 'project.txt', 'item_kind': 'file', 'keywords': ['超高速メモ']}]
    assert filter_sort_folder_rows(data, '超高速メモ') == []
    assert len(filter_sort_folder_rows(data, 'project')) == 1


def test_runtime_apps_are_not_exposed_if_parent_category_is_missing_or_disabled():
    pages, authored, runtime = sample()
    without = [r for r in authored if r['item_id'] != 'installed_apps']
    tree = virtual_launch_pages(pages, without, runtime)[0]
    assert all(n['title'] != 'アプリ' for n in tree['children'])
    assert all(not n.get('runtime_catalog') for n in tree['children'])
    disabled = [dict(r, enabled=False) if r['item_id'] == 'installed_apps' else r for r in authored]
    tree = virtual_launch_pages(pages, disabled, runtime)[0]
    assert all(n['title'] != 'アプリ' for n in tree['children'])
    assert virtual_execution_row(disabled, runtime, 'windows', runtime[-1]['item_id']) is None


def test_unknown_catalog_rows_cannot_leak_into_virtual_tree():
    pages, authored, runtime = sample()
    fake = {'page_id': 'windows', 'item_id': 'other_tool', 'parent_item_id': 'installed_apps',
            'title': 'Unknown', 'item_kind': 'command', 'enabled': True}
    fake_other_parent = dict(runtime[-1], item_id='app_fake', parent_item_id='audio')
    folder = virtual_lookup_node(pages, authored, 'windows', 'installed_apps',
                                 runtime + [fake, fake_other_parent])
    assert len(virtual_list_rows(folder)) == 2
    assert virtual_execution_row(authored, runtime + [fake], 'windows', 'other_tool') is None
    assert virtual_execution_row(authored, runtime + [fake_other_parent], 'windows', 'app_fake') is None


def test_virtual_exec_resolves_fresh_runtime_app_not_stale_ui_snapshot():
    folder, authored, runtime = app_folder()
    row = virtual_list_rows(folder)[0]
    result = virtual_execution_row(authored, runtime, row['page_id'], row['item_id'])
    assert result is next(r for r in runtime if r.get('item_id') == row['item_id'])
    assert result['_installed_app']
    assert virtual_execution_row(authored, [], row['page_id'], row['item_id']) is None
    assert virtual_execution_row(authored, runtime, 'windows', 'sound') is authored[2]


def test_real_launch_config_has_installed_app_folder():
    config = json.loads((ROOT / 'config/frb_launch_data.json').read_text('utf-8'))
    assert any(row.get('launch_source') == 'installed_apps' and row.get('item_kind') == 'category'
               and row.get('page_id') == 'windows' and row.get('title') == 'アプリ'
               for row in config['items'])


def test_ui_paths_wire_runtime_rows_filter_and_existing_activation():
    panel = (SRC / 'remote_files_explorer.py').read_text('utf-8')
    view = (SRC / 'expanded_view.py').read_text('utf-8')
    app = (SRC / 'app.py').read_text('utf-8')
    assert "(getattr(launcher, 'data', None) or {}).get('items', ())" in panel
    assert 'virtual_list_rows(virtual)' in view
    assert 'filter_sort_folder_rows(' in view
    assert 'self.middle_search.text()' in view
    assert 'virtual_execution_row(' in app
    assert 'self.activate(authoritative)' in app
    assert 'self._refresh_virtual_app_catalog()' in app
    for name in ('app.py', 'expanded_view.py', 'remote_files_explorer.py',
                 'launch_virtual_tree.py', 'middle_folder_filter.py'):
        ast.parse((SRC / name).read_text('utf-8'))
