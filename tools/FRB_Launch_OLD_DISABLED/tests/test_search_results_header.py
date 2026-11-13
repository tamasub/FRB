"""Two-column search-result header behavior (run on Windows/PySide6 Qt)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from pathlib import Path

try:
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import test_navigation
    import app
except ImportError:
    test_navigation = None


@unittest.skipIf(test_navigation is None, 'PySide6 is required for GUI tests')
class SearchHeaderTests(test_navigation.NavigationTests if test_navigation else unittest.TestCase):
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_selection_all_clear_and_back = None

    def setUp(self):
        super().setUp()
        self.w.result_sort_column = -1
        self.w.result_sort_desc = False
        self.w.settings.remove('result_sort_column')
        self.w.settings.remove('result_sort_desc')
        for name, description, order in (
            ('SORT_FIX_z', 'SORT_FIX_aaa', 1),
            ('SORT_FIX_a', 'SORT_FIX_zzz', 2),
            ('SORT_FIX_m', 'SORT_FIX_mmm', 3),
        ):
            self.w.data['items'].append({
                'item_id': name, 'title': name, 'description': description,
                'page_id': self.w.page_id, 'item_kind': 'command',
                'sort_order': order, 'enabled': True,
            })
        self.w.render()

    def listed_titles(self):
        return [self.w.list.topLevelItem(i).text(0)
                for i in range(self.w.list.topLevelItemCount())]

    def test_header_only_for_search_and_sort_both_columns(self):
        self.assertTrue(self.w.list.isHeaderHidden())
        self.w.search.setText('SORT_FIX')
        self.app.processEvents()
        self.assertFalse(self.w.list.isHeaderHidden())
        self.assertEqual(len(self.listed_titles()), 3)
        self.w.sort_search_column(0)
        self.assertEqual(self.listed_titles(), ['SORT_FIX_a', 'SORT_FIX_m', 'SORT_FIX_z'])
        self.w.sort_search_column(0)
        self.assertEqual(self.listed_titles(), ['SORT_FIX_z', 'SORT_FIX_m', 'SORT_FIX_a'])
        self.w.sort_search_column(1)
        self.assertEqual(self.listed_titles(), ['SORT_FIX_z', 'SORT_FIX_m', 'SORT_FIX_a'])
        self.w.sort_search_column(1)
        self.assertEqual(self.listed_titles(), ['SORT_FIX_a', 'SORT_FIX_m', 'SORT_FIX_z'])
        self.w.search.setText('SORT_FIX_*')
        self.assertEqual(self.listed_titles(), ['SORT_FIX_a', 'SORT_FIX_m', 'SORT_FIX_z'])
        self.w.search.clear()
        self.assertTrue(self.w.list.isHeaderHidden())
        self.assertTrue(self.w.list.order_enabled)

    def test_actual_header_mouse_click_sorts_both_columns(self):
        """Regression: setSortingEnabled(False) must not swallow header clicks."""
        self.w.search.setText('SORT_FIX')
        self.app.processEvents()
        header = self.w.list.header()
        self.assertTrue(header.sectionsClickable())

        def click(column):
            x = header.sectionViewportPosition(column) + header.sectionSize(column) // 2
            QTest.mouseClick(header.viewport(), Qt.MouseButton.LeftButton,
                             pos=QPoint(x, header.height() // 2))
            self.app.processEvents()

        click(0)  # title ascending
        self.assertEqual(self.listed_titles(), ['SORT_FIX_a', 'SORT_FIX_m', 'SORT_FIX_z'])
        click(0)  # title descending
        self.assertEqual(self.listed_titles(), ['SORT_FIX_z', 'SORT_FIX_m', 'SORT_FIX_a'])
        click(1)  # description ascending
        self.assertEqual(self.listed_titles(), ['SORT_FIX_z', 'SORT_FIX_m', 'SORT_FIX_a'])
        click(1)  # description descending
        self.assertEqual(self.listed_titles(), ['SORT_FIX_a', 'SORT_FIX_m', 'SORT_FIX_z'])

    def test_resized_column_width_persists_in_settings(self):
        self.w.search.setText('SORT_FIX')
        self.app.processEvents()
        self.w.list.header().resizeSection(0, 231)
        self.w.list.header().resizeSection(1, 181)
        self.assertEqual(int(self.w.settings.value('result_width_0')), 231)
        self.assertEqual(int(self.w.settings.value('result_width_1')), 181)
        self.w.search.clear()
        self.w.search.setText('SORT_FIX')
        self.assertEqual(self.w.list.columnWidth(0), 231)
        self.assertEqual(self.w.list.columnWidth(1), 181)


if __name__ == '__main__':
    unittest.main()
