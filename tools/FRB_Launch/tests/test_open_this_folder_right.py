"""Regression: Right Arrow must execute the 'Open this folder' utility.

Covers both compact QMenu and the scrollable tree used by long folder menus.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import app
except ImportError:
    QApplication = None
    app = None


@unittest.skipUnless(app is not None, 'PySide6 required for GUI tests')
class OpenThisFolderRightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.w = app.Launcher()
        self.w.show()
        self.row = {'item_kind': 'directory', 'launch_browse_target': str(self.root)}

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.qt.processEvents()
        self.tmp.cleanup()

    def _assert_right_opens_folder(self, long_menu):
        self.w.cascade(self.row)
        menu = self.w.menu
        self.qt.processEvents()
        self.assertEqual(menu.scroll_tree is not None, long_menu)
        actions = menu._scroll_actions if long_menu else menu.actions()
        action = next(a for a in actions if a.text() == 'このフォルダーを開く')
        self.assertTrue(action.property('launch_right_arrow_executes'))
        menu.setActiveAction(action)
        target = menu.scroll_tree if long_menu else menu
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.keyClick(target, Qt.Key.Key_Right)
            run.assert_called_once_with(self.row)

    def test_short_menu_right_arrow_opens_current_folder(self):
        (self.root / 'child').mkdir()
        self._assert_right_opens_folder(long_menu=False)

    def test_long_menu_right_arrow_opens_current_folder(self):
        for i in range(100):
            (self.root / f'file_{i:03}.txt').write_text('x', encoding='utf-8')
        self._assert_right_opens_folder(long_menu=True)

    def test_right_on_folder_child_still_expands_instead_of_executing(self):
        (self.root / 'child').mkdir()
        self.w.cascade(self.row)
        menu = self.w.menu
        action = next(a for a in menu.actions() if a in menu.openers)
        menu.setActiveAction(action)
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.keyClick(menu, Qt.Key.Key_Right)
            self.assertIsNotNone(menu.child)
            self.assertTrue(menu.child.isVisible())
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
