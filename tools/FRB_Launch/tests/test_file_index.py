"""File index tests require no Qt and must never scan outside test roots."""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from file_index import (load_options, minimize_roots, registered_roots, build_index,
                        search_index, index_status, launch_steps, studio_managed_json)


class FileIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'work'
        self.source.mkdir()
        self.folder = self.source / 'sub'
        self.folder.mkdir()
        for filename in ('build_me.bat','analysis.PY','start.ps1','data.JSON',
                         'report.xlsx','notes.md','my_view_def.json','skip.txt',
                         'folder-name-only-is-in-path.xlsx'):
            (self.folder / filename).write_text('x', encoding='utf8')
        self.out = self.root / 'file_index.db'
        self.options = load_options(self.root / 'no-such-file.json')
        self.config = {'pages': [{'page_id':'work','enabled':True}],
                       'items': [{'item_id':'top','page_id':'work','item_kind':'directory',
                                  'enabled':True,'launch_browse_target':str(self.source)},
                                 {'item_id':'child','page_id':'work','item_kind':'directory',
                                  'enabled':True,'launch_browse_target':str(self.folder)}]}

    def test_defaults_include_six_extensions_and_manual_only(self):
        self.assertEqual(set(self.options['extensions']), {'.bat','.py','.ps1','.json','.xlsx','.md'})
        self.assertEqual(self.options['update_mode'], 'manual')

    def test_options_override(self):
        p=self.root/'config.json';p.write_text(json.dumps({'extensions':['.txt','.MD'], 'search_limit':12}),encoding='utf8')
        loaded=load_options(p)
        self.assertEqual(loaded['extensions'],['.md','.txt'])
        self.assertEqual(loaded['search_limit'],12)
        p.write_text(json.dumps({'update_mode':'auto'}),encoding='utf8')
        self.assertEqual(load_options(p)['update_mode'], 'auto')

    def test_minimize_registered_roots(self):
        roots,warnings=registered_roots(self.config,lambda x:x)
        self.assertEqual(roots,[str(self.source)])
        self.assertFalse(warnings)
        self.assertEqual(minimize_roots([r'F:\FRB\tools','F:\\',r'F:\FRB',r'D:\Work']), ['F:\\',r'D:\Work'])
        self.assertEqual(minimize_roots([r'F:\FRB',r'F:\FRB_docs']), [r'F:\FRB',r'F:\FRB_docs'])

    def test_unavailable_root_is_not_widened(self):
        self.config['items'].append({'item_id':'gone','page_id':'work','item_kind':'directory',
                                     'launch_browse_target':str(self.root/'gone')})
        roots,warnings=registered_roots(self.config,lambda x:x)
        self.assertEqual(roots,[str(self.source)])
        self.assertEqual(len(warnings),1)

    def test_scan_and_filter(self):
        (self.source/'.venv').mkdir();(self.source/'.venv'/'evil.py').write_text('')
        (self.source/'dist').mkdir();(self.source/'dist'/'other.py').write_text('')
        stats=build_index(self.out,[str(self.source)],self.options)
        self.assertEqual(stats['count'],7)
        self.assertEqual(index_status(self.out)['count'],7)
        self.assertEqual(len(search_index(self.out,'.py')),1)
        self.assertEqual(search_index(self.out,'evil'),[])
        self.assertEqual(search_index(self.out,'view_def'),[])
        self.assertEqual([x['name'] for x in search_index(self.out,'report')],['report.xlsx'])
        self.assertEqual([x['name'] for x in search_index(self.out,'folder-name-only-is-in-path')], ['folder-name-only-is-in-path.xlsx'])
        self.assertEqual(len(search_index(self.out,'sub')),7)
        # AND terms may match in different parts of the full file path.
        self.assertEqual([x['name'] for x in search_index(self.out,'report sub')], ['report.xlsx'])
        self.assertEqual([x['name'] for x in search_index(self.out,'sub report*.xlsx')], ['report.xlsx'])

    def test_existing_index_can_search_paths_without_rebuild(self):
        # Database schema from prior file-index releases already stores path.
        with sqlite3.connect(self.out) as db:
            db.execute('CREATE TABLE files(path TEXT PRIMARY KEY COLLATE NOCASE, name TEXT NOT NULL, name_fold TEXT NOT NULL, directory TEXT NOT NULL, extension TEXT NOT NULL)')
            path = r'F:\FRB\tools\zip_app\make_FRB.ps1'
            db.execute('INSERT INTO files VALUES (?, ?, ?, ?, ?)',
                       (path, 'make_FRB.ps1', 'make_frb.ps1', r'F:\FRB\tools\zip_app', '.ps1'))
        hits = search_index(self.out, 'make zip_app')
        self.assertEqual([hit['path'] for hit in hits], [path])
        self.assertEqual([hit['path'] for hit in search_index(self.out, r'FRB\tools *.ps1')], [path])

    def test_view_def_always_excluded_even_if_optional_list_is_cleared(self):
        opts = {**self.options, 'exclude_name_contains': []}
        build_index(self.out, [str(self.source)], opts)
        self.assertEqual(search_index(self.out, 'view_def'), [])

    def test_full_path_search_with_and_terms(self):
        (self.folder / 'plain.md').write_text('hello',encoding='utf8')
        build_index(self.out,[str(self.source)],self.options)
        # Folder-only keywords now match, but can be narrowed by filename.
        self.assertEqual(len(search_index(self.out,self.source.name)),8)
        self.assertEqual([hit['name'] for hit in search_index(self.out,'sub plain')], ['plain.md'])
        self.assertEqual([hit['name'] for hit in search_index(self.out,'SUB *.MD')], ['notes.md', 'plain.md'])
        self.assertEqual([hit['name'] for hit in search_index(self.out,'sub plain*.ps1')], [])
        # SQL wildcards retain their literal meaning in user input.
        self.assertEqual(search_index(self.out,'foo%'),[])
        self.assertEqual(search_index(self.out,'foo_'),[])

    def test_successful_replace_and_failed_build_preserves_previous(self):
        build_index(self.out,[str(self.source)],self.options)
        before=self.out.read_bytes()
        with self.assertRaises(ValueError):build_index(self.out,[],self.options)
        self.assertEqual(before,self.out.read_bytes())
        with self.assertRaises(FileNotFoundError):build_index(self.out,[str(self.root/'gone')],self.options)
        self.assertEqual(before,self.out.read_bytes())
        (self.folder/'new.py').write_text('')
        build_index(self.out,[str(self.source)],self.options)
        self.assertEqual(len(search_index(self.out,'new.py')),1)

    def test_skip_symlink(self):
        shortcut=self.source/'external'
        try:shortcut.symlink_to(self.root, target_is_directory=True)
        except (OSError,NotImplementedError):self.skipTest('Cannot make symlink')
        build_index(self.out,[str(self.source)],self.options)
        self.assertEqual(len(search_index(self.out,'notes.md')),1)

    def test_studio_json_detect_only_resolvable_view_def(self):
        studio=self.root/'studio'; defs=studio/'defs'/'launch';defs.mkdir(parents=True)
        (defs/'sample.json').write_text('{}',encoding='utf8')
        (studio/'NativeShell'/'_publish').mkdir(parents=True)
        (studio/'NativeShell'/'_publish'/'FRBStudio.NativeShell.exe').write_text('',encoding='utf8')
        target=self.source/'managed.json';target.write_text(json.dumps({'view_def':'launch/sample.json'}),encoding='utf8')
        ordinary=self.source/'ordinary.json';ordinary.write_text(json.dumps({'view_def':'launch/missing.json'}),encoding='utf8')
        self.assertTrue(studio_managed_json(target, studio))
        self.assertFalse(studio_managed_json(ordinary, studio))
        steps=launch_steps(target,studio)
        self.assertEqual(steps[0]['launch_action_type'],'Run')
        self.assertEqual(steps[0]['launch_arguments'], ['--open-json='+str(target)])
        self.assertEqual(launch_steps(ordinary,studio)[0]['launch_action_type'],'Open')

    def test_extension_actions(self):
        script=self.folder/'analysis.PY'
        self.assertEqual(launch_steps(script)[0]['launch_program'], 'py.exe')
        self.assertEqual(launch_steps(self.folder/'start.ps1')[0]['launch_arguments'][0],'-NoProfile')
        for ext in ('.xlsx','.bat','.md','.json'):
            self.assertEqual(launch_steps(self.folder/('abc'+ext))[0]['launch_action_type'],'Open')

if __name__ == '__main__': unittest.main()
