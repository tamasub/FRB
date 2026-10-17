"""Automated incremental index tests; temp folders only, no Windows UI."""
import ast
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import file_index as fi

class AutoIndexTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.p = Path(self.t.name)
        self.a = self.p / 'root_A'
        self.b = self.p / 'root_B'
        self.a.mkdir();self.b.mkdir()
        (self.a / 'first.ps1').write_text('a', encoding='utf8')
        (self.b / 'second.md').write_text('b', encoding='utf8')
        self.db = self.p / 'index.db'
        self.options = fi.load_options(self.p / 'missing.json')
        self.options['update_mode'] = 'auto'

    def update(self, roots=None, **kwargs):
        return fi.refresh_index(self.db, roots or [str(self.a),str(self.b)],self.options,**kwargs)

    def test_first_run_then_unchanged_files(self):
        result=self.update()
        self.assertTrue(result['root_set_changed'])
        self.assertEqual(len(result['changed_roots']),2)
        self.assertEqual(result['count'],2)
        first=fi.search_index(self.db,'first')
        self.assertEqual(len(first),1)
        result2=self.update()
        self.assertFalse(result2['root_set_changed'])
        self.assertEqual(result2['changed_roots'],[])
        self.assertEqual(len(result2['unchanged_roots']),2)
        self.assertEqual(result2['count'],2)
        self.assertEqual(fi.search_index(self.db,'first'),first)

    def test_only_changed_root_updated_and_removed_file_purged(self):
        self.update()
        (self.a / 'new.xlsx').write_text('x')
        check=self.update()
        self.assertEqual(check['changed_roots'],[str(self.a)])
        self.assertEqual(check['unchanged_roots'],[str(self.b)])
        self.assertEqual(len(fi.search_index(self.db,'new.xlsx')),1)
        (self.a / 'first.ps1').unlink()
        check=self.update()
        self.assertEqual(check['changed_roots'],[str(self.a)])
        self.assertEqual(fi.search_index(self.db,'first.ps1'),[])
        self.assertEqual(len(fi.search_index(self.db,'second.md')),1)

    def test_case_only_filename_change_updates_display_name(self):
        self.update()
        (self.a / 'first.ps1').rename(self.a / 'First.ps1')
        result=self.update()
        self.assertEqual(result['changed_roots'],[str(self.a)])
        self.assertEqual([hit['name'] for hit in fi.search_index(self.db,'first.ps1')], ['First.ps1'])

    def test_root_status_timestamps(self):
        self.update()
        rows=fi.index_root_status(self.db)
        self.assertEqual(len(rows),2)
        self.assertTrue(all(r['updated_at'] and r['checked_at'] for r in rows))

    def test_content_edit_no_reindex_needed(self):
        self.update()
        (self.a/'first.ps1').write_text('different source content')
        self.assertEqual(self.update()['changed_roots'],[])

    def test_option_change_triggers_root_refresh_even_when_paths_same(self):
        self.update()
        self.options['extensions']=['.md']
        changed=self.update()
        self.assertEqual(set(changed['changed_roots']),{str(self.a),str(self.b)})
        self.assertEqual(fi.search_index(self.db,'first.ps1'),[])
        self.assertEqual(len(fi.search_index(self.db,'second.md')),1)

    def test_root_topology_change_commits_whole_new_set(self):
        self.update()
        (self.p/'top.py').write_text('test')
        changed=fi.refresh_index(self.db,[str(self.p)],self.options)
        self.assertTrue(changed['root_set_changed'])
        self.assertEqual(len(fi.search_index(self.db,'top.py')),1)
        self.assertEqual(len(fi.search_index(self.db,'first.ps1')),1)
        self.assertEqual(len(fi.search_index(self.db,'second.md')),1)
        self.assertEqual(len(fi.index_status(self.db)['roots']),1)
        unchanged=fi.refresh_index(self.db,[str(self.p)],self.options)
        self.assertFalse(unchanged['root_set_changed'])

    def test_missing_root_does_not_delete_old_files(self):
        self.update()
        (self.a/'first.ps1').unlink()
        self.a.rmdir()
        changed=self.update()
        self.assertEqual(changed['failed_roots'],[str(self.a)])
        self.assertEqual(changed['changed_roots'],[])
        self.assertEqual(len(fi.search_index(self.db,'first.ps1')),1)
        self.assertTrue(changed['scan_warnings'])

    def test_topology_change_failure_maintains_previous_index(self):
        self.update()
        missing=self.p/'offline'
        state=self.update([str(self.a),str(missing)])
        self.assertFalse(state['applied'])
        self.assertEqual(fi.index_status(self.db)['count'],2)
        self.assertEqual(len(fi.search_index(self.db,'second.md')),1)
        self.assertEqual(state['changed_roots'],[])

    def test_old_index_migrates_only_on_success(self):
        fi.build_index(self.db,[str(self.a)],self.options)
        self.assertEqual(len(fi.search_index(self.db,'first.ps1')),1)
        failure=self.update([str(self.a),str(self.p/'offline')])
        self.assertFalse(failure['applied'])
        self.assertEqual(fi.index_status(self.db)['index_version'] if 'index_version' in fi.index_status(self.db) else 1,1)
        self.assertEqual(len(fi.search_index(self.db,'first.ps1')),1)
        success=self.update()
        self.assertTrue(success['applied'])
        self.assertEqual(fi.index_status(self.db)['index_version'],2)
        self.assertEqual(len(fi.search_index(self.db,'second.md')),1)

    def test_cancel_retains_old_snapshot(self):
        self.update()
        (self.a/'new.ps1').write_text('')
        with self.assertRaises(InterruptedError):
            self.update(cancelled=lambda: True)
        self.assertEqual(fi.search_index(self.db,'new.ps1'),[])

    def test_one_pass_per_root_and_worker_limit(self):
        visited=[]
        real=fi._root_scan
        def wrapping(root,opts,cancelled=None):
            visited.append(str(root))
            return real(root,opts,cancelled)
        with patch.object(fi,'_root_scan',side_effect=wrapping):
            self.update()
        self.assertCountEqual(visited,[str(self.a),str(self.b)])

    def test_wal_read_during_update(self):
        self.update()
        with sqlite3.connect(self.db) as reader:
            reader.execute('BEGIN')
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM files').fetchone()[0],2)
            (self.a/'new.json').write_text('{}')
            state=self.update()
            self.assertEqual(state['count'],3)
            # Same reader transaction sees snapshot; fresh reader sees new rows.
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM files').fetchone()[0],2)
        self.assertEqual(len(fi.search_index(self.db,'new.json')),1)

    def test_unavailable_registered_root_kept_for_failure(self):
        data={'pages':[{'page_id':'p'}], 'items':[{'page_id':'p','item_kind':'directory','enabled':True,
              'launch_browse_target':str(self.p/'offline')} ]}
        roots,warnings=fi.registered_roots(data,lambda x:x,include_unavailable=True)
        self.assertEqual(roots,[str(self.p/'offline')])
        self.assertTrue(warnings)

    def test_options_validates_auto_configuration(self):
        path=self.p/'config.json'
        path.write_text(json.dumps({'update_mode':'auto','auto_update':{'check_interval_minutes':15}}))
        self.assertEqual(fi.load_options(path)['auto_update']['check_interval_minutes'],15)
        path.write_text(json.dumps({'update_mode':'auto','auto_update':{'max_scan_workers':0}}))
        with self.assertRaises(ValueError):fi.load_options(path)

    def test_app_timer_and_manual_update_wired(self):
        source=(Path(__file__).parents[1]/'app.py').read_text(encoding='utf8')
        ast.parse(source)
        self.assertIn('self.file_index_check_timer.timeout.connect(self.auto_refresh_file_index)',source)
        self.assertIn('file_index.refresh_index(',source)
        self.assertIn('manual=False',source)
        self.assertIn("self._file_index_cancel.set()",source)

if __name__=='__main__':unittest.main()
