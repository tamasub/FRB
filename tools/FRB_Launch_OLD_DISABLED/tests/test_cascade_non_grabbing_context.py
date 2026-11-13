"""Make context interaction independent of click-coordinate redirection."""
import ast
import pathlib
import unittest
from unittest.mock import Mock

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'src/app.py'


class CascadeStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.text)

    def source(self, cls_name, method):
        node = next(node for node in self.tree.body if isinstance(node, ast.ClassDef)
                    and node.name == cls_name)
        fn = next(node for node in node.body if isinstance(node, ast.FunctionDef)
                  and node.name == method)
        return ast.get_source_segment(self.text, fn)

    def test_cascade_is_not_mouse_grabbing_qt_popup(self):
        init = self.source('CascadeMenu', '__init__')
        self.assertIn('self.setWindowFlags(Qt.WindowType.Tool', init)
        self.assertNotIn('Qt.WindowType.Popup', init)

    def test_esc_equivalent_closes_popup_on_same_initial_press(self):
        event_filter = self.source('Launcher', 'eventFilter')
        self.assertLess(event_filter.index('self.close_cascade_for_main_interaction()'),
                        event_filter.index('self._launcher_context_press = True'))
        self.assertIn('self.show_launch_context_menu(event.globalPosition().toPoint(), row)', event_filter)
        dismiss = self.source('Launcher', 'close_cascade_for_main_interaction')
        self.assertIn('self.menu.close()', dismiss)
        self.assertNotIn('QCursor.pos()', dismiss)
        self.assertNotIn('sendEvent', dismiss)

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    import app
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication is not None, 'PySide6 needed for native popup regression')
class CascadeNativeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        cls.qt = QApplication.instance() or QApplication([])

    def test_cascade_does_not_register_as_active_modal_popup(self):
        w = app.Launcher()
        try:
            w.show()
            self.qt.processEvents()
            item = w.list.topLevelItem(0)
            if item is None:
                self.skipTest('No menu items to test')
            row = item.data(0, Qt.ItemDataRole.UserRole)
            if row.get('item_kind') not in ('category','directory'):
                self.skipTest('First item does not support cascading')
            w.cascade(row,item)
            self.qt.processEvents()
            self.assertTrue(w.menu.isVisible())
            self.assertIsNone(QApplication.activePopupWidget(),
                              'The cascade must not grab input like Qt.Popup')
            w.close_cascade_for_main_interaction()
            self.qt.processEvents()
            self.assertFalse(w.menu.isVisible())
        finally:
            w.tray.hide()
            w.close()

if __name__ == '__main__': unittest.main()
