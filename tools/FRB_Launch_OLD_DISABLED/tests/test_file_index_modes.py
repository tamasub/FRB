"""Scope modes, paths with spaces, scan-depth cap, and SQLite cache reset."""
import ast
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import file_index as fi


class IndexModesTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.launch_root = self.base / 'launch_registered'
        self.launch_root.mkdir()
        self.company = self.base / 'SharePoint Company Files'
        self.company.mkdir()
        (self.company / 'root file.md').write_text('test')
        self.sub = self.company / 'Box Project Team'
        self.sub.mkdir()
        (self.sub / 'child report.xlsx').write_text('test')
        self.deep = self.sub / 'nested folder'
        self.deep.mkdir()
        (self.deep / 'deep script.ps1').write_text('test')
        (self.launch_root / 'launch only.md').write_text('test')
        self.db = self.base / 'index.db'
        self.conf = self.base / 'config.json'
        self.data = {'pages': [{'page_id': 'work'}], 'items': [
            {'page_id': 'work', 'item_kind': 'directory', 'launch_browse_target': str(self.launch_root)}
        ]}

    def opts(self, **changes):
        self.conf.write_text(json.dumps(changes, ensure_ascii=False), encoding='utf8')
        return fi.load_options(self.conf)

    def test_registered_mode_matches_existing_roots(self):
        options = self.opts(index_mode='registered', index_folders=[str(self.company)])
        roots, _ = fi.resolve_roots(options, self.data, lambda x: x)
        self.assertEqual(roots, [str(self.launch_root)])
        fi.refresh_index(self.db, roots, options)
        self.assertTrue(fi.search_index(self.db, 'launch only.md'))
        self.assertFalse(fi.search_index(self.db, 'root file.md'))

    def test_configured_mode_is_independent_of_launcher_and_keeps_spaces(self):
        options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        roots, warning = fi.resolve_roots(options)
        self.assertEqual(roots, [str(self.company)])
        self.assertEqual(warning, [])
        result = fi.refresh_index(self.db, roots, options)
        self.assertEqual(result['count'], 3)
        self.assertEqual(len(fi.search_index(self.db, 'child report')), 1)
        self.assertEqual(len(fi.search_index(self.db, 'nested folder deep script')), 1)
        self.assertFalse(fi.search_index(self.db, 'launch only'))

    def test_scope_switch_replaces_old_hits(self):
        current = self.opts(index_mode='registered')
        fi.refresh_index(self.db, fi.resolve_roots(current, self.data, lambda p:p)[0], current)
        next_options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        fi.refresh_index(self.db, fi.resolve_roots(next_options)[0], next_options)
        self.assertFalse(fi.search_index(self.db, 'launch only'))
        self.assertTrue(fi.search_index(self.db, 'root file'))

    def test_max_depth_limits_scan_and_invalidates_cached_results(self):
        options = self.opts(index_mode='configured', index_folders=[str(self.company)], max_depth=0)
        roots, _ = fi.resolve_roots(options)
        fi.refresh_index(self.db, roots, options)
        self.assertEqual(fi.index_status(self.db)['count'], 1)
        options = self.opts(index_mode='configured', index_folders=[str(self.company)], max_depth=1)
        state = fi.refresh_index(self.db, roots, options)
        self.assertEqual(state['count'], 2)
        self.assertEqual(len(state['changed_roots']), 1)
        options = self.opts(index_mode='configured', index_folders=[str(self.company)], max_depth=2)
        self.assertEqual(fi.refresh_index(self.db, roots, options)['count'], 3)

    def test_off_disables_scope_and_legacy_enabled_false(self):
        for options in (self.opts(index_mode='off', index_folders=[str(self.company)]),
                        self.opts(enabled=False, index_mode='configured', index_folders=[str(self.company)])):
            self.assertEqual(fi.index_mode(options), 'off')
            self.assertEqual(fi.resolve_roots(options), ([], []))

    def test_validation_and_reject_root(self):
        for values in ({'index_mode':'all'}, {'index_folders': 'not-a-list'},
                       {'max_depth':-1}, {'max_depth':True}, {'max_depth':101}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.opts(**values)
        for folder in (str(Path(os.sep)), 'not/an/absolute/path'):
            with self.subTest(folder=folder), self.assertRaises(ValueError):
                fi.resolve_roots(self.opts(index_mode='configured', index_folders=[folder]))

    def test_missing_cloud_folder_keeps_previous_snapshot(self):
        options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        roots, _ = fi.resolve_roots(options)
        fi.refresh_index(self.db, roots, options)
        offline = self.base / 'offline mapped share'
        options = self.opts(index_mode='configured', index_folders=[str(self.company), str(offline)])
        roots, warnings = fi.resolve_roots(options)
        self.assertTrue(warnings)
        self.assertEqual(len(roots), 2)
        result = fi.refresh_index(self.db, roots, options)
        self.assertFalse(result['applied'])
        self.assertEqual(fi.index_status(self.db)['count'], 3)

    def test_clear_index_removes_cache_only_and_supports_rebuild(self):
        options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        roots, _ = fi.resolve_roots(options)
        fi.refresh_index(self.db, roots, options)
        self.assertTrue(fi.clear_index(self.db))
        # Live Windows SQLite connections may hold the file open; the DB file
        # remains, but every table storing index data must be empty.
        self.assertTrue(self.db.is_file())
        self.assertIsNone(fi.index_status(self.db))
        self.assertEqual(fi.index_root_status(self.db), [])
        self.assertFalse(fi.search_index(self.db, 'root file'))
        with sqlite3.connect(self.db) as db:
            for table in ('files', 'index_roots', 'metadata'):
                self.assertEqual(db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0], 0)
        self.assertTrue((self.company / 'root file.md').is_file())
        self.assertTrue(fi.clear_index(self.db))  # idempotent even when DB is empty
        self.assertEqual(fi.refresh_index(self.db, roots, options)['count'], 3)
        self.assertEqual(len(fi.search_index(self.db, 'root file')), 1)

    def test_clear_with_a_second_open_sqlite_reader_in_wal_mode(self):
        """An open search connection must not cause Windows file-delete failure."""
        options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        roots, _ = fi.resolve_roots(options)
        fi.refresh_index(self.db, roots, options)
        with sqlite3.connect(self.db) as reader:
            self.assertEqual(reader.execute('PRAGMA journal_mode').fetchone()[0], 'wal')
            reader.execute('BEGIN')
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM files').fetchone()[0], 3)
            self.assertTrue(fi.clear_index(self.db))
            # A live reader can finish on its old snapshot, but new queries
            # will see an empty index immediately after the clear commits.
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM files').fetchone()[0], 3)
            self.assertEqual(fi.search_index(self.db, 'child report'), [])
            reader.commit()
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM files').fetchone()[0], 0)
        self.assertTrue(self.db.is_file())

    def test_clear_is_atomic_when_sqlite_write_fails(self):
        options = self.opts(index_mode='configured', index_folders=[str(self.company)])
        roots, _ = fi.resolve_roots(options)
        fi.refresh_index(self.db, roots, options)
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TRIGGER refuse_clear BEFORE DELETE ON metadata '
                       "BEGIN SELECT RAISE(ABORT, 'refuse'); END")
        with self.assertRaises(sqlite3.DatabaseError):
            fi.clear_index(self.db)
        # A failure during the third delete rolls back the first two.
        self.assertEqual(fi.index_status(self.db)['count'], 3)
        self.assertEqual(len(fi.index_root_status(self.db)), 1)
        self.assertEqual(len(fi.search_index(self.db, 'root file')), 1)

    def test_clear_legacy_schema_without_index_roots(self):
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE files(path TEXT PRIMARY KEY, name TEXT, '
                       'name_fold TEXT, directory TEXT, extension TEXT)')
            db.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT)')
            db.execute("INSERT INTO files VALUES('a.md','a.md','a.md','.','.md')")
            db.execute("INSERT INTO metadata VALUES('count','1')")
        self.assertTrue(fi.clear_index(self.db))
        self.assertIsNone(fi.index_status(self.db))
        self.assertEqual(fi.search_index(self.db, 'a.md'), [])
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM files').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM metadata').fetchone()[0], 0)

    def test_clear_missing_index_does_not_create_db(self):
        self.assertFalse(fi.clear_index(self.db))
        self.assertFalse(self.db.exists())

    def test_app_tray_wiring_and_live_index_mode_check(self):
        source = (Path(__file__).resolve().parents[1] / 'src/app.py').read_text(encoding='utf8')
        ast.parse(source)
        for fragment in ('file_index.resolve_roots(', 'file_index.index_mode(opts)',
                         'self.file_index_clear_action = traymenu.addAction(',
                         'def clear_file_index(self):',
                         'file_index.index_mode(self.file_index_settings) != \'off\''):
            self.assertIn(fragment, source)


if __name__ == '__main__':
    unittest.main()
