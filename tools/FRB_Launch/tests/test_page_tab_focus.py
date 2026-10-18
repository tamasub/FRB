"""Keyboard-focus indicator contract for Page tabs."""
import importlib.util
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FocusTabSourceTests(unittest.TestCase):
    def test_main_launcher_uses_focus_aware_tab_bar(self):
        source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
        self.assertIn('from page_tab_focus import FocusPageTabBar', source)
        self.assertIn('self.tabs = FocusPageTabBar()', source)
        self.assertIn('self.tabs.setStyleSheet(PAGE_TABS_QSS)', source)

    def test_focus_ring_depends_on_actual_keyboard_focus(self):
        source = (ROOT / 'src/page_tab_focus.py').read_text(encoding='utf-8')
        self.assertIn('not self.hasFocus()', source)
        self.assertIn('self.tabRect(index)', source)
        self.assertIn('def focusInEvent(', source)
        self.assertIn('def focusOutEvent(', source)
        self.assertIn('super().paintEvent(event)', source)
        self.assertIn('QRectF(tab_rect).adjusted(', source)


@unittest.skipUnless(importlib.util.find_spec('PySide6'), 'PySide6 not installed')
class FocusTabGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_keyboard_focus_appears_and_follows_current_tab(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
        sys.path.insert(0, str(ROOT / 'src'))
        from page_tab_focus import FocusPageTabBar
        from page_tab_theme import PAGE_TABS_QSS
        root = QWidget()
        layout = QVBoxLayout(root)
        edit = QLineEdit()
        tabs = FocusPageTabBar()
        tabs.setStyleSheet(PAGE_TABS_QSS)
        tabs.setExpanding(False)
        tabs.setDrawBase(False)
        for label in ('仕事', 'Windows', 'FRB実験'):
            tabs.addTab(label)
        layout.addWidget(edit)
        layout.addWidget(tabs)
        root.show()
        self.app.processEvents()
        try:
            tabs.setCurrentIndex(0)
            edit.setFocus()
            self.app.processEvents()
            self.assertFalse(tabs.hasFocus())
            tabs.setFocus(Qt.FocusReason.TabFocusReason)
            self.app.processEvents()
            self.assertTrue(tabs.hasFocus())
            QTest.keyClick(tabs, Qt.Key.Key_Right)
            self.assertEqual(tabs.currentIndex(), 1)
            self.assertTrue(tabs.hasFocus())
            edit.setFocus()
            self.app.processEvents()
            self.assertFalse(tabs.hasFocus())
            self.assertEqual(tabs.currentIndex(), 1)
        finally:
            root.close()


if __name__ == '__main__':
    unittest.main()
