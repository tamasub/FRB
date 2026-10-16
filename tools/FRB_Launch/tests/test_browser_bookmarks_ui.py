"""Bookmark cascade and browser switch behavior (requires PySide6)."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import app as module
except ImportError:
    module = None


@unittest.skipUnless(module is not None, 'PySide6 required for GUI tests')
class BrowserBookmarksUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.localappdata = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'LOCALAPPDATA': self.temp.name})
        self.env.start()
        folder = self.localappdata/'Google'/'Chrome'/'User Data'/'Default'
        folder.mkdir(parents=True)
        (folder/'Bookmarks').write_text(json.dumps({'roots':{'bookmark_bar':{'children':[
            {'type':'folder','name':'研究','children':[
                {'type':'url','name':'FRB記事','url':'https://example.org/frb'}]}]}}}), encoding='utf-8')
        edge = self.localappdata/'Microsoft'/'Edge'/'User Data'/'Default'
        edge.mkdir(parents=True)
        (edge/'Bookmarks').write_text(json.dumps({'roots':{'bookmark_bar':{'children':[
            {'type':'url','name':'Edgeのページ','url':'https://example.org/edge'}]}}}), encoding='utf-8')
        self.old_state = module.STATE
        module.STATE = self.localappdata
        self.hotkey = patch.object(module.windows, 'hotkey', return_value=None)
        self.unhotkey = patch.object(module.windows, 'unhotkey', return_value=None)
        self.hotkey.start();self.unhotkey.start()
        self.w = module.Launcher()
        self.w.select_bookmark_browser('chrome')
        self.w.summon()
        # The bookmark root is editable in Studio and may move to any Page.
        root = next(r for r in self.w.data['items'] if r.get('launch_source') == 'browser_bookmarks')
        self.w.switch_page(next(i for i,p in enumerate(self.w.pages) if p['page_id'] == root['page_id']))
        self.qt.processEvents()

    def tearDown(self):
        self.w.dismiss();self.w.tray.hide();self.w.deleteLater();self.qt.processEvents()
        self.hotkey.stop();self.unhotkey.stop()
        module.STATE = self.old_state
        self.env.stop()
        self.temp.cleanup()

    def test_right_arrows_expand_then_open_leaf(self):
        rows=[self.w.list.topLevelItem(i) for i in range(self.w.list.topLevelItemCount())]
        root=next(i for i in rows if i.data(0,Qt.ItemDataRole.UserRole)['item_id']=='__browser_bookmarks_root')
        self.w.list.setCurrentItem(root)
        QTest.keyClick(self.w.list,Qt.Key.Key_Right)
        menu = self.w.menu
        self.assertTrue(menu.isVisible())
        # The unique bookmark-bar -> research-folder chain is a presentation
        # shortcut, not two extra popups. Never auto-execute the terminal URL.
        self.assertEqual(menu.activeAction().data()['title'],'FRB記事')
        self.assertIsNone(menu.child)
        with patch.object(self.w,'run_menu_item') as run:
            QTest.keyClick(menu,Qt.Key.Key_Right)
            self.assertEqual(run.call_args.args[0]['launch_actions'][0]['launch_browser'], 'chrome')

    def test_entering_bookmark_root_also_skips_redundant_folders(self):
        root = next(r for r in self.w.data['items'] if r.get('launch_source') == 'browser_bookmarks')
        self.w.activate(root)
        self.assertEqual(self.w.list.topLevelItemCount(), 1)
        self.assertEqual(self.w.list.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole)['title'], 'FRB記事')
        self.w.go_back()
        self.assertFalse(self.w.stack)

    def test_bookmark_item_hides_url_but_keeps_tooltip(self):
        root = next(r for r in self.w.data['items'] if r.get('item_id') == '__browser_bookmarks_root')
        top = module.CascadeMenu(parent=self.w, launcher=self.w)
        self.w.fill_cascade(top, root)
        leaf = next(a for a in top.actions() if isinstance(a.data(), dict))
        self.assertEqual(leaf.text(), 'FRB記事')
        self.assertNotIn('https://', leaf.text())
        self.assertIn('https://example.org/frb', leaf.toolTip())
        self.assertTrue(top.toolTipsVisible())
        top.deleteLater()

    def test_long_description_clipped_and_full_tooltip(self):
        parent = {'item_id':'menu_display_test', 'page_id':'windows', 'item_kind':'category'}
        long_description = 'https://example.org/' + 'really-long-description/' * 80
        self.w.data['items'].append(dict(item_id='display_leaf', parent_item_id='menu_display_test',
                                        page_id='windows', title='説明つきアイテム', description=long_description,
                                        item_kind='command', sort_order=0, enabled=True))
        menu = module.CascadeMenu(parent=self.w, launcher=self.w)
        self.w.fill_cascade(menu, parent)
        action = next(a for a in menu.actions() if isinstance(a.data(),dict))
        self.assertTrue(action.text().endswith('…'), action.text())
        self.assertEqual(action.toolTip(), '説明つきアイテム\n' + long_description)
        self.assertLessEqual(menu.maximumWidth(), module.CASCADE_MAX_WIDTH)
        menu.deleteLater()

    def test_long_folder_name_keeps_right_arrow(self):
        parent = {'item_id':'menu_display_test', 'page_id':'windows', 'item_kind':'category'}
        title = '研究フォルダー' * 90
        self.w.data['items'].append(dict(item_id='display_folder', parent_item_id='menu_display_test',
                                        page_id='windows', title=title, item_kind='category',
                                        sort_order=0, enabled=True))
        menu = module.CascadeMenu(parent=self.w, launcher=self.w)
        self.w.fill_cascade(menu, parent)
        action = next(a for a in menu.actions() if isinstance(a.data(),dict))
        self.assertTrue(action.text().endswith('  ›'), action.text())
        self.assertIn('…', action.text())
        self.assertEqual(action.toolTip(), title)
        menu.deleteLater()

    def test_main_search_respects_selected_browser(self):
        self.w.search.setText('FRB記事')
        self.qt.processEvents()
        self.assertTrue(any(self.w.list.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole).get('title') == 'FRB記事'
                            for i in range(self.w.list.topLevelItemCount())))
        self.w.select_bookmark_browser('edge')
        self.qt.processEvents()
        self.assertFalse(any(self.w.list.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole).get('title') == 'FRB記事'
                             for i in range(self.w.list.topLevelItemCount())))
        self.w.search.setText('Edgeのページ')
        self.qt.processEvents()
        self.assertTrue(any(self.w.list.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole).get('title') == 'Edgeのページ'
                            for i in range(self.w.list.topLevelItemCount())))

    def test_auto_source_action_only_enabled_when_manual_file_is_set(self):
        self.assertFalse(self.w.bookmark_auto_action.isEnabled())
        self.assertIn('手動指定を解除', self.w.bookmark_auto_action.text())
        self.w.settings.setValue('bookmark_manual_chrome', str(self.localappdata / 'manual.html'))
        self.w.update_bookmark_source_action()
        self.assertTrue(self.w.bookmark_auto_action.isEnabled())
        self.w.select_bookmark_browser('edge')
        self.assertFalse(self.w.bookmark_auto_action.isEnabled())
        self.w.select_bookmark_browser('chrome')
        self.assertTrue(self.w.bookmark_auto_action.isEnabled())
        self.w.use_auto_bookmarks()
        self.assertFalse(self.w.bookmark_auto_action.isEnabled())
        self.assertEqual(self.w.bookmark_manual_file(), '')

    def test_switch_browser_replaces_catalog(self):
        self.assertTrue(any(r.get('title') == 'FRB記事' for r in self.w.data['items']))
        self.w.select_bookmark_browser('edge')
        self.assertTrue(any(r.get('title') == 'Edgeのページ' for r in self.w.data['items']))
        self.assertFalse(any(r.get('title') == 'FRB記事' for r in self.w.data['items']))


if __name__=='__main__':unittest.main()
