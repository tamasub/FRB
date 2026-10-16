"""Editable bookmark-root regression coverage; runs without PySide6."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import browser_bookmarks as bm
from core import load, validate
from ordering import save_order
from prepare_launch_home import prepare, READY

SAMPLE = Path(__file__).resolve().parents[1] / 'config' / 'frb_launch_sample_data_v0_1.json'


class BookmarkCategoryConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.config = self.root / 'config' / SAMPLE.name
        self.config.parent.mkdir(parents=True)
        self.data = load(SAMPLE)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data):
        self.config.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    def test_shipped_category_is_studio_editable_and_not_runtime_generated(self):
        root = next(r for r in self.data['items'] if r['item_id'] == bm.ROOT_ID)
        self.assertEqual(root['launch_source'], 'browser_bookmarks')
        self.assertEqual(root['page_id'], 'windows')
        self.assertFalse(root.get('_browser_bookmark', False))
        self.assertTrue(self.data[bm.BOOTSTRAP_FIELD])
        attached = bm.attach(self.data, 'chrome', [{'directory':'Default', 'browser_profile':'Default',
                              'roots':[{'name':'ブックマーク バー', 'children':[
                                  {'type':'url', 'name':'FRB', 'url':'https://example.org/frb'}]}]}])
        self.assertEqual(next(r for r in attached['items'] if r['item_id'] == bm.ROOT_ID), root)
        self.assertEqual(sum(r['item_id'] == bm.ROOT_ID for r in attached['items']), 1)
        self.assertTrue(any(r.get('title') == 'FRB' for r in attached['items']))
        validate(attached)

    def test_legacy_migration_keeps_customized_json_and_creates_backup(self):
        legacy = copy.deepcopy(self.data)
        legacy['items'] = [x for x in legacy['items'] if x['item_id'] != bm.ROOT_ID]
        legacy.pop(bm.BOOTSTRAP_FIELD, None)
        existing = next(r for r in legacy['items'] if r['page_id'] == 'windows' and not r.get('parent_item_id'))
        existing['title'] = '自分でつけた名前'
        existing['sort_order'] = 777
        self.write(legacy)
        self.assertTrue(bm.ensure_category_file(self.config))
        updated = load(self.config)
        old_row = next(r for r in updated['items'] if r['item_id'] == existing['item_id'])
        self.assertEqual(old_row, existing)
        self.assertTrue(any(r['item_id'] == bm.ROOT_ID for r in updated['items']))
        backup = list((self.root / 'backups').glob('launch_before_bookmarks_*.json'))
        self.assertEqual(len(backup), 1)
        self.assertEqual(json.loads(backup[0].read_text(encoding='utf-8')), legacy)
        self.assertFalse(bm.ensure_category_file(self.config))
        self.assertEqual(len(list((self.root / 'backups').glob('*'))), 1)

    def test_persist_order_works_with_live_bookmark_children(self):
        self.write(self.data)
        root = next(r for r in self.data['items'] if r['item_id'] == bm.ROOT_ID)
        siblings = sorted((r for r in self.data['items'] if r['page_id'] == 'windows'
                           and not r.get('parent_item_id') and r.get('enabled', True)),
                          key=lambda r:r['sort_order'])
        ids = [r['item_id'] for r in siblings]
        self.assertIn(root['item_id'], ids)
        reordered, _ = save_order(self.config, self.config.stat().st_mtime_ns, 'windows', '', list(reversed(ids)))
        self.assertEqual([r['item_id'] for r in sorted((r for r in reordered['items']
                          if r['page_id']=='windows' and not r.get('parent_item_id')),
                          key=lambda r:r['sort_order'])], list(reversed(ids)))
        self.assertEqual(next(r for r in reordered['items'] if r['item_id']==bm.ROOT_ID)['launch_source'], 'browser_bookmarks')

    def test_title_position_enabled_and_parent_from_json(self):
        cfg = copy.deepcopy(self.data)
        root = next(r for r in cfg['items'] if r['item_id'] == bm.ROOT_ID)
        root['title'] = 'お気に入り世界'
        root['page_id'] = 'work'
        root['sort_order'] = 7
        profiles = [{'directory':'Default','browser_profile':'Default',
                    'roots':[{'name':'ブックマーク バー','children':[{'type':'url','name':'ABC','url':'https://example.org'}]}]}]
        result = bm.attach(cfg, 'edge', profiles)
        self.assertEqual(next(r for r in result['items'] if r['item_id'] == bm.ROOT_ID)['title'], 'お気に入り世界')
        site = next(r for r in result['items'] if r['title'] == 'ABC')
        self.assertEqual(site['page_id'], 'work')
        self.assertEqual(site['launch_actions'][0]['launch_browser'], 'edge')
        root['enabled'] = False
        disabled = bm.attach(cfg, 'edge', profiles)
        self.assertFalse(any(r.get('_browser_bookmark') for r in disabled['items']))
        validate(disabled)

    def test_removed_category_is_not_recreated_after_bootstrap(self):
        cfg = copy.deepcopy(self.data)
        cfg['items'] = [r for r in cfg['items'] if r['item_id'] != bm.ROOT_ID]
        self.write(cfg)
        self.assertFalse(bm.ensure_category_file(self.config))
        self.assertFalse(any(r['item_id'] == bm.ROOT_ID for r in load(self.config)['items']))

    def test_existing_custom_source_category_prevents_duplicate(self):
        cfg = copy.deepcopy(self.data)
        cfg.pop(bm.BOOTSTRAP_FIELD, None)
        custom = next(r for r in cfg['items'] if r['item_id'] == bm.ROOT_ID)
        custom['item_id'] = 'my_bookmarks'
        custom['title'] = '好きな名前'
        self.write(cfg)
        self.assertTrue(bm.ensure_category_file(self.config))  # marker only
        updated=load(self.config)
        self.assertEqual(len([r for r in updated['items'] if r.get('launch_source')=='browser_bookmarks']), 1)
        self.assertEqual(next(r for r in updated['items'] if r.get('launch_source')=='browser_bookmarks')['title'], '好きな名前')
        self.assertFalse(bm.ensure_category_file(self.config))

    def test_ready_build_migrates_existing_home_without_reset(self):
        cfg = copy.deepcopy(self.data)
        cfg.pop(bm.BOOTSTRAP_FIELD, None)
        cfg['items'] = [r for r in cfg['items'] if r['item_id'] != bm.ROOT_ID]
        self.write(cfg)
        (self.root / READY).write_text('ready', encoding='utf-8')
        self.assertIsNone(prepare(self.root))
        self.assertTrue(bm.has_category(load(self.config)))
        self.assertEqual(len(list((self.root / 'backups').glob('launch_before_bookmarks_*.json'))), 1)

if __name__ == '__main__':
    unittest.main()
