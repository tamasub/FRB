"""Right-click must not dismiss folder/app cascades before a context menu exists.

Run on a Windows/PySide6 build (or with QT_QPA_PLATFORM=offscreen).
"""
import ast
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtGui import QContextMenuEvent
    from PySide6.QtWidgets import QApplication
    import app
except ImportError:
    QApplication = None
    app = None


class RightClickConnectionTests(unittest.TestCase):
    """Structural check that runs even without PySide6."""

    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[1] / 'src/app.py').read_text(encoding='utf-8')
        parsed = ast.parse(cls.source)
        cls.cascade = next(node for node in parsed.body
                           if isinstance(node, ast.ClassDef) and node.name == 'CascadeMenu')

    def method_source(self, name):
        method = next(n for n in self.cascade.body
                      if isinstance(n, ast.FunctionDef) and n.name == name)
        return ast.get_source_segment(self.source, method)

    def test_qmenu_event_swallowed_before_default_handler(self):
        handler = self.method_source('event')
        self.assertLess(handler.index('_consume_unused_right_click'),
                        handler.index('super().event(event)'))
        guard = self.method_source('_consume_unused_right_click')
        self.assertIn('QEvent.Type.ContextMenu', guard)
        self.assertIn('QEvent.Type.MouseButtonPress', guard)
        self.assertIn('QEvent.Type.MouseButtonRelease', guard)
        self.assertIn('QEvent.Type.MouseButtonDblClick', guard)
        self.assertIn('Qt.MouseButton.RightButton', guard)

    def test_embedded_views_and_filter_have_same_guard(self):
        filtered = self.method_source('eventFilter')
        self.assertIn("getattr(self, 'tree', None)", filtered)
        self.assertIn('self.scroll_tree.viewport()', filtered)
        self.assertIn("getattr(self, 'filter_edit', None)", filtered)
        self.assertLess(filtered.index('_consume_unused_right_click'),
                        filtered.index('if self.scroll_tree is not None and obj is self.scroll_tree:'))


@unittest.skipUnless(app is not None, 'PySide6 is required for the Qt mouse test')
class CascadeRightClickIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'folder').mkdir()
        self.w = app.Launcher()
        self.w.show()

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.qt.processEvents()
        self.tmp.cleanup()

    def _menu(self, many=False):
        if many:
            for i in range(75):
                (self.root / f'{i:03}.txt').write_text('x', encoding='utf-8')
        self.w.cascade({'item_kind': 'directory', 'launch_browse_target': str(self.root)})
        self.qt.processEvents()
        return self.w.menu

    def test_compact_directory_menu_one_or_two_right_clicks_do_not_close(self):
        menu = self._menu()
        action = next(a for a in menu.actions() if
                      isinstance(a.data(), dict) and a.data().get('title') == 'folder')
        pos = menu.actionGeometry(action).center()
        with patch.object(self.w, 'run_menu_item') as open_item:
            for _ in range(2):
                QTest.mouseClick(menu, Qt.MouseButton.RightButton, pos=pos)
                self.qt.processEvents()
                self.assertTrue(menu.isVisible())
            QTest.mouseDClick(menu, Qt.MouseButton.RightButton, pos=pos)
            self.qt.processEvents()
            self.assertTrue(menu.isVisible())
            # Some Windows/Qt styles deliver this separately after mouse-up.
            menu_event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, pos)
            QApplication.sendEvent(menu, menu_event)
            self.qt.processEvents()
            self.assertTrue(menu.isVisible())
            open_item.assert_not_called()

    def test_scrollable_directory_menu_one_or_two_right_clicks_do_not_close(self):
        menu = self._menu(many=True)
        tree = menu.scroll_tree
        self.assertIsNotNone(tree)
        item = tree.topLevelItem(0)
        point = tree.visualItemRect(item).center()
        with patch.object(self.w, 'run_menu_item') as open_item:
            for _ in range(2):
                QTest.mouseClick(tree.viewport(), Qt.MouseButton.RightButton, pos=point)
                self.qt.processEvents()
                self.assertTrue(menu.isVisible())
            open_item.assert_not_called()

    def test_installed_apps_view_right_click_does_not_close(self):
        menu = app.AppCascadeMenu(parent=self.w, launcher=self.w)
        menu.populate([{'item_kind': 'command', 'item_id': 'dummy',
                        'title': 'Demo', 'description': ''}])
        menu.popup(self.w.mapToGlobal(self.w.rect().center()))
        self.qt.processEvents()
        self.assertTrue(menu.isVisible())
        with patch.object(self.w, 'run_menu_item') as open_item:
            for _ in range(2):
                QTest.mouseClick(menu.tree.viewport(), Qt.MouseButton.RightButton,
                                 pos=menu.tree.visualItemRect(menu.tree.topLevelItem(0)).center())
                self.qt.processEvents()
                self.assertTrue(menu.isVisible())
            open_item.assert_not_called()
        menu.close()


if __name__ == '__main__':
    unittest.main()
