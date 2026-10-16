"""Pure-Python browser import regression tests (also run without PySide6)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import browser_bookmarks as bm
from core import load, Expander, searchable_rows, validate
import windows

CONFIG = Path(__file__).resolve().parents[1] / 'config' / 'frb_launch_sample_data_v0_1.json'


class BrowserBookmarksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.chrome = self.root/'Google'/'Chrome'/'User Data'/'Default'/'Bookmarks'
        self.edge = self.root/'Microsoft'/'Edge'/'User Data'/'Default'/'Bookmarks'
        self.chrome.parent.mkdir(parents=True)
        self.edge.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def doc():
        return {'roots': {'bookmark_bar': {'children': [
            {'type': 'folder', 'name': '研究', 'id': '10', 'children': [
                {'type':'url','name':'資料','url':'https://example.org/a%20b?x=%E3%81','id':'11'},
                {'type':'url','name':'危険','url':'javascript:alert(1)','id':'12'},
            ]},
            {'type':'url','name':'ニュース','url':'https://news.example.com','id':'13'}]},
            'other': {'children': [{'type':'url','name':'その他','url':'https://other.example.com','id':'14'}]},
            'synced': {'children': []}}}

    def write(self, path, doc=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.doc() if doc is None else doc,ensure_ascii=False), encoding='utf-8')

    def test_chrome_and_edge_select_separately_and_preserve_hierarchy(self):
        self.write(self.chrome)
        self.write(self.edge, {'roots': {'bookmark_bar': {'children': [
            {'type':'url','name':'Edge専用','url':'https://microsoft.com'}]}}})
        chrome, errors = bm.read('chrome', self.root)
        self.assertFalse(errors)
        data = bm.attach(load(CONFIG), 'chrome', chrome)
        validate(data)
        root = next(x for x in data['items'] if x['item_id'] == bm.ROOT_ID)
        self.assertIn('Chrome',root['description'])
        shelf = next(x for x in data['items'] if x['parent_item_id'] == bm.ROOT_ID)
        self.assertEqual(shelf['title'], 'ブックマーク バー')
        folder = next(x for x in data['items'] if x['parent_item_id'] == shelf['item_id'])
        self.assertEqual(folder['title'], '研究')
        site = next(x for x in data['items'] if x.get('title') == '資料')
        self.assertEqual(site['parent_item_id'], folder['item_id'])
        step = site['launch_actions'][0]
        self.assertEqual(step['launch_browser'],'chrome')
        self.assertEqual(step['launch_browser_profile'],'Default')
        self.assertEqual(Expander(data).expand(step['launch_target']), 'https://example.org/a%20b?x=%E3%81')
        self.assertFalse(any(x.get('title')=='危険' for x in data['items']))
        self.assertTrue(any(x.get('title')=='資料' for x,_ in searchable_rows(data,'資料')))
        edge, errors = bm.read('edge', self.root)
        new = bm.attach(data,'edge',edge)
        self.assertFalse(any(x.get('title') == '資料' for x in new['items']))
        self.assertTrue(any(x.get('title') == 'Edge専用' for x in new['items']))
        self.assertEqual(sum(x['item_id']==bm.ROOT_ID for x in new['items']),1)

    def test_nonstandard_profile_folder_detected_automatically(self):
        custom=self.chrome.parents[1]/'Research User'/'Bookmarks'
        self.write(custom)
        self.assertEqual(bm.bookmark_files('chrome', self.root),[custom])
        profiles, errors=bm.read('chrome',self.root)
        self.assertFalse(errors)
        self.assertEqual(profiles[0]['directory'],'Research User')
        data=bm.attach(load(CONFIG),'chrome',profiles)
        self.assertTrue(any(x.get('title')=='資料' for x in data['items']))

    def test_account_bookmarks_only_signed_in_chrome(self):
        """Chrome 153+ may store signed-in bookmarks only in AccountBookmarks."""
        account = self.chrome.with_name('AccountBookmarks')
        self.write(account)
        self.assertFalse(self.chrome.exists())
        self.assertEqual(bm.bookmark_files('chrome', self.root), [account])
        profiles, errors = bm.read('chrome', self.root)
        self.assertFalse(errors)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['browser_profile'], 'Default')
        data = bm.attach(load(CONFIG), 'chrome', profiles)
        validate(data)
        shelf = next(x for x in data['items'] if x['parent_item_id'] == bm.ROOT_ID)
        self.assertEqual(shelf['title'], 'ブックマーク バー')
        site = next(x for x in data['items'] if x.get('title') == '資料')
        self.assertEqual(site['launch_actions'][0]['launch_browser_profile'], 'Default')
        self.assertEqual(len(bm.signature('chrome', self.root)), 1)

    def test_account_and_local_combined_without_duplicate_profile(self):
        """Local + signed-in trees stay separate but use the same Chrome profile."""
        self.write(self.chrome, {'roots': {'bookmark_bar': {'children': [
            {'type': 'url', 'name': 'ローカルページ', 'url': 'https://local.example/'}]}}})
        account = self.chrome.with_name('AccountBookmarks')
        self.write(account, {'roots': {'bookmark_bar': {'children': [
            {'type': 'url', 'name': 'アカウントページ', 'url': 'https://account.example/'}]}}})
        self.assertEqual(bm.bookmark_files('chrome', self.root), [self.chrome, account])
        profiles, errors = bm.read('chrome', self.root)
        self.assertFalse(errors)
        self.assertEqual(len(profiles), 1)
        self.assertEqual([x['name'] for x in profiles[0]['roots']],
                         ['ローカル: ブックマーク バー', 'アカウント: ブックマーク バー'])
        data = bm.attach(load(CONFIG), 'chrome', profiles)
        validate(data)
        for name in ('ローカルページ', 'アカウントページ'):
            item = next(x for x in data['items'] if x.get('title') == name)
            self.assertEqual(item['launch_actions'][0]['launch_browser_profile'], 'Default')
        before = bm.signature('chrome', self.root)
        account.write_text(account.read_text(encoding='utf-8') + ' ', encoding='utf-8')
        self.assertNotEqual(bm.signature('chrome', self.root), before)

    def test_mixed_profiles_account_and_local(self):
        self.write(self.chrome.with_name('AccountBookmarks'))
        second = self.chrome.parents[1] / 'Profile 1' / 'Bookmarks'
        self.write(second)
        profiles, errors = bm.read('chrome', self.root)
        self.assertFalse(errors)
        self.assertEqual([p['directory'] for p in profiles], ['Default', 'Profile 1'])
        data = bm.attach(load(CONFIG), 'chrome', profiles)
        validate(data)
        self.assertEqual(len([x for x in data['items'] if x.get('title') == '資料']), 2)

    def test_two_profiles_kept_separate(self):
        self.write(self.chrome)
        profile2 = self.chrome.parents[1]/'Profile 2'/'Bookmarks'
        self.write(profile2)
        profiles, errors = bm.read('chrome', self.root)
        self.assertFalse(errors)
        self.assertEqual([p['directory'] for p in profiles], ['Default','Profile 2'])
        data = bm.attach(load(CONFIG),'chrome',profiles)
        profile_nodes=[x for x in data['items'] if x['parent_item_id']==bm.ROOT_ID]
        self.assertEqual([x['title'] for x in profile_nodes], ['Default','Profile 2'])
        sites = [x for x in data['items'] if x.get('title')=='資料']
        self.assertEqual({x['launch_actions'][0]['launch_browser_profile'] for x in sites}, {'Default','Profile 2'})
        self.assertEqual(len({x['item_id'] for x in sites}), 2)

    def test_signature_detects_modification(self):
        self.write(self.chrome)
        before=bm.signature('chrome',self.root)
        self.assertEqual(len(before),1)
        self.chrome.write_text('{}')
        after=bm.signature('chrome',self.root)
        self.assertNotEqual(before,after)
        self.assertEqual(bm.signature('edge',self.root),())

    def test_missing_and_corrupt_files_do_not_crash(self):
        self.assertEqual(bm.read('edge',self.root), ([],[]))
        self.chrome.write_text('{bad json',encoding='utf-8')
        profiles,errors=bm.read('chrome',self.root)
        self.assertFalse(profiles)
        self.assertEqual(len(errors),1)

    def test_existing_user_config_unchanged_and_installed_apps_untouched(self):
        original=CONFIG.read_bytes()
        self.write(self.chrome)
        profiles,_=bm.read('chrome',self.root)
        data=bm.attach(load(CONFIG),'chrome',profiles)
        self.assertEqual(CONFIG.read_bytes(),original)
        self.assertTrue(any(r['item_id']=='installed_apps' for r in data['items']))
        twice=bm.attach(data,'chrome',profiles)
        self.assertEqual(len(twice['items']),len(data['items']))

    def test_manual_json_outside_default_browser_directory(self):
        custom = self.root/'portable'/'my_chrome_bookmarks.json'
        self.write(custom)
        self.assertFalse(bm.bookmark_files('chrome', self.root, str(self.root/'missing')))
        self.assertEqual(bm.bookmark_files('chrome', self.root, str(custom)), [custom])
        profiles, errors = bm.read('chrome', self.root, str(custom))
        self.assertFalse(errors)
        self.assertEqual(profiles[0]['browser_profile'], '')
        data = bm.attach(load(CONFIG),'chrome',profiles)
        validate(data)
        site=next(x for x in data['items'] if x.get('title')=='資料')
        self.assertEqual(site['launch_actions'][0]['launch_browser_profile'], '')
        first=bm.signature('chrome',self.root,str(custom))
        custom.write_text(json.dumps({'roots': {'bookmark_bar': {'children': []}}}), encoding='utf-8')
        self.assertNotEqual(first,bm.signature('chrome',self.root,str(custom)))

    def test_manual_html_export_retains_folders(self):
        path=self.root/'import.html'
        path.write_text("""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p><DT><H3>釣り実験</H3>
<DL><p><DT><A HREF="https://example.org/frb?x=1&amp;y=2">FRB記事</A>
<DT><H3>測定</H3><DL><p><DT><A HREF="https://example.org/fft">FFT</A></DL><p>
<DT><A HREF="javascript:alert(1)">危険</A>
</DL><p></DL><p>""",encoding='utf-8')
        profiles,errors=bm.read('edge', self.root,str(path))
        self.assertFalse(errors)
        data=bm.attach(load(CONFIG),'edge',profiles)
        validate(data)
        topics={x.get('title'):x for x in data['items']}
        self.assertEqual(topics['釣り実験']['item_kind'],'category')
        self.assertEqual(topics['FRB記事']['parent_item_id'],topics['釣り実験']['item_id'])
        self.assertEqual(topics['FFT']['parent_item_id'],topics['測定']['item_id'])
        self.assertEqual(topics['FRB記事']['launch_actions'][0]['launch_target'], 'https://example.org/frb?x=1&y=2')
        self.assertNotIn('危険',topics)

    def test_browser_launch_preserves_profile_and_checks_scheme(self):
        with patch.object(windows,'IS_WINDOWS',True), patch.object(windows,'chrome_path',return_value=r'C:\\chrome.exe'), patch.object(windows,'edge_path',return_value=r'C:\\edge.exe'), patch('subprocess.Popen') as popen:
            windows.open_browser('https://example.org/','chrome','Profile 2')
            popen.assert_called_once_with([r'C:\\chrome.exe','--profile-directory=Profile 2','https://example.org/'])
            popen.reset_mock()
            windows.open_browser('https://example.org/','edge','Default')
            popen.assert_called_once_with([r'C:\\edge.exe','--profile-directory=Default','https://example.org/'])
            with self.assertRaises(ValueError):windows.open_browser('javascript:alert(1)','edge')
            with self.assertRaises(ValueError):windows.open_browser('https://a.com','chrome','--incognito')


if __name__=='__main__':unittest.main()
