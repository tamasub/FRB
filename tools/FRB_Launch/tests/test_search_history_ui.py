"""Search-history UI integration (executed on Windows with PySide6).

Intentionally uses actual key and mouse events, not merely calling the
handler, to catch focus/shortcut wiring regressions.
"""
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
class SearchHistoryUITests(test_navigation.NavigationTests if test_navigation else unittest.TestCase):
    # The parent provides window setup/teardown; do not rerun its navigation tests.
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_main_list_right_executes_leaf = None
    test_selection_right_toggles_recipients_and_keeps_f12 = None
    test_selection_right_from_search_preserves_text_caret = None
    test_selection_all_clear_and_back = None

    def setUp(self):
        super().setUp()
        self.w.search_history.keywords = ['*.ps1', 'FRB*.md', 'make']
        self.w.search_history._save()

    def test_slash_opens_and_closes_from_search_without_typing(self):
        QTest.keyClicks(self.w.search, '/')
        self.app.processEvents()
        self.assertTrue(self.w.history_popup.isVisible())
        self.assertEqual(self.w.search.text(), '')
        self.assertTrue(self.w.history_choices.hasFocus())
        QTest.keyClick(self.w.history_choices, Qt.Key.Key_Escape)
        self.assertFalse(self.w.history_popup.isVisible())
        self.assertTrue(self.w.search.hasFocus())

    def test_down_enter_runs_search_but_does_not_open_result(self):
        launched = []
        self.w.activate = lambda row: launched.append(row)
        self.w.search.setText('before')
        QTest.keyClicks(self.w.search, '/')
        QTest.keyClick(self.w.history_choices, Qt.Key.Key_Down)
        QTest.keyClick(self.w.history_choices, Qt.Key.Key_Return)
        self.assertFalse(self.w.history_popup.isVisible())
        self.assertEqual(self.w.search.text(), 'FRB*.md')
        self.assertTrue(self.w.list.hasFocus())
        self.assertEqual(launched, [])

    def test_right_and_tab_also_commit_search(self):
        for key in (Qt.Key.Key_Right, Qt.Key.Key_Tab):
            self.w.search.clear()
            QTest.keyClicks(self.w.search, '/')
            self.assertTrue(self.w.history_popup.isVisible())
            QTest.keyClick(self.w.history_choices, key)
            self.assertEqual(self.w.search.text(), '*.ps1')
            self.assertFalse(self.w.history_popup.isVisible())
            self.assertTrue(self.w.list.hasFocus())

    def test_escape_preserves_existing_query(self):
        self.w.search.setText('MyCurrentQuery')
        QTest.keyClicks(self.w.search, '/')
        QTest.keyClick(self.w.history_choices, Qt.Key.Key_Escape)
        self.assertEqual(self.w.search.text(), 'MyCurrentQuery')

    def test_mouse_reorder_delete_and_json_reload(self):
        QTest.keyClicks(self.w.search, '/')
        self.assertTrue(self.w.history_popup.isVisible())
        def click(row_index, column):
            view = self.w.history_choices
            row = view.topLevelItem(row_index)
            x = sum(view.columnWidth(c) for c in range(column)) + view.columnWidth(column) // 2
            y = view.visualItemRect(row).center().y()
            QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x,y))
            self.app.processEvents()
        click(1, 1)  # FRB*.md -> up
        self.assertEqual(self.w.search_history.keywords[:2], ['FRB*.md', '*.ps1'])
        click(0, 2)  # FRB*.md -> down
        self.assertEqual(self.w.search_history.keywords[:2], ['*.ps1', 'FRB*.md'])
        click(0, 3)  # delete *.ps1
        self.assertEqual(self.w.search_history.keywords, ['FRB*.md', 'make'])
        self.assertEqual(type(self.w.search_history)(self.w.search_history.path).keywords,
                         self.w.search_history.keywords)

    def test_slash_paste_is_stripped_and_manual_search_saved_on_dismiss(self):
        self.w.search.setText('ab/c')
        self.assertEqual(self.w.search.text(), 'abc')
        self.w.search.setText('*.xlsx')
        self.w.dismiss()
        self.assertIn('*.xlsx', type(self.w.search_history)(self.w.search_history.path).keywords)


if __name__ == '__main__':
    unittest.main()
