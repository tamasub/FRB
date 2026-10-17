"""A global search must match user-visible fields, not internal JSON keys."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import load, searchable_rows
from installed_apps import attach

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/frb_launch_sample_data_v0_1.json'


class GlobalVisibleFieldSearchTests(unittest.TestCase):
    def setUp(self):
        self.data = load(CONFIG)
        self.records = [
            {'name': 'Administrative Tools', 'kind': 'shortcut',
             'target': r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Administrative Tools\IIS Manager.lnk'},
            {'name': 'Audacity', 'kind': 'shortcut',
             'target': r'C:\Tools\FRB_Launch\Audacity.lnk'},
            {'name': 'Google Chrome', 'kind': 'aumid',
             'target': 'Chrome.App'},
        ]
        self.data = attach(self.data, self.records)

    def apps(self, query):
        return [row['title'] for row, _ in searchable_rows(self.data, query)
                if row.get('_installed_app')]

    def test_launch_key_does_not_match_all_installed_apps(self):
        self.assertEqual(self.apps('launch'), [])
        self.assertEqual(self.apps('launch_actions'), [])

    def test_launch_in_target_path_does_not_match(self):
        self.assertNotIn('Audacity', self.apps('FRB_Launch'))

    def test_title_and_alias_still_match(self):
        self.assertEqual(self.apps('Administrative'), ['Administrative Tools'])
        self.assertEqual(self.apps('クローム'), ['Google Chrome'])

    def test_description_and_user_keywords_still_match(self):
        target = next(row for row in self.data['items']
                      if row.get('_installed_app') and row['title'] == 'Audacity')
        target['description'] = 'audio launch helper'
        target['keywords'] = ['音声編集']
        self.assertEqual(self.apps('launch'), ['Audacity'])
        self.assertEqual(self.apps('音声編集'), ['Audacity'])

    def test_page_path_and_other_searches_still_work(self):
        self.assertEqual({row['item_id'] for row, _ in searchable_rows(self.data, 'appdata')},
                         {'roaming', 'local'})
        self.assertIn('Google Chrome', self.apps('Windows アプリ'))

    def test_internal_names_not_used_even_on_user_config_items(self):
        row = next(row for row in self.data['items'] if row['item_id'] == 'installed_apps')
        self.assertNotIn(row, [x for x, _ in searchable_rows(self.data, 'launch_source')])


if __name__ == '__main__':
    unittest.main()
