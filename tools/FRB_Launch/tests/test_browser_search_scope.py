"""Global search must never leak another browser's bookmarks or internal metadata."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from browser_bookmarks import attach
from core import load, searchable_rows

CONFIG = Path(__file__).resolve().parents[1] / 'config/frb_launch_sample_data_v0_1.json'


class BrowserSearchScopeTests(unittest.TestCase):
    def setUp(self):
        self.data = load(CONFIG)
        chrome_profiles = [{'directory': 'Default', 'browser_profile': 'Default', 'roots': [
            {'name': 'ブックマーク バー', 'children': [
                {'type': 'url', 'name': 'FRB Chrome専用', 'url': 'https://example.com/chrome-only'},
                {'type': 'url', 'name': '共通サイト', 'url': 'https://example.com/for-chrome'},
            ]}]}]
        edge_profiles = [{'directory': 'Default', 'browser_profile': 'Default', 'roots': [
            {'name': 'ブックマーク バー', 'children': [
                {'type': 'url', 'name': 'FRB Edge専用', 'url': 'https://example.com/edge-only'},
            ]}]}]
        self.chrome = attach(self.data, 'chrome', chrome_profiles)
        self.edge = attach(self.data, 'edge', edge_profiles)

    @staticmethod
    def names(data, word, browser):
        return [r['title'] for r, path in searchable_rows(data, word, bookmark_browser=browser)
                if r.get('_browser_bookmark')]

    def test_chrome_scope_only_chrome_even_if_both_catalogs_are_present(self):
        # Simulate accidentally stale Edge entries in memory, independent of
        # the reader's existing replace-on-switch protection.
        mixed = {**self.chrome, 'items': self.chrome['items'] + [
            r for r in self.edge['items'] if r.get('_browser_bookmark') and
            r.get('item_id') != '__browser_bookmarks_root']}
        self.assertIn('FRB Chrome専用', self.names(mixed, 'FRB', 'chrome'))
        self.assertNotIn('FRB Edge専用', self.names(mixed, 'FRB', 'chrome'))
        self.assertIn('FRB Edge専用', self.names(mixed, 'FRB', 'edge'))
        self.assertNotIn('FRB Chrome専用', self.names(mixed, 'FRB', 'edge'))

    def test_internal_launch_browser_or_profile_metadata_is_not_searchable(self):
        # 'chrome' occurs in the URL of the item named '共通サイト', so that
        # remains intentionally searchable.  An unrelated internal property
        # such as '_bookmark_browser' must NOT turn other results into hits.
        self.assertNotIn('FRB Chrome専用', self.names(self.chrome, 'launch_browser', 'chrome'))
        self.assertEqual(self.names(self.chrome, 'Default', 'chrome'), [])
        self.assertIn('共通サイト', self.names(self.chrome, 'for-chrome', 'chrome'))
        self.assertIn('FRB Chrome専用', self.names(self.chrome, 'FRB', 'chrome'))

    def test_non_bookmark_global_search_remains_unchanged(self):
        rows = searchable_rows(self.chrome, 'appdata', bookmark_browser='chrome')
        self.assertEqual({row['item_id'] for row, _ in rows}, {'roaming', 'local'})

    def test_malformed_or_untagged_bookmark_not_admitted_to_scoped_search(self):
        stale = {**self.chrome['items'][-1]}
        stale['item_id'] = 'legacy_other_browser'
        stale.pop('_bookmark_browser', None)
        stale['title'] = '古いブラウザの登録'
        mixed = {**self.chrome, 'items': self.chrome['items'] + [stale]}
        self.assertNotIn('古いブラウザの登録', self.names(mixed, '古い', 'chrome'))


if __name__ == '__main__':
    unittest.main()
