"""Exp-only promotion: hide System, surface Browser as a page-style bookmark root."""
import ast
import json
from pathlib import Path

from browser_bookmarks import attach, ROOT_ID
from launch_virtual_tree import (
    virtual_exp_roots, virtual_exp_presentation, virtual_lookup_node,
    virtual_list_rows, virtual_item_identity, virtual_studio_target,
)

ROOT = Path(__file__).resolve().parents[1]


def config():
    return json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def test_system_hidden_but_bookmarks_are_top_level_page_alias():
    data = config()
    roots = virtual_exp_roots(data['pages'], data['items'])
    names = [node['title'] for node in roots]
    assert '⚙️ System' not in names
    assert names[-1] == '🔖 ブックマーク'
    bookmark = roots[-1]
    assert bookmark['kind'] == 'page'  # visible Page-like presentation
    assert bookmark['page_id'] == 'system'
    assert bookmark['item_id'] == ROOT_ID
    assert bookmark['node_id'] == f'item:system:{ROOT_ID}'
    assert bookmark['lineage'] == (f'item:system:{ROOT_ID}',)
    assert bookmark['breadcrumbs'] == ('🔖 ブックマーク',)
    assert all(node['item_id'] != 'folders' for node in roots)
    assert virtual_studio_target(virtual_item_identity(bookmark), data['pages'], data['items']) == {
        'kind': 'item', 'page_id': 'system', 'item_id': ROOT_ID,
    }
    assert next(r for r in data['items'] if r['item_id'] == ROOT_ID)['title'] == 'Browser'


def test_nested_dynamic_bookmarks_keep_navigation_and_original_identity():
    data = config()
    imported = attach(data, 'chrome', [{'directory': 'Default', 'browser_profile': 'Default',
        'roots': [{'name': 'ブックマーク バー', 'children': [
            {'type': 'folder', 'name': '仕事', 'children': [
                {'type': 'url', 'name': 'Example', 'url': 'https://example.com/a'}]}]}]}])
    bookmark = virtual_exp_roots(data['pages'], data['items'], imported['items'])[-1]
    bar = bookmark['children'][0]
    work = bar['children'][0]
    url = virtual_list_rows(work)[0]['_launch_virtual_node']
    assert bar['lineage'] == (bookmark['node_id'], bar['node_id'])
    assert work['lineage'] == (bookmark['node_id'], bar['node_id'], work['node_id'])
    assert work['breadcrumbs'] == ('🔖 ブックマーク', 'ブックマーク バー', '仕事')
    assert url['breadcrumbs'][0] == '🔖 ブックマーク'
    assert url['row'].get('_browser_bookmark')
    assert url['page_id'] == 'system'
    # A canonical Lookup (e.g. on Back) is normalized to the same visual path.
    canonical = virtual_lookup_node(data['pages'], data['items'], 'system', ROOT_ID,
                                    imported['items'])
    projected = virtual_exp_presentation(canonical)
    assert projected['title'] == bookmark['title']
    assert projected['lineage'] == bookmark['lineage']
    assert projected['kind'] == 'page'
    assert virtual_exp_presentation(projected)['breadcrumbs'] == ('🔖 ブックマーク',)
    assert virtual_item_identity(bar)['item_id'] == bar['item_id']
    assert virtual_studio_target(virtual_item_identity(bar), data['pages'], data['items']) is None


def test_other_pages_unaffected_and_missing_browser_does_not_fake_one():
    data = config()
    baseline = virtual_exp_roots(data['pages'], data['items'])
    assert baseline[0]['title'] == '💼 My Work'
    assert baseline[0]['children'][0]['title'] == 'ZIP'
    without = [r for r in data['items'] if r['item_id'] != ROOT_ID]
    assert all(n['item_id'] != ROOT_ID for n in virtual_exp_roots(data['pages'], without))
    disabled = [{**r, 'enabled': False} if r['item_id'] == ROOT_ID else r for r in data['items']]
    assert all(n['item_id'] != ROOT_ID for n in virtual_exp_roots(data['pages'], disabled))
    # This is a presentation rule, not a broad rename of every Browser category.
    others = [{'page_id': 'other', 'title': 'Other'}]
    items = [{'page_id': 'other', 'item_id': ROOT_ID, 'title': 'Browser',
              'item_kind': 'category', 'enabled': True}]
    assert virtual_exp_roots(others, items)[0]['children'][0]['title'] == 'Browser'


def test_runtime_wiring_stays_in_display_layer_and_compiles():
    source = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
    view = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    assert 'for page in virtual_exp_roots(' in source
    assert 'bookmarks_item_id=options.get(' in source
    assert 'virtual_exp_presentation(' in view
    assert 'panel.remote_select_virtual_node(node)' in view
    for file in ('remote_files_explorer.py', 'expanded_view.py', 'launch_virtual_tree.py'):
        ast.parse((ROOT / 'src' / file).read_text('utf-8'))
