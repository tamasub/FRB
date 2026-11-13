"""FRB Launch: Explorer-like row states, independent of Qt GUI backend."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from main_grid_visual_state import (ROW_PALETTE, row_visual_state,
                                    row_fill, row_has_outline)


class MainGridVisualStateTests(unittest.TestCase):
    def test_current_without_grid_focus_has_outline_only(self):
        state = row_visual_state(current=True, focused=False, hovered=False)
        self.assertEqual(state, 'inactive_current')
        self.assertTrue(row_has_outline(state))
        for palette in ROW_PALETTE.values():
            self.assertIsNone(row_fill(palette, state))

    def test_current_with_grid_focus_has_blue_and_outline(self):
        state = row_visual_state(current=True, focused=True, hovered=False)
        self.assertEqual(state, 'focused_current')
        self.assertTrue(row_has_outline(state))
        for palette in ROW_PALETTE.values():
            self.assertIsNotNone(row_fill(palette, state))

    def test_hover_without_focus_fills_without_outline(self):
        state = row_visual_state(current=False, focused=False, hovered=True)
        self.assertEqual(state, 'hover')
        self.assertFalse(row_has_outline(state))
        for palette in ROW_PALETTE.values():
            self.assertIsNotNone(row_fill(palette, state))

    def test_pointer_over_inactive_current_fills_without_outline(self):
        state = row_visual_state(current=True, focused=False, hovered=True)
        self.assertEqual(state, 'hover')
        self.assertFalse(row_has_outline(state))

    def test_keyboard_current_remains_distinct_from_hover(self):
        self.assertEqual(row_visual_state(current=True, focused=True,
                                          hovered=True), 'focused_current')
        self.assertTrue(row_has_outline('focused_current'))
        self.assertEqual(row_visual_state(current=False, focused=True,
                                          hovered=True), 'hover')

    def test_regular_row_never_has_fill_or_outline(self):
        for focused in (True, False):
            state = row_visual_state(current=False, focused=focused,
                                     hovered=False)
            self.assertEqual(state, 'normal')
            self.assertFalse(row_has_outline(state))
            for palette in ROW_PALETTE.values():
                self.assertIsNone(row_fill(palette, state))

    def test_both_themes_have_distinct_blue_fill_and_border(self):
        for theme in ('light', 'dark'):
            palette = ROW_PALETTE[theme]
            for prop in ('focused_current', 'hover', 'outline'):
                self.assertRegex(palette[prop], r'^#[0-9a-fA-F]{6}$')
            self.assertNotEqual(palette['hover'], palette['outline'])


try:
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt, QTimer, QPoint
    from PySide6.QtWidgets import QApplication, QTreeWidgetItem, QLineEdit
    from PySide6.QtTest import QTest
    from reorder_widgets import ReorderTree, MainGridRowDelegate
except ImportError:
    ReorderTree = None


@unittest.skipUnless(ReorderTree is not None, 'PySide6 required for GUI visual-state tests')
class MainGridVisualQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        class Owner:
            hover_timer = QTimer()
            pending_menu_item = None
            _column_mode = 'result'
            _main_column_hover = False
        self.tree = ReorderTree(Owner())
        self.tree.setColumnCount(2)
        self.tree.setMouseTracking(True)
        self.tree.resize(500, 200)
        for ix in range(3):
            self.tree.addTopLevelItem(QTreeWidgetItem([f'item {ix}', 'description']))
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        self.tree.show()
        self.app.processEvents()

    def tearDown(self):
        self.tree.close()
        self.tree.deleteLater()
        self.app.processEvents()

    def test_delegate_does_not_change_actual_current_item(self):
        self.assertIsInstance(self.tree.itemDelegate(), MainGridRowDelegate)
        self.tree.setFocus()
        self.app.processEvents()
        self.assertEqual(self.tree.row_state_for_index(
            self.tree.model().index(0, 0)), 'focused_current')
        self.tree.clearFocus()
        self.app.processEvents()
        self.assertEqual(self.tree.row_state_for_index(
            self.tree.model().index(0, 0)), 'inactive_current')
        self.assertEqual(self.tree.currentItem(), self.tree.topLevelItem(0))

    def test_mouse_hover_does_not_move_keyboard_current_item(self):
        self.tree.clearFocus()
        pos = self.tree.visualItemRect(self.tree.topLevelItem(1)).center()
        QTest.mouseMove(self.tree.viewport(), pos)
        self.app.processEvents()
        self.assertEqual(self.tree.row_state_for_index(
            self.tree.model().index(1, 0)), 'hover')
        self.assertEqual(self.tree.currentItem(), self.tree.topLevelItem(0))
        self.assertEqual(self.tree.row_state_for_index(
            self.tree.model().index(0, 1)), 'inactive_current')

    def _blank_row_pixel(self, row):
        # Check the color at the far right of the viewport, beyond both texts.
        rect = self.tree.visualItemRect(self.tree.topLevelItem(row))
        image = self.tree.viewport().grab().toImage()
        return image.pixelColor(image.width() - 25, rect.center().y()).name()

    def test_actual_row_pixels_track_focus_and_hover(self):
        """The stylesheet must not erase Qt's custom highlight fill."""
        self.tree.setObjectName('mainLaunchList')
        self.tree.setStyleSheet("""
            QTreeWidget { background:#202b29; border:0; outline:0; }
            QTreeWidget::item { height:35px; padding:0 6px; }
            QTreeWidget#mainLaunchList::item:selected,
            QTreeWidget#mainLaunchList::item:hover { background:transparent; }
        """)
        self.tree.set_row_theme('dark')
        self.tree.setFocus()
        self.app.processEvents()
        self.assertEqual(self._blank_row_pixel(0), ROW_PALETTE['dark']['focused_current'])
        other = QLineEdit()
        other.show()
        other.activateWindow()
        other.setFocus()
        self.app.processEvents()
        self.assertEqual(self._blank_row_pixel(0), '#202b29')
        pos = self.tree.visualItemRect(self.tree.topLevelItem(1)).center()
        QTest.mouseMove(self.tree.viewport(), pos)
        self.app.processEvents()
        self.assertEqual(self._blank_row_pixel(1), ROW_PALETTE['dark']['hover'])
        self.assertEqual(self.tree.currentItem(), self.tree.topLevelItem(0))
        other.close()

    def test_theme_switch_and_rebuild_repaints(self):
        self.tree.set_row_theme('light')
        self.assertEqual(self.tree.row_palette, ROW_PALETTE['light'])
        self.tree.set_row_theme('dark')
        self.assertEqual(self.tree.row_palette, ROW_PALETTE['dark'])
        self.tree._hover_item = self.tree.topLevelItem(2)
        self.tree.clear_row_hover()
        self.assertIsNone(self.tree._hover_item)


if __name__ == '__main__':
    unittest.main()
