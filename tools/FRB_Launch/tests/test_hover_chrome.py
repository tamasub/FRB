import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
import test_navigation
import app as module

class HoverChromeTests(test_navigation.NavigationTests):
    # Keep only the new regressions here (base setup supplies a real launcher).
    test_immediate_right_and_left=None
    test_nested_and_directory_single_column=None
    test_function_page_keys=None
    test_selection_all_clear_and_back=None

    def root_menu(self,mode):
        q=self.w.list.currentItem()
        self.w.cascade(q.data(0,Qt.ItemDataRole.UserRole),q,mode)
        self.app.processEvents();return self.w.menu

    def test_hover_related_area_and_departure(self):
        m=self.root_menu('hover');outside=QPoint(-10000,-10000)
        self.w.check_hover_menus(m.mapToGlobal(m.rect().center()),1)
        self.w.check_hover_menus(outside,2)
        self.assertTrue(m.isVisible())
        self.w.check_hover_menus(m.mapToGlobal(m.rect().center()),2.1)
        self.w.check_hover_menus(outside,3)
        self.w.check_hover_menus(outside,3.3)
        self.assertFalse(m.isVisible())

    def test_keyboard_promotes_hover_root(self):
        m=self.root_menu('hover')
        QTest.keyClick(m,Qt.Key.Key_Right)
        self.assertEqual(m.open_mode,'keyboard')
        self.w.check_hover_menus(QPoint(-10000,-10000),1)
        self.w.check_hover_menus(QPoint(-10000,-10000),2)
        self.assertTrue(m.isVisible())

    def test_child_hover_closes_without_closing_keyboard_parent(self):
        # The text category has no subfolder; use favorites with its AI child.
        row=next(r for r in self.w.data['items'] if r['item_id']=='websites') if any(r['item_id']=='websites' for r in self.w.data['items']) else next(r for r in self.w.data['items'] if r['item_id']=='website')
        self.w.cascade(row);m=self.w.menu
        a=next(iter(m.openers));m.setActiveAction(a);m.openers[a]('hover')
        child=m.child
        self.w.check_hover_menus(child.mapToGlobal(child.rect().center()),1)
        self.assertTrue(m.isVisible());self.assertTrue(child.isVisible())
        self.w.check_hover_menus(QPoint(-10000,-10000),2)
        self.w.check_hover_menus(QPoint(-10000,-10000),2.3)
        self.assertTrue(m.isVisible());self.assertFalse(child.isVisible())

    def test_chrome_and_file_association_are_separate(self):
        with patch.object(module.windows,'open_chrome') as chrome:
            self.w.open_target('https://chatgpt.com/','chrome')
            chrome.assert_called_once_with('https://chatgpt.com/')
        with patch.object(module.windows,'IS_WINDOWS',True),patch.object(module.os,'startfile',create=True) as start:
            self.w.open_target(r'F:\FRB_docsExcel\実験全体図.xlsx')
            start.assert_called_once_with(r'F:\FRB_docsExcel\実験全体図.xlsx')

    def test_chrome_missing_is_visible_error(self):
        with patch.object(module.windows,'IS_WINDOWS',True),patch.object(module.windows,'chrome_path',return_value=None):
            with self.assertRaisesRegex(RuntimeError,'Chromeが見つかりません'):module.windows.open_chrome('https://chatgpt.com/')
        with patch.object(module.windows,'IS_WINDOWS',True),patch.object(module.windows,'chrome_path',return_value=r'C:\chrome.exe'),patch('subprocess.Popen') as process:
            module.windows.open_chrome('https://chatgpt.com/')
            process.assert_called_once_with([r'C:\chrome.exe','https://chatgpt.com/'])
