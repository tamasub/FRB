"""Regression checks for the modern Page tab style.

The style contract is Qt stylesheet based so basic checks run even without
PySide6 (the Windows launcher uses the GUI-capable environment).
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from page_tab_theme import PAGE_TABS_QSS


class PageTabThemeTests(unittest.TestCase):
    def test_inactive_tabs_are_not_native_beveled_controls(self):
        # Explicit border AND background avoid the Qt/Windows native fallback.
        base = PAGE_TABS_QSS.split('QTabBar::tab {', 1)[1].split('}', 1)[0]
        self.assertIn('background:', base)
        self.assertIn('border:', base)
        self.assertIn('border-radius:', base)
        self.assertIn('margin-right:', base)

    def test_selection_and_hover_have_distinct_states(self):
        self.assertIn('QTabBar::tab:selected {', PAGE_TABS_QSS)
        self.assertIn('QTabBar::tab:hover:!selected {', PAGE_TABS_QSS)
        self.assertIn('border-bottom: 2px solid #8ab9ff', PAGE_TABS_QSS)
        self.assertIn('qlineargradient(', PAGE_TABS_QSS)

    def test_launcher_uses_style_without_changing_page_navigation(self):
        source = (ROOT / 'app.py').read_text(encoding='utf-8')
        self.assertIn('self.tabs.setStyleSheet(PAGE_TABS_QSS)', source)
        self.assertIn('self.tabs.currentChanged.connect(self.page_changed)', source)
        self.assertIn('self.tabs.setCurrentIndex(index)', source)
        self.assertIn("for p in self.pages:self.tabs.addTab(p['title'])", source)
        self.assertNotIn('QTabBar::tab{padding:7px 17px;', source)

    @unittest.skipUnless(importlib.util.find_spec('PySide6'), 'PySide6 not installed in this test environment')
    def test_qtabbar_keeps_click_and_arrow_navigation(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication, QTabBar
        app = QApplication.instance() or QApplication([])
        bar = QTabBar()
        bar.setExpanding(False)
        bar.setDrawBase(False)
        bar.setStyleSheet(PAGE_TABS_QSS)
        for title in ('仕事', 'Windows', 'FRB実験'):
            bar.addTab(title)
        bar.show()
        app.processEvents()
        try:
            self.assertEqual(bar.count(), 3)
            bar.setCurrentIndex(0)
            QTest.mouseClick(bar, Qt.MouseButton.LeftButton,
                             pos=bar.tabRect(1).center())
            self.assertEqual(bar.currentIndex(), 1)
            QTest.keyClick(bar, Qt.Key.Key_Right)
            self.assertEqual(bar.currentIndex(), 2)
        finally:
            bar.close()


if __name__ == '__main__':
    unittest.main()
