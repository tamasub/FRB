import json,tempfile,unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module
import installed_apps

class AppsUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old_state=module.STATE;module.STATE=Path(self.temp.name)
        self.w=module.Launcher()
        self.records=[dict(name='Google Chrome',target='Chrome.App',kind='aumid'),dict(name='Excel',target='Excel.App',kind='aumid')]
        self.w.app_records=self.records;self.w.data=installed_apps.attach(self.w.data,self.records)
        self.w.switch_page(next(i for i,p in enumerate(self.w.pages) if p['page_id']=='windows'))
        self.w.show();self.qt.processEvents()
    def tearDown(self):
        self.w.dismiss();self.w.tray.hide();self.w.deleteLater();self.qt.processEvents()
        module.STATE=self.old_state;self.temp.cleanup()
    def test_first_app_selected_cascade_and_launch(self):
        QTest.keyClick(self.w.search,Qt.Key.Key_Right)
        menu=self.w.menu;self.assertTrue(menu.isVisible());self.assertFalse(menu.order_enabled)
        self.assertEqual(menu.activeAction().data()['title'],'Excel')
        sent=[];self.w.execute=lambda row,*args:sent.append(row)
        QTest.keyClick(menu,Qt.Key.Key_Return)
        self.assertEqual(sent[0]['launch_actions'][0]['launch_target'],r'shell:AppsFolder\Excel.App')
    def test_global_search_and_category_reorder(self):
        self.w.search.setText('クローム');self.assertEqual(self.w.list.topLevelItemCount(),1)
        self.w.search.clear();self.w.activate(next(r for r in self.w.data['items'] if r['item_id']=='installed_apps'))
        self.assertFalse(self.w.list.order_enabled);self.assertEqual(self.w.list.topLevelItemCount(),2)
        QTest.keyClick(self.w.list,Qt.Key.Key_Left);self.assertTrue(self.w.list.order_enabled)
    def test_background_result_replaces_cache_without_changing_config(self):
        config_before=module.CONFIG.read_bytes()
        class Done:
            def poll(self):return 0
        self.w.apps_proc=Done();self.w.apps_output=Path(self.temp.name)/'scan.json'
        self.w.apps_output.write_text(json.dumps({'version':1,'apps':self.records}),encoding='utf-8')
        self.w.poll_apps()
        self.assertEqual(len(installed_apps.read_cache(Path(self.temp.name)/'apps_cache.json')),2)
        self.assertIsNone(self.w.apps_proc);self.assertEqual(module.CONFIG.read_bytes(),config_before)
    def test_failed_refresh_retains_previous_list(self):
        class Done:
            def poll(self):return 1
        self.w.apps_proc=Done();self.w.apps_output=Path(self.temp.name)/'scan.json'
        self.w.poll_apps();self.assertEqual(self.w.app_records,self.records)

if __name__=='__main__':unittest.main()
