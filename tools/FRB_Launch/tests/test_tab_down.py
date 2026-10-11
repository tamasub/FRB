import test_navigation
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

class TabDownTests(test_navigation.NavigationTests):
    test_immediate_right_and_left=None
    test_nested_and_directory_single_column=None
    test_function_page_keys=None
    test_selection_all_clear_and_back=None

    def test_down_leaves_page_tabs_without_skipping_item(self):
        first=self.w.list.topLevelItem(0)
        self.w.list.setCurrentItem(first)
        self.w.tabs.setFocus();self.app.processEvents()
        page=self.w.tabs.currentIndex()
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Down)
        self.assertEqual(QApplication.focusWidget(),self.w.list)
        self.assertEqual(self.w.list.currentItem(),first)
        self.assertEqual(self.w.tabs.currentIndex(),page)
        QTest.keyClick(self.w.list,Qt.Key.Key_Down)
        self.assertEqual(self.w.list.currentItem(),self.w.list.topLevelItem(1))

    def test_tab_arrow_keeps_normal_page_navigation(self):
        self.w.tabs.setCurrentIndex(0);self.w.tabs.setFocus()
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Right)
        self.assertEqual(self.w.tabs.currentIndex(),1)
        self.w.tabs.setFocus()
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Down)
        self.assertEqual(QApplication.focusWidget(),self.w.list)
        self.assertEqual(self.w.list.currentItem(),self.w.list.topLevelItem(0))

    def test_empty_list_down_does_not_fail(self):
        self.w.search.setText('___no_such_item___')
        self.w.tabs.setFocus()
        QTest.keyClick(self.w.tabs,Qt.Key.Key_Down)
        self.assertEqual(QApplication.focusWidget(),self.w.list)
        self.assertIsNone(self.w.list.currentItem())
