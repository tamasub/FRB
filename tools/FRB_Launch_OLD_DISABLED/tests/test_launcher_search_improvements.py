"""Regression tests for shared OR query, file indexing and scoped selection."""
import ast
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import file_index as fi
from core import searchable_rows
from search_matching import parse_search_query, matches_search_text
from selection_scope import update_visible_checks
from ime_input import initialize_halfwidth_english


class SearchOrTests(unittest.TestCase):
    def test_and_or_with_wildcards_and_mixed_case(self):
        cases = [
            ('XXXX aaa', 'XXXX (aaa or bbb)', True),
            ('XXXX bbb', 'XXXX (AAA OR BBB)', True),
            ('XXXX ccc', 'XXXX (aaa or bbb)', False),
            ('aaa', 'XXXX (aaa or bbb)', False),
            ('XXXX aaa ccc', 'XXXX (aaa or bbb) ccc', True),
            ('XXXX bbb', 'XXXX (aaa or bbb) ccc', False),
            ('Q4 Budget_report.md', 'q4 (budget* or forecast*) *.md', True),
            ('Q4 Incident.md', 'q4 (budget* or forecast*) *.md', False),
            ('report(2026).md', 'report(2026)', True),
            ('draft (approved)', '(approved)', True),
            ('abc', '(abc or)', False),
            ('ABC (aaa', '(aaa', True),
        ]
        for text, query, expected in cases:
            with self.subTest(text=text, query=query):
                self.assertEqual(matches_search_text(text, query), expected)

    def test_sql_index_same_or_results_as_in_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / 'Project (Team) & SharePoint'
            folder.mkdir()
            files = [folder / n for n in ('AAAA_aaa.md', 'AAAA_bbb.ps1',
                                           'AAAA_ccc.md', 'Bbbb_aaa.md',
                                           'AAAA_100%_!.json')]
            for file in files:
                file.write_text('ok', encoding='utf8')
            db = root / 'index.db'
            opts = fi.load_options(root / 'missing.json')
            fi.refresh_index(db, [str(folder)], opts)
            queries = ('AAAA (aaa or bbb)', 'AAAA (aaa OR bbb) *.md',
                       '(AAAA or Bbbb) (aaa or bbb)', 'AAAA* (100% or ccc)',
                       'Project (Team) AAAA', 'AAAA (100% or 100_)')
            for query in queries:
                with self.subTest(query=query):
                    expected = {str(f) for f in files if matches_search_text(str(f), query)}
                    actual = {r['path'] for r in fi.search_index(db, query)}
                    self.assertEqual(actual, expected)

    def test_shared_parser_is_structured_and_does_not_evaluate_query(self):
        self.assertEqual(parse_search_query('x (a or b) y'),
                         ((('x',),), (('a',), ('b',)), (('y',),)))
        self.assertTrue(matches_search_text('`%_*`', '%_*'))
        self.assertFalse(matches_search_text('hello', '(x or)'))


class IndexResilienceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / 'cache.db'
        self.opts = fi.load_options(self.root / 'none.json')

    def test_literal_punctuation_in_directory_names(self):
        dirnames = ['FY (2026)', 'Box [A] 100%_!', '日本語＆① (改定)']
        for d in dirnames:
            folder = self.root / d
            folder.mkdir()
            (folder / '資料 (最終)_v2.md').write_text('ok')
        result = fi.refresh_index(self.db, [str(self.root)], self.opts)
        self.assertEqual(result['count'], len(dirnames))
        self.assertEqual(len(fi.search_index(self.db, '資料')), len(dirnames))
        self.assertEqual(len(fi.search_index(self.db, '(2026)')), 1)
        self.assertEqual(len(fi.search_index(self.db, '100%_!')), 1)
        self.assertEqual(fi._original_scan_path(r'\\?\C:\foo (1)'), r'C:\foo (1)')
        self.assertEqual(fi._original_scan_path(r'\\?\UNC\server\share\doc'),
                         r'\\server\share\doc')

    def test_exclude_folder_glob_configuration(self):
        bad = self.root / 'Unreadable (old)'
        good = self.root / 'Readable (new)'
        bad.mkdir(); good.mkdir()
        (bad / 'skip.md').write_text('ok')
        (good / 'keep.md').write_text('ok')
        self.opts['exclude_directory_globs'] = ['Unreadable (*)']
        result = fi.refresh_index(self.db, [str(self.root)], self.opts)
        self.assertEqual(result['count'], 1)
        self.assertFalse(fi.search_index(self.db, 'skip.md'))
        self.assertTrue(fi.search_index(self.db, 'keep.md'))

    def test_preserve_cached_items_for_inaccessible_subtree(self):
        failed = self.root / 'Unreliable (OneDrive)'
        failed.mkdir()
        (failed / 'old.md').write_text('old')
        (self.root / 'new.md').write_text('ok')
        fi.refresh_index(self.db, [str(self.root)], self.opts)
        (self.root / 'new.md').unlink()
        (self.root / 'other.md').write_text('ok')
        walk = fi.os.walk

        def partly_failing_walk(path, *args, **kwargs):
            for parent, dirs, files in walk(path, *args, **kwargs):
                if os.path.normpath(parent) == os.path.normpath(str(self.root)):
                    if failed.name in dirs:
                        dirs.remove(failed.name)
                        kwargs['onerror'](PermissionError(13, 'Access denied', str(failed)))
                yield parent, dirs, files

        with patch.object(fi.os, 'walk', side_effect=partly_failing_walk):
            result = fi.refresh_index(self.db, [str(self.root)], self.opts)
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['failed_roots'], [])
        self.assertTrue(result['scan_warnings'])
        self.assertEqual(len(fi.search_index(self.db, 'old.md')), 1)
        self.assertEqual(fi.search_index(self.db, 'new.md'), [])
        self.assertEqual(len(fi.search_index(self.db, 'other.md')), 1)

    def test_fail_root_mode_does_not_change_snapshot(self):
        (self.root / 'existing.md').write_text('ok')
        fi.refresh_index(self.db, [str(self.root)], self.opts)
        self.opts['scan_error_policy'] = 'fail_root'
        real_scan = fi._root_scan
        def fail(*args):
            raise PermissionError('folder (bad)')
        with patch.object(fi, '_root_scan', side_effect=fail):
            result = fi.refresh_index(self.db, [str(self.root)], self.opts)
        self.assertEqual(result['failed_roots'], [str(self.root)])
        self.assertTrue(fi.search_index(self.db, 'existing.md'))


class SelectionScopeTests(unittest.TestCase):
    def test_select_all_only_filtered_visible_addresses(self):
        self.assertEqual(update_visible_checks(set(), {'A', 'B'}, True), {'A', 'B'})
        self.assertEqual(update_visible_checks({'Z'}, {'A', 'B'}, True), {'Z','A','B'})
        self.assertEqual(update_visible_checks({'Z','A','B'}, {'A','B'}, False), {'Z'})
        self.assertEqual(update_visible_checks({'Z'}, set(), True), {'Z'})

    def test_launcher_wires_alt_a_and_visible_rows(self):
        source = (ROOT/'src/app.py').read_text(encoding='utf8')
        tree = ast.parse(source)
        klass = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
        methods = {x.name: ast.get_source_segment(source, x) for x in klass.body if isinstance(x, ast.FunctionDef)}
        self.assertIn('Qt.KeyboardModifier.AltModifier', methods['eventFilter'])
        self.assertIn('self.list.topLevelItemCount()', methods['select_all'])
        self.assertIn('update_visible_checks', methods['select_all'])


class IMEFocusTests(unittest.TestCase):
    def test_nonwindows_is_noop_and_focus_is_delayed(self):
        if os.name != 'nt':
            self.assertFalse(initialize_halfwidth_english())
        source = (ROOT/'src/app.py').read_text(encoding='utf8')
        self.assertIn('event.type() == QEvent.Type.FocusIn', source)
        self.assertIn('QTimer.singleShot(0, self.initialize_search_ime)', source)


if __name__ == '__main__':
    unittest.main()
