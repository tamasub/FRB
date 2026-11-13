"""studio_work_0269: Launch Add-only contract / no GUI dependency."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import (
    RegistrationError, category_record, eligible_parent, normalize_sources,
    records_for_sources, commit_add, mime_sources, studio_core_root,
)
from core import load


class FakeUrl:
    def __init__(self, data): self.data = data
    def isLocalFile(self): return self.data.startswith('file:')
    def toLocalFile(self): return self.data[5:]
    def toString(self): return self.data


class FakeMime:
    def __init__(self, urls=(), text='', formats=None):
        self._urls, self._text, self._formats = urls, text, formats or {}
    def hasUrls(self): return bool(self._urls)
    def urls(self): return [FakeUrl(u) for u in self._urls]
    def hasFormat(self, key): return key in self._formats
    def data(self, key): return self._formats[key]
    def hasText(self): return bool(self._text)
    def text(self): return self._text


class RegisterTest(unittest.TestCase):
    def test_title_and_record_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'日本語フォルダー'; folder.mkdir()
            f = folder/'ファイル.txt'; f.write_text('a', encoding='utf-8')
            sources = normalize_sources([
                {'value': str(folder)}, {'value': str(f)},
                {'value': 'https://example.com/my/page', 'title': 'Chrome ページ'},
                {'value': str(f)},
            ])
            self.assertEqual([x['kind'] for x in sources], ['directory','file','url'])
            rows = records_for_sources(sources)
            self.assertEqual([r['item_kind'] for r in rows], ['directory','command','command'])
            self.assertEqual(rows[0]['launch_browse_target'], str(folder.resolve()))
            self.assertEqual(rows[2]['launch_actions'][0]['launch_target'], 'https://example.com/my/page')
            self.assertEqual(rows[2]['icon_key'], 'globe')
            self.assertEqual(rows[2]['title'], 'Chrome ページ')

    def test_internet_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp)/'日本語タイトル.url'
            link.write_text('[InternetShortcut]\nURL=https://qiita.com/a\n',encoding='utf-8')
            source = normalize_sources([{'value': str(link)}])[0]
            self.assertEqual(source, {'kind':'url','value':'https://qiita.com/a','title':'日本語タイトル'})

    def test_url_mime(self):
        sources = mime_sources(FakeMime(urls=['https://zenn.dev/a'],text='Zenn 記事'))
        self.assertEqual(normalize_sources(sources)[0]['title'], 'Zenn 記事')
        self.assertEqual(mime_sources(FakeMime(formats={
            'application/x-qt-windows-mime;value="UniformResourceLocatorW"':
            'https://example.com/日本語'.encode('utf-16-le') + b'\x00\x00'
        }))[0]['value'], 'https://example.com/日本語')

    def test_unsupported_urls_and_missing_path(self):
        for value in ('javascript:alert(1)', 'file:///etc/passwd', '/missing-path-54321'):
            with self.assertRaises(RegistrationError): normalize_sources([{'value': value}])
        self.assertEqual(mime_sources(FakeMime(text='javascript:alert(1)')), [])
        with self.assertRaises(RegistrationError): category_record('   ')

    def test_parent_category_only(self):
        doc = load(ROOT/'config/frb_launch_data.json')
        eligible_parent(doc,'work','')
        eligible_parent(doc,'system','folders')
        with self.assertRaises(RegistrationError): eligible_parent(doc,'system','studio_dir')
        with self.assertRaises(RegistrationError): eligible_parent(doc,'not-page','')

    def test_cli_integration_on_temporary_copy(self):
        studio = os.environ.get('FRB_STUDIO_TEST_ROOT','')
        node = shutil.which('node')
        if not studio or not node:
            self.skipTest('Studio source / Node not supplied for integration test')
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)/'launch.json'
            shutil.copy2(ROOT/'config/frb_launch_data.json',data)
            original = data.read_bytes()
            self.assertNotIn('試験カテゴリー'.encode('utf-8'),original)
            result = commit_add(data,studio,'work','',[category_record('試験カテゴリー')])
            self.assertEqual(result['status'],'COMMITTED')
            result = commit_add(data,studio,'system','folders',records_for_sources([
                {'kind':'url','value':'https://example.com/new','title':'登録URL'},
                {'kind':'url','value':'https://zenn.dev/a','title':'Zenn'},
            ]))
            self.assertEqual(result['summary']['added'],2)
            modified = load(data)
            self.assertEqual(len(modified['items']),len(load(ROOT/'config/frb_launch_data.json')['items'])+3)
            self.assertEqual(modified['items'][-1]['title'],'Zenn')
            with self.assertRaises(RegistrationError):
                commit_add(data,studio,'system','studio_dir',[category_record('禁止')])
            self.assertEqual(load(data)['items'][-1]['title'],'Zenn')


if __name__ == '__main__': unittest.main()
