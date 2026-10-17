"""Real widget key routing; run on Windows with PySide6 or offscreen Qt."""
import importlib.util
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
QT_AVAILABLE = importlib.util.find_spec('PySide6') is not None


@unittest.skipUnless(QT_AVAILABLE, 'PySide6 is required for UI navigation checks')
class WrapNavigationGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        import app
        self.app_module = app
        self.w = app.Launcher()
        self.w.show()
        self.qt.processEvents()

    def tearDown(self):
        if self.w.menu:
            self.w.menu.close()
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.qt.processEvents()

    def test_main_and_search_results_wrap_with_real_key_events(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        for search in ('', 'a'):
            self.w.search.setText(search)
            self.qt.processEvents()
            tree = self.w.list
            count = tree.topLevelItemCount()
            if count < 2:
                continue
            tree.setCurrentItem(tree.topLevelItem(0))
            tree.setFocus()
            QTest.keyClick(tree, Qt.Key.Key_Up)
            self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), count-1)
            QTest.keyClick(tree, Qt.Key.Key_Down)
            self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), 0)
            self.assertTrue(tree.hasFocus())

    def test_short_directory_actions_wrap(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        with TemporaryDirectory() as tmp:
            (Path(tmp)/'first.txt').write_text('a')
            (Path(tmp)/'second.txt').write_text('b')
            self.w.cascade({'item_kind': 'directory', 'launch_browse_target': tmp})
            menu = self.w.menu
            candidates = [a for a in menu.actions() if a.isVisible() and a.isEnabled()
                          and not a.isSeparator() and (isinstance(a.data(), dict)
                              or bool(a.property('launch_right_arrow_executes')))]
            self.assertGreaterEqual(len(candidates), 2)
            menu.setActiveAction(candidates[0])
            QTest.keyClick(menu, Qt.Key.Key_Up)
            self.assertIs(menu.activeAction(), candidates[-1])
            QTest.keyClick(menu, Qt.Key.Key_Down)
            self.assertIs(menu.activeAction(), candidates[0])

    def test_history_up_down_wrap_does_not_reorder_entries(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        self.w.search_history.keywords = ['a', 'b', 'c']
        self.w.toggle_history_popup()
        tree = self.w.history_choices
        tree.setCurrentItem(tree.topLevelItem(0))
        QTest.keyClick(tree, Qt.Key.Key_Up)
        self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), 2)
        QTest.keyClick(tree, Qt.Key.Key_Down)
        self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), 0)
        self.assertEqual(self.w.search_history.keywords, ['a', 'b', 'c'])

    def test_large_cascade_scroll_tree_wraps(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        with TemporaryDirectory() as tmp:
            for i in range(60):
                (Path(tmp)/f'file_{i:03}.txt').touch()
            self.w.cascade({'item_kind': 'directory', 'launch_browse_target': tmp})
            menu = self.w.menu
            self.assertIsNotNone(menu.scroll_tree)
            tree = menu.scroll_tree
            tree.setCurrentItem(tree.topLevelItem(0))
            QTest.keyClick(tree, Qt.Key.Key_Up)
            self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), tree.topLevelItemCount()-1)
            QTest.keyClick(tree, Qt.Key.Key_Down)
            self.assertEqual(tree.indexOfTopLevelItem(tree.currentItem()), 0)


if __name__ == '__main__':
    unittest.main()
