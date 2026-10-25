"""Windows/PySide6 regression: the main history must dismiss on outside clicks."""
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
class HistoryPopupOutsideClickTests(test_navigation.NavigationTests if test_navigation else unittest.TestCase):
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_main_list_right_executes_leaf = None
    test_selection_right_toggles_recipients_and_keeps_f12 = None
    test_selection_right_from_search_preserves_text_caret = None
    test_selection_all_clear_and_back = None

    def setUp(self):
        super().setUp()
        self.w.search_history.keywords = ['alpha', 'beta']
        self.w.search_history._save()
        self.w.show_history_popup()
        self.app.processEvents()

    def test_click_unrelated_main_header_area_closes_without_swallowing_event(self):
        self.assertTrue(self.w.history_popup.isVisible())
        QTest.mouseClick(self.w.mode_bar, Qt.MouseButton.LeftButton,
                         pos=QPoint(self.w.mode_bar.width()-2, 2))
        self.app.processEvents()
        self.assertFalse(self.w.history_popup.isVisible())

    def test_click_search_field_keeps_history_open(self):
        QTest.mouseClick(self.w.search, Qt.MouseButton.LeftButton,
                         pos=QPoint(self.w.search.width()//2, self.w.search.height()//2))
        self.app.processEvents()
        self.assertTrue(self.w.history_popup.isVisible())


if __name__ == '__main__':
    unittest.main()
