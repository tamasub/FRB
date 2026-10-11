import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import test_apps_ui as apps_ui

class TabArrowTests(unittest.TestCase):
    setUpClass=classmethod(apps_ui.AppsUITests.setUpClass.__func__)
    setUp=apps_ui.AppsUITests.setUp
    tearDown=apps_ui.AppsUITests.tearDown
    def test_first_item_up_stops_at_tabs_and_down_returns(self):
        self.w.list.setCurrentItem(self.w.list.topLevelItem(0));self.w.list.setFocus()
        QTest.keyClick(self.w.list,Qt.Key.Key_Up)
        self.assertEqual(QApplication.focusWidget(),self.w.tabs)
        for _ in range(4):QTest.keyClick(self.w.tabs,Qt.Key.Key_Up)
        self.assertEqual(QApplication.focusWidget(),self.w.tabs)
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Down)
        self.assertEqual(QApplication.focusWidget(),self.w.list)
        self.assertEqual(self.w.list.indexOfTopLevelItem(self.w.list.currentItem()),0)
    def test_tab_arrows_change_page_keep_focus_and_stop_at_edges(self):
        self.w.tabs.setCurrentIndex(0);self.w.tabs.setFocus()
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Right)
        self.assertEqual(self.w.tabs.currentIndex(),1);self.assertEqual(self.w.page_id,self.w.pages[1]['page_id'])
        self.assertEqual(QApplication.focusWidget(),self.w.tabs)
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Left);self.assertEqual(self.w.tabs.currentIndex(),0)
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Left);self.assertEqual(self.w.tabs.currentIndex(),0)
        self.w.tabs.setCurrentIndex(self.w.tabs.count()-1)
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Right);self.assertEqual(self.w.tabs.currentIndex(),self.w.tabs.count()-1)
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Down);self.assertEqual(QApplication.focusWidget(),self.w.list)
    def test_up_from_second_row_stays_in_list(self):
        self.w.list.setCurrentItem(self.w.list.topLevelItem(1));self.w.list.setFocus()
        QTest.keyClick(self.w.list,Qt.Key.Key_Up)
        self.assertEqual(QApplication.focusWidget(),self.w.list)
        self.assertEqual(self.w.list.indexOfTopLevelItem(self.w.list.currentItem()),0)

if __name__=='__main__':unittest.main()
