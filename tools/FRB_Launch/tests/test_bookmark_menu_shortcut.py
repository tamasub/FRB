"""The bookmark singleton-folder shortcut must not modify the browser tree."""
import unittest
from copy import deepcopy

from bookmark_menu import visible_bookmark_children
from browser_bookmarks import attach, ROOT_ID


def row(item_id, parent='', *, title=None, kind='category', bookmark=True, source=None, enabled=True):
    result = dict(item_id=item_id, parent_item_id=parent,
                  title=title or item_id, item_kind=kind,
                  page_id='windows', enabled=enabled, sort_order=0)
    if bookmark:
        result['_browser_bookmark'] = True
    if source:
        result['launch_source'] = source
    return result


def children_of(items):
    def lookup(parent):
        return [r for r in items if r.get('enabled', True)
                and r.get('parent_item_id') == parent['item_id']]
    return lookup


class BookmarkMenuShortcutTests(unittest.TestCase):
    def setUp(self):
        self.root = row('root', bookmark=False, source='browser_bookmarks')

    def test_skip_one_intermediate_folder_when_it_opens_to_many_entries(self):
        shelf = row('bar', 'root')
        first = row('first', 'bar', kind='command')
        second = row('second', 'bar', kind='command')
        items = [shelf, first, second]
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))],
                         ['first', 'second'])
        self.assertEqual(items[0]['parent_item_id'], 'root')
        self.assertEqual(first['parent_item_id'], 'bar')

    def test_collapse_multiple_single_folder_levels_but_not_the_url(self):
        items = [row('bar', 'root'), row('study', 'bar'), row('url', 'study', kind='command')]
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))], ['url'])

    def test_siblings_keep_folder_choice_and_actual_folders(self):
        items = [row('bar', 'root'), row('other', 'root'), row('page', 'bar', kind='command')]
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))],
                         ['bar', 'other'])

    def test_non_bookmark_and_manual_folders_never_collapse(self):
        items = [row('bar', 'root'), row('page', 'bar', kind='command')]
        regular = row('normal', bookmark=False)
        regular_child = row('bar2', 'normal', bookmark=False)
        items.extend([regular_child, row('page2', 'bar2', kind='command')])
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(regular, children_of(items))], ['bar2'])
        # A user-defined folder placed below bookmark root must remain visible.
        manually_added = row('custom', 'root', bookmark=False)
        items.append(manually_added)
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))],
                         ['bar', 'custom'])

    def test_empty_bookmark_folder_remains_visible(self):
        items = [row('empty', 'root')]
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))], ['empty'])

    def test_disabled_items_not_counted_as_siblings(self):
        items = [row('bar', 'root'), row('disabled', 'root', enabled=False),
                 row('page', 'bar', kind='command')]
        self.assertEqual([x['item_id'] for x in visible_bookmark_children(self.root, children_of(items))], ['page'])

    def test_bookmark_data_and_launch_profile_preserved_by_navigation(self):
        data = {'items': [dict(item_id=ROOT_ID, page_id='windows', parent_item_id='',
                               title='ブックマーク', item_kind='category', enabled=True,
                               launch_source='browser_bookmarks') ]}
        profiles = [{'directory': 'Default', 'browser_profile': 'Default',
                     'roots': [{'name': 'ブックマーク バー', 'children': [
                         {'type': 'url', 'name': 'Qiita', 'url': 'https://qiita.com'},
                         {'type': 'url', 'name': 'Zenn', 'url': 'https://zenn.dev'}]}]}]
        runtime = attach(data, 'chrome', profiles)
        before = deepcopy(runtime)
        root = runtime['items'][0]
        result = visible_bookmark_children(root, children_of(runtime['items']))
        self.assertEqual([r['title'] for r in result], ['Qiita', 'Zenn'])
        self.assertEqual(runtime, before)
        self.assertEqual(result[0]['launch_actions'][0]['launch_browser_profile'], 'Default')
        self.assertEqual(result[0]['launch_actions'][0]['launch_browser'], 'chrome')

    def test_more_than_one_profile_keeps_profile_selection(self):
        data = {'items': [dict(item_id=ROOT_ID, page_id='windows', parent_item_id='',
                               title='ブックマーク', item_kind='category', enabled=True,
                               launch_source='browser_bookmarks')]}
        profiles = [{'directory': label, 'browser_profile': label,
                     'roots': [{'name': 'ブックマーク バー', 'children': [
                         {'type': 'url', 'name': label + ' link', 'url': 'https://example.org'}]}]}
                    for label in ('Default', 'Profile 2')]
        runtime = attach(data, 'chrome', profiles)
        result = visible_bookmark_children(runtime['items'][0], children_of(runtime['items']))
        self.assertEqual([r['title'] for r in result], ['Default', 'Profile 2'])


if __name__ == '__main__':
    unittest.main()
