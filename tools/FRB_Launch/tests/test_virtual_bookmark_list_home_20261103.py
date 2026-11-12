"""HOME-first-root and bookmark virtual Files List integration (Qt-free)."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

import browser_bookmarks
from launch_virtual_tree import (virtual_launch_pages, virtual_lookup_node,
                                 virtual_exp_folders, virtual_list_rows,
                                 virtual_bookmark_execution_row)
from webview_routes import bookmark_web_url


def fixture():
    pages = [{'page_id': 'windows', 'title': 'Windows'}]
    authored = [{'item_id': 'bookmark-root', 'page_id': 'windows', 'parent_item_id': '',
                 'title': 'ブックマーク', 'item_kind': 'category', 'enabled': True,
                 'launch_source': 'browser_bookmarks', 'sort_order': 10}]
    profiles = [{'directory': 'Default', 'browser_profile': 'Default',
                 'roots': [{'name': 'ブックマーク バー', 'children': [
                     {'type': 'url', 'name': 'OpenAI', 'url': 'https://openai.com/a?b=1&c=2'},
                     {'type': 'folder', 'name': '仕事', 'children': [
                         {'type': 'url', 'name': 'Studio', 'url': 'https://example.org/docs'}]}]}]}]
    runtime = browser_bookmarks.attach({'items': authored}, 'chrome', profiles)['items']
    return pages, authored, runtime


def test_bookmark_folder_tree_and_list_are_projected_from_runtime_records():
    pages, authored, runtime = fixture()
    root = virtual_lookup_node(pages, authored, 'windows', 'bookmark-root', runtime)
    assert root['kind'] == 'folder'
    group = root['children'][0]
    assert group['title'] == 'ブックマーク バー'
    assert group['runtime_catalog'] == 'browser_bookmarks'
    assert [x['title'] for x in virtual_exp_folders(group)] == ['仕事']
    rows = virtual_list_rows(group)
    assert [r['title'] for r in rows] == ['OpenAI', '仕事']
    leaf = rows[0]
    assert leaf['item_kind'] == 'virtual_launch_file'
    assert leaf['_launch_virtual_node']['runtime_catalog'] == 'browser_bookmarks'
    assert bookmark_web_url(leaf['_launch_virtual_node']['row']) == 'https://openai.com/a?b=1&c=2'
    assert all('_browse_file' not in r and '_file' not in r for r in rows)


def test_bookmark_url_resolves_against_fresh_catalog_only():
    pages, authored, runtime = fixture()
    root = virtual_lookup_node(pages, authored, 'windows', 'bookmark-root', runtime)
    bookmark = virtual_list_rows(root['children'][0])[0]
    resolved = virtual_bookmark_execution_row(authored, runtime,
                                               bookmark['page_id'], bookmark['item_id'])
    assert resolved is bookmark['_launch_virtual_node']['row']
    assert virtual_bookmark_execution_row(authored, [], 'windows', bookmark['item_id']) is None
    disabled = [{**authored[0], 'enabled': False}]
    assert virtual_bookmark_execution_row(disabled, runtime, 'windows', bookmark['item_id']) is None
    injected = {**resolved, 'item_id': 'forged', 'parent_item_id': 'missing', '_browser_bookmark': True}
    assert virtual_bookmark_execution_row(authored, runtime + [injected], 'windows', 'forged') is None
    orphan = {**resolved, 'item_id': 'orphan', 'parent_item_id': 'bookmark-root',
              'page_id': 'work'}
    assert virtual_bookmark_execution_row(authored, runtime + [orphan], 'work', 'orphan') is None
    assert virtual_lookup_node(pages, disabled, 'windows', 'bookmark-root', runtime) is None


def test_non_http_links_and_bookmark_folders_cannot_execute():
    pages, authored, runtime = fixture()
    root = virtual_lookup_node(pages, authored, 'windows', 'bookmark-root', runtime)
    folder = root['children'][0]
    assert virtual_bookmark_execution_row(authored, runtime, 'windows', folder['item_id']) is None
    leaf = virtual_list_rows(folder)[0]
    assert bookmark_web_url({**leaf, 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': 'javascript:alert(1)'}]}) is None


def method(filename, cls, name):
    module = ast.parse((SRC / filename).read_text(encoding='utf-8'))
    owner = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.unparse(fn)


def test_home_and_remote_both_target_first_visible_exp_root():
    exp = method('remote_files_explorer.py', 'RemoteFilesExplorer', 'select_first_root_for_home')
    home = method('app.py', 'Launcher', 'navigate_home')
    remote = method('app.py', 'Launcher', 'remote_command')
    assert 'self.model.index(0, 0)' in exp
    assert "('virtual', data['virtual'])" in exp
    assert 'self.navigate_virtual_launch_folder(directory)' in home
    assert "self.remote_focus_area('files_exp'" in home
    assert "self.navigate_home()" in remote
    home_branch = remote.split("if command == 'HOME':", 1)[1].split("if command == 'SEARCH':", 1)[0]
    assert 'self.remote_focus_area' not in home_branch


def test_bookmark_double_click_routes_to_real_browser_new_tab():
    app = method('app.py', 'Launcher', 'activate_virtual_launch_item')
    middle = method('expanded_view.py', 'ExpandedLauncherView', 'activate_row')
    remote = method('app.py', 'Launcher', 'remote_mouse_click')
    assert 'virtual_bookmark_execution_row(' in app
    assert 'bookmark_web_url(authoritative)' in app
    assert 'view.show_web_url(url, new_tab=True)' in app
    assert 'self.launcher.activate_virtual_launch_item' in middle
    assert "elif double:" in remote and 'view.activate_row(pane, item)' in remote


def test_actual_browser_bookmark_attach_and_virtual_node_include_only_allowed_root():
    pages, authored, runtime = fixture()
    no_root = virtual_launch_pages(pages, [], runtime)[0]
    assert not no_root['children']
    root = virtual_launch_pages(pages, authored, runtime)[0]
    assert [child['title'] for child in root['children']] == ['ブックマーク']
    assert len(virtual_exp_folders(root)) == 1


def _extracted_method(filename, cls, name, globals_):
    module = ast.parse((SRC / filename).read_text(encoding='utf-8'))
    owner = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    space = dict(globals_)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<virtual-bookmark-method>', 'exec'), space)
    return space[name]


def test_bookmark_launch_invokes_new_tab_without_running_launch_action():
    events = []
    pages, authored, runtime = fixture()
    node = virtual_lookup_node(pages, authored, 'windows', 'bookmark-root', runtime)
    bookmark = virtual_list_rows(node['children'][0])[0]
    leaf = bookmark['_launch_virtual_node']['row']
    action = _extracted_method('app.py', 'Launcher', 'activate_virtual_launch_item', {
        'virtual_bookmark_execution_row': virtual_bookmark_execution_row,
        'bookmark_web_url': bookmark_web_url,
        'virtual_execution_row': lambda *args: None,
    })
    view = NS(show_web_url=lambda url, **k: (events.append(('web', url, k)) or True),
              switch_workspace=lambda mode: events.append(('workspace', mode)))
    launch = NS(authored_items=authored, data={'items': runtime}, expanded_view=view,
                webview_settings={'mode': 'embedded'}, activate=lambda row: events.append(('execute', row)))
    assert action(launch, leaf) is True
    assert events == [('web', 'https://openai.com/a?b=1&c=2', {'new_tab': True})]
    assert action(launch, {**leaf, 'item_id': 'deleted'}) is False
    assert len(events) == 1


def test_external_mode_switches_to_browser_and_uses_existing_open_action():
    events = []
    _, authored, runtime = fixture()
    leaf = next(r for r in runtime if r.get('item_kind') == 'command')
    action = _extracted_method('app.py', 'Launcher', 'activate_virtual_launch_item', {
        'virtual_bookmark_execution_row': virtual_bookmark_execution_row,
        'bookmark_web_url': bookmark_web_url,
        'virtual_execution_row': lambda *args: None,
    })
    view = NS(show_web_url=lambda *a, **k: events.append(('bad-embedded', a)),
              switch_workspace=lambda mode: events.append(('workspace', mode)))
    launch = NS(authored_items=authored, data={'items': runtime}, expanded_view=view,
                webview_settings={'mode': 'external'}, activate=lambda row: events.append(('execute', row['item_id'])))
    assert action(launch, leaf) is True
    assert events == [('workspace', 'browser'), ('execute', leaf['item_id'])]


def test_current_launch_config_bookmark_location_is_not_hard_coded():
    import json
    data = json.loads((ROOT / 'config/frb_launch_data.json').read_text('utf-8'))
    bookmark_roots = [r for r in data['items']
                      if r.get('launch_source') == 'browser_bookmarks'
                      and r.get('enabled', True)]
    assert bookmark_roots
    root = bookmark_roots[0]
    profiles = [{'directory': 'Default', 'browser_profile': 'Default', 'roots': [
        {'name': 'ブックマーク バー', 'children': [
            {'type': 'url', 'name': 'FRB', 'url': 'https://example.org/FRB'}]}]}]
    runtime = browser_bookmarks.attach(data, 'chrome', profiles)['items']
    projected = virtual_lookup_node(data['pages'], data['items'],
                                    root['page_id'], root['item_id'], runtime)
    assert projected is not None and projected['children']
    assert projected['children'][0]['title'] == 'ブックマーク バー'
    assert virtual_list_rows(projected['children'][0])[0]['title'] == 'FRB'
