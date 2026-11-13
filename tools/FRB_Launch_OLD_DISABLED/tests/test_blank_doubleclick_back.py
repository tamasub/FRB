"""Regression tests for in-window submenu blank-area double-click Back.

Run on a Windows/PySide6 build, or with QT_QPA_PLATFORM=offscreen:
  python -m unittest discover -s tests -p test_blank_doubleclick_back.py
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module


class BlankDoubleClickBackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.tmp = tempfile.TemporaryDirectory()
        module.STATE = Path(cls.tmp.name)
        cls.old_hotkey = module.windows.hotkey
        cls.old_unhotkey = module.windows.unhotkey
        module.windows.hotkey = lambda *args: None
        module.windows.unhotkey = lambda *args: None

    @classmethod
    def tearDownClass(cls):
        module.windows.hotkey = cls.old_hotkey
        module.windows.unhotkey = cls.old_unhotkey
        cls.tmp.cleanup()

    def setUp(self):
        self.w = module.Launcher()
        self.w.page_id = 'work'
        self.w.render()
        self.w.show()
        self.app.processEvents()

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.app.processEvents()

    def enter_item(self, item_id):
        tree = self.w.list
        item = next(tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                    if tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole).get('item_id') == item_id)
        tree.setCurrentItem(item)
        QTest.keyClick(tree, Qt.Key.Key_Return)
        self.app.processEvents()

    def dblclick_blank(self):
        viewport = self.w.list.viewport()
        self.app.processEvents()
        pos = QPoint(viewport.width() // 2, viewport.height() - 3)
        self.assertIsNone(self.w.list.itemAt(pos), 'Test needs a blank point below last menu item')
        QTest.mouseDClick(viewport, Qt.MouseButton.LeftButton, pos=pos)
        self.app.processEvents()

    def test_enter_category_then_blank_double_click_goes_back(self):
        self.enter_item('dates')
        self.assertEqual([r['item_id'] for r in self.w.stack], ['dates'])
        self.dblclick_blank()
        self.assertEqual(self.w.stack, [])
        self.assertTrue(self.w.isVisible())

    def test_nested_menu_goes_back_exactly_one_level(self):
        self.enter_item('website')
        self.enter_item('favorite_ai')
        self.assertEqual(len(self.w.stack), 2)
        self.dblclick_blank()
        self.assertEqual([r['item_id'] for r in self.w.stack], ['website'])
        self.dblclick_blank()
        self.assertEqual(self.w.stack, [])

    def test_selection_back_preserves_parent_category(self):
        self.enter_item('mail')
        self.enter_item('sales')
        self.assertIsNotNone(self.w.selection)
        self.dblclick_blank()
        self.assertIsNone(self.w.selection)
        self.assertEqual([r['item_id'] for r in self.w.stack], ['mail'])

    def test_double_click_on_existing_item_never_goes_back(self):
        self.enter_item('dates')
        rect = self.w.list.visualItemRect(self.w.list.topLevelItem(0))
        self.assertIsNotNone(self.w.list.itemAt(rect.center()))
        # This might activate the item; prevent real actions during the test.
        with patch.object(self.w, 'execute'):
            QTest.mouseDClick(self.w.list.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())
            self.app.processEvents()
        self.assertEqual([r['item_id'] for r in self.w.stack], ['dates'])

    def test_root_blank_double_click_does_nothing(self):
        self.w.switch_page(1)  # FRB page has only two root items.
        self.dblclick_blank()
        self.assertEqual(self.w.stack, [])
        self.assertTrue(self.w.isVisible())

    def test_right_double_click_does_not_go_back(self):
        self.enter_item('dates')
        viewport = self.w.list.viewport()
        point = QPoint(viewport.width() // 2, viewport.height() - 3)
        self.assertIsNone(self.w.list.itemAt(point))
        QTest.mouseDClick(viewport, Qt.MouseButton.RightButton, pos=point)
        self.app.processEvents()
        self.assertEqual([r['item_id'] for r in self.w.stack], ['dates'])


if __name__ == '__main__':
    unittest.main()
