"""Browser bookmark grouping: only genuine top-level groups become headings."""
from copy import deepcopy
from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bookmark_menu import expanded_bookmark_rows, visible_bookmark_children
from browser_bookmarks import ROOT_ID, attach


def children_of(items):
    def get(parent):
        return sorted((row for row in items if row.get('parent_item_id') == parent['item_id']
                       and row.get('enabled', True)), key=lambda r: r.get('sort_order', 0))
    return get


def runtime(profiles):
    data = {'items': [{'item_id': ROOT_ID, 'page_id': 'windows',
                       'parent_item_id': '', 'title': 'ブックマーク',
                       'item_kind': 'category', 'launch_source': 'browser_bookmarks',
                       'enabled': True}]}
    catalog = attach(data, 'edge', profiles)
    return catalog, catalog['items'][0]


def leaf(title):
    return {'name': title, 'type': 'url', 'url': 'https://example.org/' + title}


def folder(title, *nodes):
    return {'name': title, 'type': 'folder', 'children': list(nodes)}


def test_single_top_level_browser_folder_preserves_nested_folders():
    profiles = [{'directory': 'Default', 'browser_profile': 'Default', 'roots': [
        {'name': 'お気に入りバー', 'children': [folder('仕事', leaf('Teams'), leaf('社内Wiki')),
                                     folder('個人', leaf('Qiita'), leaf('Zenn'))]}]}]
    catalog, root = runtime(profiles)
    snapshot = deepcopy(catalog)
    rows = expanded_bookmark_rows(root, children_of(catalog['items']))
    assert [r['title'] for r in rows] == ['仕事', '個人']
    assert not any(r.get('_bookmark_group_header') for r in rows)
    assert all(r['item_kind'] == 'category' for r in rows)
    assert [r['title'] for r in children_of(catalog['items'])(rows[0])] == ['Teams', '社内Wiki']
    assert [r['title'] for r in children_of(catalog['items'])(rows[1])] == ['Qiita', 'Zenn']
    assert catalog == snapshot  # Do not alter Edge data or persisted config.
    assert all(r['launch_actions'][0]['launch_browser'] == 'edge'
               and r['launch_actions'][0]['launch_browser_profile'] == 'Default'
               for r in catalog['items'] if r.get('item_kind') == 'command')
    assert [r['title'] for r in visible_bookmark_children(root, children_of(catalog['items']))] == ['仕事', '個人']


def test_existing_single_folder_shortcut_still_collapses_singleton_chains():
    profiles = [{'directory': 'Default', 'roots': [
        {'name': 'お気に入りバー', 'children': [folder('仕事', leaf('Wiki'))]}]}]
    catalog, root = runtime(profiles)
    assert [r['title'] for r in expanded_bookmark_rows(root, children_of(catalog['items']))] == ['Wiki']
    profiles[0]['roots'][0]['children'].append(folder('個人', folder('技術', leaf('記事'))))
    catalog, root = runtime(profiles)
    assert [r['title'] for r in expanded_bookmark_rows(root, children_of(catalog['items']))] == [
        '仕事', '個人']


def test_empty_groups_stay_navigable_and_direct_urls_keep_relative_order():
    profiles = [{'directory': 'Default', 'roots': [
        {'name': 'お気に入りバー', 'children': [folder('空'), leaf('トップ'),
                 folder('A', leaf('A1')), folder('B', leaf('B1'))]}]}]
    catalog, root = runtime(profiles)
    rows = expanded_bookmark_rows(root, children_of(catalog['items']))
    assert [r['title'] for r in rows] == ['空', 'トップ', 'A', 'B']
    assert [r['title'] for r in rows if r.get('_bookmark_group_header')] == []
    assert rows[0]['item_kind'] == 'category'



def test_two_genuine_top_level_groups_become_headings_only_at_that_level():
    """This works equally for Chrome or Edge; it is a tree-shape decision."""
    profiles = [{'directory': 'Default', 'browser_profile': 'Default', 'roots': [
        {'name': '第1グループ', 'children': [leaf('入口'), folder('仕事', leaf('Teams'), leaf('社内Wiki'))]},
        {'name': '第2グループ', 'children': [leaf('個人サイト'), folder('保存先', leaf('GitHub'))]}
    ]}]
    for browser in ('chrome', 'edge'):
        data = {'items': [{'item_id': ROOT_ID, 'page_id': 'windows',
                           'parent_item_id': '', 'title': 'ブックマーク',
                           'item_kind': 'category', 'launch_source': 'browser_bookmarks',
                           'enabled': True}]}
        catalog = attach(data, browser, profiles)
        root = catalog['items'][0]
        rows = expanded_bookmark_rows(root, children_of(catalog['items']))
        assert [r['title'] for r in rows] == [
            '第1グループ', '入口', '仕事', '第2グループ', '個人サイト', '保存先']
        assert [r['title'] for r in rows if r.get('_bookmark_group_header')] == [
            '第1グループ', '第2グループ']
        assert [r['title'] for r in rows if r.get('item_kind') == 'category'] == [
            '仕事', '保存先']
        assert [r['title'] for r in children_of(catalog['items'])(rows[2])] == [
            'Teams', '社内Wiki']


def test_single_root_with_many_direct_links_and_nested_folders():
    """Regression for the screenshot: Studioくん and FRB_FFT are not headers."""
    profiles = [{'directory': 'Default', 'roots': [
        {'name': 'ブックマーク バー', 'children': [
            leaf('GA_Zenn'), leaf('GA_Qiita'), leaf('Claude'),
            folder('Studioくん', leaf('FRB認証'), leaf('FX Studioくん')),
            folder('FRB_FFT', leaf('FFT1'), leaf('localFFT')),
            folder('★SNS_Blog★', leaf('note'), leaf('X'))]}]}]
    catalog, root = runtime(profiles)
    rows = expanded_bookmark_rows(root, children_of(catalog['items']))
    assert [r['title'] for r in rows] == [
        'GA_Zenn', 'GA_Qiita', 'Claude', 'Studioくん', 'FRB_FFT', '★SNS_Blog★']
    assert not any(r.get('_bookmark_group_header') for r in rows)
    for nested in rows[3:]:
        assert nested['item_kind'] == 'category'
        assert nested.get('_browser_bookmark')
        assert len(children_of(catalog['items'])(nested)) == 2

def test_two_profiles_preserve_individual_browser_routing():
    profiles = [{'directory': name, 'browser_profile': name,
                 'roots': [{'name': 'ブックマークバー', 'children': [leaf(name)]}]}
                for name in ('Default', 'Profile 2')]
    catalog, root = runtime(profiles)
    rows = expanded_bookmark_rows(root, children_of(catalog['items']))
    assert [r['title'] for r in rows] == ['Default', 'Default', 'Profile 2', 'Profile 2']
    assert [r.get('_bookmark_group_header', False) for r in rows] == [True, False, True, False]
    links = [r for r in rows if r.get('item_kind') == 'command']
    assert [r['launch_actions'][0]['launch_browser_profile'] for r in links] == ['Default', 'Profile 2']


def test_non_bookmark_folders_are_not_flattened_and_ui_headings_not_actions():
    src = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    tree = ast.parse(src)
    assert "expanded_bookmark_rows(right, self.launcher.children)" in src
    assert "heading.setData(0, Qt.ItemDataRole.UserRole + 1, True)" in src
    assert "item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)" in src
    assert "if row is None:  # Non-actionable bookmark section heading." in src
    parent = {'item_id': 'manual', 'item_kind': 'category'}
    items = [{'item_id': 'folder_a', 'item_kind': 'category', 'parent_item_id': 'manual'},
             {'item_id': 'folder_b', 'item_kind': 'category', 'parent_item_id': 'manual'}]
    assert expanded_bookmark_rows(parent, children_of(items)) == items


def test_wheel_navigation_skips_non_clickable_group_headers():
    # Run the real wheel handlers with the project's existing Qt-free fakes.
    from test_bookmark_first_level_wheel_20261025 import Demo as LegacyDemo, Event as LegacyEvent
    old = LegacyDemo(kinds=('command', 'command', 'command'))
    rows = [dict(title='A1', item_kind='command'),
            dict(title='A', _bookmark_group_header=True),
            dict(title='B1', item_kind='command')]
    old.right.tree.rows = rows
    old.right.tree.current = rows[0]
    old.row_data = lambda item: None if item.get('_bookmark_group_header') else item
    assert old.wheel_bookmarks_first_level(LegacyEvent(angle=-120))
    assert old.right.tree.current is rows[2]
    assert old.wheel_bookmarks_first_level(LegacyEvent(angle=120))
    assert old.right.tree.current is rows[0]

    from test_bookmark_wan_hybrid_20261025 import Demo as WanDemo, Event as WanEvent
    wan = WanDemo()
    wan.right.tree.rows = rows
    wan.right.tree.cur = rows[0]
    wan.right.tree.hovered = 0
    wan.row_data = lambda item: None if item.get('_bookmark_group_header') else item
    assert wan.wheel_bookmarks_at_edge(WanEvent(angle=-120), 0, 0)
    assert wan.right.tree.cur is rows[2]
