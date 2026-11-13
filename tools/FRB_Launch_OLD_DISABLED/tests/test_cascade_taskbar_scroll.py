"""Qt integration checks for long normal-folder/bookmark cascade lists."""
import unittest
from pathlib import Path

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import app
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication is not None, 'Requires PySide6')
class CascadingLongMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        class DummyLauncher:
            data = {'launch_hover_delay_ms': 250}
            def page_key(self, event): return False
            def focus_search(self, select=True): pass
            def run_menu_item(self, row): pass
        self.launcher = DummyLauncher()
        self.menu = app.CascadeMenu(launcher=self.launcher)
        self.menu.order_enabled = False
        for idx in range(70):
            action = self.menu.addAction(f'entry_{idx:03}')
            action.setData({'item_id': str(idx), 'title': f'entry_{idx:03}'})

    def tearDown(self):
        self.menu.close()
        self.menu.deleteLater()
        self.qt.processEvents()

    def test_many_items_have_true_vertical_scrollbar(self):
        available = QApplication.primaryScreen().availableGeometry()
        self.menu.popup(available.center())
        self.qt.processEvents()
        self.assertIsNotNone(self.menu.scroll_tree)
        self.assertEqual(self.menu.scroll_tree.topLevelItemCount(), 70)
        bar = self.menu.scroll_tree.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(bar.maximum())
        self.qt.processEvents()
        last = self.menu.scroll_tree.visualItemRect(self.menu.scroll_tree.topLevelItem(69))
        self.assertTrue(self.menu.scroll_tree.viewport().rect().intersects(last))
        self.assertLessEqual(self.menu.frameGeometry().bottom(), available.bottom()-app.MENU_SCREEN_MARGIN+3)

    def test_short_menu_uses_regular_actions(self):
        for action in self.menu.actions()[5:]:
            self.menu.removeAction(action)
        available = QApplication.primaryScreen().availableGeometry()
        self.menu.popup(available.center())
        self.qt.processEvents()
        self.assertIsNone(self.menu.scroll_tree)
        self.assertEqual(len(self.menu.actions()), 5)

if __name__ == '__main__':
    unittest.main()
