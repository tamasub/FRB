"""Integration: Python subprocess → actual Node CLI → disposable JSON file."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.change_core.python_client import file_sha256, run_changeset

ROOT = Path(__file__).resolve().parents[2]
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node.js is not available in test environment')
class PythonChangeSetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='studio-python-')
        self.addCleanup(self.tmp.cleanup)
        tmp = Path(self.tmp.name)
        self.document = tmp / 'document.json'
        self.document.write_text(json.dumps({
            'pages': [{'page_id': 'work', 'title': 'work'}],
            'items': [{'item_id': 'folders', 'parent_item_id': '', 'page_id': 'work',
                       'sort_order': 10, 'item_kind': 'category', 'title': 'Folder'}]
        }, ensure_ascii=False), encoding='utf-8')
        self.config = tmp / 'config.json'
        self.config.write_text(json.dumps({
            'schema_version': 'studio_change_core_config_v0_1',
            'documents': {'approved_launch_config': {
                'path': str(self.document),
                'view_def': 'launch/frb_launch_maintenance_view_def_v0_1.json',
                'view_id': 'items_view', 'section_ids': ['items']
            }}
        }), encoding='utf-8')
        self.base = file_sha256(self.document)
        self.request = {
            'schema_version': 'studio_changeset_v0_1', 'request_id': 'python-1',
            'mode': 'dry_run', 'document_ref': 'approved_launch_config',
            'base_sha256': self.base,
            'view_def': 'launch/frb_launch_maintenance_view_def_v0_1.json',
            'view_id': 'items_view',
            'operations': [{'operation': 'add', 'section_id': 'items',
                            'placement': {'group_id': 'work', 'parent_id': 'folders', 'position': 'end'},
                            'records': [
                                {'title': 'テストA', 'item_kind': 'command', 'launch_actions': []},
                                {'title': 'テストB', 'item_kind': 'command', 'launch_actions': []}
                            ]}]
        }

    def call(self):
        return run_changeset(self.request, node_executable=NODE,
                             cli_path=ROOT / 'tools/change_core/cli.mjs', config_path=self.config)

    def test_preview_commit_and_conflict(self):
        preview = self.call()
        self.assertEqual(preview['status'], 'PREVIEW')
        self.assertEqual(file_sha256(self.document), self.base)
        self.assertEqual(preview['summary']['added'], 2)
        self.request['mode'] = 'commit'
        committed = self.call()
        self.assertEqual(committed['status'], 'COMMITTED')
        self.assertTrue(committed['saved'])
        self.assertEqual(committed['new_sha256'], file_sha256(self.document))
        self.assertEqual([r['title'] for r in json.loads(self.document.read_text('utf8'))['items'][1:]],
                         ['テストA', 'テストB'])
        conflict = self.call()
        self.assertEqual(conflict['status'], 'CONFLICT')
        self.assertFalse(conflict['saved'])
        self.assertEqual(len(json.loads(self.document.read_text('utf8'))['items']), 3)

    def test_bad_parent_rejected_without_change(self):
        self.request['mode'] = 'commit'
        self.request['operations'][0]['placement']['parent_id'] = 'missing'
        result = self.call()
        self.assertEqual(result['status'], 'REJECTED')
        self.assertFalse(result['saved'])
        self.assertEqual(file_sha256(self.document), self.base)


if __name__ == '__main__':
    unittest.main()
