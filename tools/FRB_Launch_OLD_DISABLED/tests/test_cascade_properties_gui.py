"""Native Qt tests of cascading Properties. Run with PySide6 on Windows/offscreen."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import app
except ImportError:
    app = None
    QApplication = None


@unittest.skipUnless(app is not None, 'PySide6 is required for mouse GUI tests')
class CascadePropertiesGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.w = app.Launcher()
        self.w.show()
        self.qt.processEvents()

    def tearDown(self):
        self.w.close_cascade_for_main_interaction()
        self.w.tray.hide()
        self.w.close()
        self.qt.processEvents()

    def test_compact_cascade_authored_row_opens_properties_on_first_click(self):
        # category dates and its authored child today exist in the test config.
        parent = next(row for row in self.w.data['items'] if row.get('item_id') == 'dates')
        self.w.cascade(parent)
        menu = self.w.menu
        action = next(a for a in menu.actions() if isinstance(a.data(), dict)
                      and a.data().get('item_id') == 'today')
        with patch.object(self.w, 'show_launch_context_menu', return_value=True) as popup:
            QTest.mouseClick(menu, Qt.MouseButton.RightButton, pos=menu.actionGeometry(action).center())
            self.qt.processEvents()
            self.assertEqual(popup.call_count, 1)
            self.assertEqual(popup.call_args.args[1]['item_id'], 'today')
            self.assertTrue(menu.isVisible(), 'Right-click Properties must not erase the submenu')

    def test_long_cascade_authored_row_opens_properties(self):
        parent = {'page_id': 'work', 'item_id': 'gui_parent', 'title': 'bulk',
                  'item_kind': 'category', 'enabled': True}
        self.w.data['items'].append(parent)
        for index in range(75):
            self.w.data['items'].append({'page_id': 'work',
                                         'parent_item_id': 'gui_parent',
                                         'item_id': f'gui_{index:03}',
                                         'title': f'item {index:03}',
                                         'item_kind': 'command', 'enabled': True,
                                         'launch_actions': []})
        self.w.cascade(parent)
        menu = self.w.menu
        self.qt.processEvents()
        self.assertIsNotNone(menu.scroll_tree)
        item = menu.scroll_tree.topLevelItem(0)
        with patch.object(self.w, 'show_launch_context_menu', return_value=True) as popup:
            QTest.mouseClick(menu.scroll_tree.viewport(), Qt.MouseButton.RightButton,
                             pos=menu.scroll_tree.visualItemRect(item).center())
            self.qt.processEvents()
            self.assertEqual(popup.call_count, 1)
            self.assertEqual(popup.call_args.args[1]['item_id'], 'gui_000')

if __name__ == '__main__':
    unittest.main()
