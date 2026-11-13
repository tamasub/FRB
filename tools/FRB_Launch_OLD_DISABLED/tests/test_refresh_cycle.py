import json, os, unittest
from unittest.mock import patch
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module
import test_apps_ui as apps_ui

class RefreshCycleTests(unittest.TestCase):
    setUpClass=classmethod(apps_ui.AppsUITests.setUpClass.__func__)
    setUp=apps_ui.AppsUITests.setUp
    tearDown=apps_ui.AppsUITests.tearDown
    def test_up_and_down_wrap_inside_list_without_switching_to_tabs(self):
        w=self.w;count=w.list.topLevelItemCount();self.assertGreater(count,0)
        w.list.setCurrentItem(w.list.topLevelItem(0));w.list.setFocus()
        QTest.keyClick(w.list,Qt.Key.Key_Up)
        self.assertEqual(QApplication.focusWidget(),w.list)
        self.assertEqual(w.list.indexOfTopLevelItem(w.list.currentItem()),count-1)
        QTest.keyClick(w.list,Qt.Key.Key_Down)
        self.assertEqual(QApplication.focusWidget(),w.list)
        self.assertEqual(w.list.indexOfTopLevelItem(w.list.currentItem()),0)
    def test_reload_on_show_and_skip_unchanged(self):
        path=Path(self.temp.name)/'settings.json';data=json.loads(module.CONFIG.read_text(encoding='utf-8-sig'));path.write_text(json.dumps(data),encoding='utf-8')
        with patch.object(module,'CONFIG',path):
            self.w.reload(True);self.w.dismiss()
            with patch.object(module,'load',wraps=module.load) as reader:
                self.w.show();self.qt.processEvents();self.assertEqual(reader.call_count,0)
                self.w.dismiss();data['pages'][0]['title']='Auto updated';path.write_text(json.dumps(data),encoding='utf-8');stat=path.stat();os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns+1000000))
                self.w.show();self.qt.processEvents();self.assertEqual(reader.call_count,1);self.assertEqual(self.w.pages[0]['title'],'Auto updated')
    def test_bad_config_keeps_last_good_and_retries(self):
        path=Path(self.temp.name)/'settings.json';good=module.CONFIG.read_text(encoding='utf-8-sig');path.write_text(good)
        with patch.object(module,'CONFIG',path):
            self.w.reload(True);before=self.w.data;stamp=self.w.mtime;path.write_text('{invalid')
            with patch.object(self.w,'error') as error:self.w.reload();self.assertTrue(error.called)
            self.assertIs(self.w.data,before);self.assertEqual(self.w.mtime,stamp)
            path.write_text(good);self.w.reload();self.assertEqual(self.w.mtime,path.stat().st_mtime_ns)
    def test_empty_page_tabs_do_not_crash(self):
        self.w.list.clear();self.w.tabs.setFocus();QTest.keyClick(self.w.tabs,Qt.Key.Key_Up);QTest.keyClick(self.w.tabs,Qt.Key.Key_Down)
