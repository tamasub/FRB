"""Wildcard search across global search, local menu and SQLite file index."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import searchable_rows, column_filter_match
from file_index import build_index, load_options, search_index
from search_matching import matches_search_text, sql_like_term


class WildcardSearchTests(unittest.TestCase):
    def test_star_is_zero_or_more_case_insensitive(self):
        for pattern in ('FRB*.MD', '*report.md', 'FRB*port*md', 'frb**.md', '*'):
            with self.subTest(pattern=pattern):
                self.assertTrue(matches_search_text('FRB_report.md', pattern))
        self.assertFalse(matches_search_text('FRB_report.md', 'FRB*.py'))
        self.assertFalse(matches_search_text('FRB_report.md', 'frb*z.md'))

    def test_original_substrings_and_space_separated_and(self):
        self.assertTrue(matches_search_text('Markdown report Q4', 'mark port'))
        self.assertTrue(matches_search_text('Markdown report Q4', 'mark*own *Q4'))
        self.assertFalse(matches_search_text('Markdown report Q4', 'mark *Q3'))
        self.assertTrue(matches_search_text('SAVE_10%.json', '10%'))
        self.assertFalse(matches_search_text('SAVE_10%.json', '11%'))
        self.assertEqual(sql_like_term('file_10%*.MD'), '%file!_10!%%.md%')

    def test_cascade_search_excludes_ancestor_folder_names(self):
        row = {'title': 'notes.md', 'description': r'F:\FRB\files\notes.md', '_file': 'exists'}
        self.assertTrue(column_filter_match(row, '*.md'))
        self.assertFalse(column_filter_match(row, 'F*FRB'))
        other = {'title': 'Run utility', 'description': 'Server scripts'}
        self.assertTrue(column_filter_match(other, 'run* server*'))

    def test_global_items_paths_and_choice_hits(self):
        data = {
            'pages': [{'page_id': 'work', 'title': '仕事', 'enabled': True}],
            'items': [
                {'item_id': 'folder', 'item_kind': 'category', 'page_id': 'work', 'title': 'Tools', 'enabled': True},
                {'item_id': 'a', 'item_kind': 'command', 'page_id': 'work', 'parent_item_id': 'folder',
                 'title': 'Launch_Report.md', 'description': 'Monthly', 'enabled': True},
                {'item_id': 'b', 'item_kind': 'command', 'page_id': 'work',
                 'title': 'Other.ps1', 'description': 'System', 'enabled': True},
                {'item_id': 'sel', 'item_kind': 'selection', 'page_id': 'work',
                 'title': '連絡先', 'launch_selection_group_id': 'g', 'enabled': True},
            ],
            'launch_choices': [{'choice_id': 'c', 'group_id': 'g', 'title': '田中 太郎',
                                'value': 'tanaka@example.invalid', 'enabled': True}],
        }
        self.assertEqual([r['item_id'] for r, _ in searchable_rows(data, 'Launch*.md')], ['a'])
        self.assertEqual([r['item_id'] for r, _ in searchable_rows(data, 'TOO* monthly')], ['a'])
        hits = [(r, p) for r, p in searchable_rows(data, 'tan*example.*') if r.get('_search_selection_owner')]
        self.assertEqual([r['choice_id'] for r, p in hits], ['c'])
        self.assertEqual(searchable_rows(data, 'missing*.bat'), [])

    def test_file_index_star_and_sql_special_chars(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('FRB_alpha.md', 'frb_11.ps1', 'FRB_test.py',
                         'FRB_10%.ps1', 'frb_10_test.ps1', 'view_def.md'):
                (root / name).write_text('sample', encoding='utf8')
            db = root / 'file_index.db'
            build_index(db, [str(root)], load_options(root / 'missing.json'))
            find = lambda q: {hit['name'] for hit in search_index(db, q)}
            self.assertEqual(find('FRB*.ps1'), {'frb_11.ps1', 'FRB_10%.ps1', 'frb_10_test.ps1'})
            self.assertEqual(find('frb*test*'), {'FRB_test.py', 'frb_10_test.ps1'})
            self.assertEqual(find('*10%*'), {'FRB_10%.ps1'})
            self.assertEqual(find('frb_11'), {'frb_11.ps1'})
            self.assertEqual(find('frb%11'), set())
            self.assertNotIn('view_def.md', find('*'))
            self.assertTrue(find('*'))


if __name__ == '__main__':
    unittest.main()
