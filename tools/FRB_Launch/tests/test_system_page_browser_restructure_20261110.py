"""Publish prep: move authored Files + bookmarks under System without breaking Files workspace.

This is a data migration contract. It must not change item IDs or actions.
"""
import json
from pathlib import Path

from browser_bookmarks import attach, ROOT_ID
from core import validate
from expanded_view_model import expanded_targets, normalize_options, should_expand, toolbar_roots
from launch_virtual_tree import virtual_launch_pages, virtual_lookup_node, virtual_studio_target
from menu_hotkeys import menu_shortcuts

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    return json.loads((ROOT / 'config/frb_launch_data.json').read_text(encoding='utf-8'))


def options():
    return normalize_options(json.loads((ROOT / 'config/expanded_view_options.json').read_text(encoding='utf-8')))


def test_system_page_structure_and_stable_ids():
    data = validate(load_config())
    pages = {p['page_id']: p for p in data['pages']}
    rows = {r['item_id']: r for r in data['items']}
    assert len(pages) == 5
    assert pages['system']['enabled'] is True
    assert pages['system']['title'] == '⚙️ System'
    assert len(rows) == 88  # No menus/commands deleted or duplicated
    assert rows['folders']['page_id'] == 'system'
    assert rows['folders']['parent_item_id'] == ''
    assert rows[ROOT_ID]['title'] == 'Browser'
    assert rows[ROOT_ID]['page_id'] == 'system'
    assert rows[ROOT_ID]['launch_source'] == 'browser_bookmarks'
    assert rows[ROOT_ID]['launch_shortcut_key'] == 'Ctrl+Shift+B'
    assert len([r for r in data['items'] if r['parent_item_id'] == 'folders']) == 11
    assert all(r['page_id'] == 'system' for r in data['items']
               if r['parent_item_id'] == 'folders')
    assert all(r['page_id'] != 'work' for r in data['items']
               if r['item_id'] in ('folders', ROOT_ID) or r['parent_item_id'] == 'folders')
    assert {r['title'] for r in data['items'] if r['page_id']=='work'
            and not r['parent_item_id']} == {'ZIP', 'Quick', '日付・定型文', 'メール宛先／😀絵文字'}
    assert data['launch_default_page_id'] == 'work'  # Compact behavior retained


def test_expanded_workspace_uses_system_page_not_old_work():
    data = load_config()
    actual = options()
    assert actual == normalize_options(None)
    assert actual['page_id'] == 'system'
    roots, files, browser = expanded_targets(data['items'], actual)
    assert {r['item_id'] for r in roots} == {'folders', ROOT_ID}
    assert [files['title'], browser['title']] == ['Files', 'Browser']
    assert toolbar_roots(roots, files, browser) == []
    assert should_expand(view_mode='expanded', page_id='system', query='',
                         stack=[], selection=None, options=actual, available=True)
    assert not should_expand(view_mode='expanded', page_id='work', query='',
                             stack=[], selection=None, options=actual, available=True)


def test_bookmark_import_and_files_exp_studio_identity():
    data = load_config()
    bookmark_profiles = [{'directory':'Default', 'browser_profile':'Default', 'roots':[
        {'name':'ブックマーク バー', 'children':[
            {'type':'url', 'name':'テストURL', 'url':'https://example.org/test', 'id':'1'}]}]}]
    imported = attach(data, 'chrome', bookmark_profiles)
    validate(imported)
    assert len(imported['items']) > len(data['items'])
    assert all(row['page_id'] == 'system' for row in imported['items']
               if row.get('_browser_bookmark'))
    assert len([r for r in imported['items'] if r['item_id'] == ROOT_ID]) == 1
    trees = virtual_launch_pages(data['pages'], data['items'], imported['items'])
    assert len(trees) == 5
    system = next(n for n in trees if n['page_id'] == 'system')
    work = next(n for n in trees if n['page_id'] == 'work')
    assert all(n['item_id'] != 'folders' for n in system['children'])
    assert any(n['title'] == 'Browser' for n in system['children'])
    assert all(n['item_id'] not in {'folders', ROOT_ID} for n in work['children'])
    node = virtual_lookup_node(data['pages'], data['items'], 'system', ROOT_ID, imported['items'])
    assert node['title'] == 'Browser'
    assert virtual_studio_target({'source':'launch_json', 'page_id':'system',
                                  'item_id':ROOT_ID,
                                  'node_id':f'item:system:{ROOT_ID}'},
                                 data['pages'], data['items']) == {
                                     'kind':'item','page_id':'system','item_id':ROOT_ID}
    assert virtual_studio_target({'source':'launch_json', 'page_id':'work',
                                  'item_id':ROOT_ID,
                                  'node_id':f'item:work:{ROOT_ID}'},
                                 data['pages'], data['items']) is None


def test_system_hotkeys_are_not_tied_to_my_work_enabled_state():
    data = load_config()
    codes = dict(menu_shortcuts(validate(data)))
    assert codes['folders'] == 'Ctrl+Shift+F'
    assert codes[ROOT_ID] == 'Ctrl+Shift+B'
    next(p for p in data['pages'] if p['page_id']=='work')['enabled'] = False
    assert {'folders', ROOT_ID} <= set(dict(menu_shortcuts(validate(data))))
