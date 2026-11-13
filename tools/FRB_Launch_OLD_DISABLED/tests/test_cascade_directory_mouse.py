"""Mouse semantics for real folder cascades (QT_QPA_PLATFORM=offscreen).

A single click must keep a folder popup alive; a double click opens the
real directory only AFTER the second mouse-button release. This covers both
QMenu's compact actions and the scrollable QTreeWidget adaptation.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QApplication
    from PySide6.QtTest import QTest
    import app
except ImportError:
    QApplication = None
    app = None


@unittest.skipUnless(app is not None, 'PySide6 needed for mouse integration tests')
class DirectoryPopupMouseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / 'subfolder'
        self.folder.mkdir()
        (self.folder / 'hello.txt').write_text('hello', encoding='utf-8')
        self.w = app.Launcher()
        self.w.show()

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.qt.processEvents()
        self.temp.cleanup()

    def _open_menu(self, long_menu=False):
        if long_menu:
            for i in range(70):
                (self.root / f'{i+1:03}.txt').write_text('x', encoding='utf-8')
        self.w.cascade({'item_kind': 'directory', 'launch_browse_target': str(self.root)})
        self.qt.processEvents()
        menu = self.w.menu
        self.assertTrue(menu.isVisible())
        self.assertEqual(menu.scroll_tree is not None, long_menu)
        return menu

    def test_compact_one_click_expands_without_dismissing(self):
        menu = self._open_menu()
        action = next(a for a in menu.actions() if
                      isinstance(a.data(), dict) and a.data().get('title') == 'subfolder')
        pos = menu.actionGeometry(action).center()
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.mouseClick(menu, Qt.MouseButton.LeftButton, pos=pos)
            self.qt.processEvents()
            self.assertTrue(menu.isVisible())
            run.assert_not_called()
            QTest.qWait(self.qt.doubleClickInterval() + 45)
            self.assertTrue(menu.isVisible())
            self.assertIsNotNone(menu.child)
            self.assertTrue(menu.child.isVisible())
            run.assert_not_called()

    def test_compact_double_click_opens_directory(self):
        menu = self._open_menu()
        action = next(a for a in menu.actions() if
                      isinstance(a.data(), dict) and a.data().get('title') == 'subfolder')
        pos = menu.actionGeometry(action).center()
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.mouseClick(menu, Qt.MouseButton.LeftButton, pos=pos)
            QTest.mouseDClick(menu, Qt.MouseButton.LeftButton, pos=pos)
            self.qt.processEvents()
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0]['launch_browse_target'], str(self.folder))

    def test_long_scroll_double_click_opens_directory(self):
        menu = self._open_menu(long_menu=True)
        tree = menu.scroll_tree
        item = next(tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
                    if tree.topLevelItem(i).text(0) == 'subfolder')
        tree.scrollToItem(item)
        self.qt.processEvents()
        pos = tree.visualItemRect(item).center()
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=pos)
            self.qt.processEvents()
            self.assertTrue(menu.isVisible())
            run.assert_not_called()
            QTest.mouseDClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=pos)
            self.qt.processEvents()
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0]['launch_browse_target'], str(self.folder))

    def test_double_click_on_empty_popup_space_opens_displayed_folder(self):
        menu = self._open_menu()
        # A click in the empty margin (outside QAction geometry) must not
        # dismiss the menu; the double click should open the displayed root.
        pos = QPoint(menu.width() - 3, menu.height() - 3)
        if menu.actionAt(pos) is not None:
            self.skipTest('Qt platform has no unused space in compact QMenu')
        with patch.object(self.w, 'run_menu_item') as run:
            QTest.mouseClick(menu, Qt.MouseButton.LeftButton, pos=pos)
            self.assertTrue(menu.isVisible())
            QTest.mouseDClick(menu, Qt.MouseButton.LeftButton, pos=pos)
            self.qt.processEvents()
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0]['launch_browse_target'], str(self.root))


if __name__ == '__main__':
    unittest.main()
