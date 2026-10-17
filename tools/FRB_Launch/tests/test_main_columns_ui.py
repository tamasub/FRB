"""GUI regression tests; run on Windows/PySide6 with Qt offscreen support."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
try:
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtTest import QTest
    import test_navigation
except ImportError:
    test_navigation = None


@unittest.skipIf(test_navigation is None, 'PySide6 is required for GUI tests')
class MainMenuColumnTests(test_navigation.NavigationTests if test_navigation else unittest.TestCase):
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_selection_all_clear_and_back = None

    def setUp(self):
        super().setUp()
        self.w.search.clear()
        self.w.render()
        self.w.show()
        self.app.processEvents()

    def test_main_divider_drag_and_search_widths_are_separate(self):
        self.assertTrue(self.w.list.isHeaderHidden())
        viewport = self.w.list.viewport()
        old = self.w.list.columnWidth(0)
        divider = self.w.list.columnViewportPosition(1)
        y = self.w.list.visualItemRect(self.w.list.topLevelItem(0)).center().y()
        QTest.mouseMove(viewport, QPoint(divider, y))
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=QPoint(divider, y))
        QTest.mouseMove(viewport, QPoint(divider + 34, y))
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=QPoint(divider + 34, y))
        self.app.processEvents()
        self.assertEqual(self.w.list.columnWidth(0), old + 34)
        self.assertEqual(int(self.w.settings.value('main_width_0')), old + 34)

        self.w.search.setText('bat')
        self.app.processEvents()
        self.assertFalse(self.w.list.isHeaderHidden())
        self.w.list.header().resizeSection(0, 201)
        self.assertEqual(int(self.w.settings.value('result_width_0')), 201)
        self.w.search.clear()
        self.app.processEvents()
        self.assertTrue(self.w.list.isHeaderHidden())
        self.assertEqual(self.w.list.columnWidth(0), old + 34)
        self.w.search.setText('bat')
        self.assertEqual(self.w.list.columnWidth(0), 201)

    def test_popup_anchor_not_affected_by_main_column_width(self):
        viewport = self.w.list.viewport()
        item = self.w.list.topLevelItem(0)
        row = item.data(0, Qt.ItemDataRole.UserRole)
        if row.get('item_kind') not in ('category', 'directory'):
            self.skipTest('First row does not open a cascade menu')
        right = viewport.mapToGlobal(QPoint(viewport.width() - 1, 0)).x()
        first_width = self.w.list.columnWidth(0)
        self.w.list.setColumnWidth(0, min(viewport.width() - 90, first_width + 80))
        self.w.cascade(row, item)
        self.app.processEvents()
        if self.w.menu:
            # No more 30+px gap due to visualItemRect extending off viewport.
            self.assertLessEqual(abs(self.w.menu.pos().x() - right), 12)
            self.w.menu.close()


if __name__ == '__main__':
    unittest.main()
