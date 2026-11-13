"""Search-history UI integration (executed on Windows with PySide6).

Intentionally uses actual key and mouse events, not merely calling the
handler, to catch focus/shortcut wiring regressions.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest

try:
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtGui import QInputMethodEvent
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

    def test_japanese_preedit_from_history_closes_and_moves_to_search(self):
        QTest.keyClicks(self.w.search, '/')
        self.assertTrue(self.w.history_popup.isVisible())
        self.assertTrue(self.w.history_choices.hasFocus())
        # Windows Japanese IME sends preedit before textChanged or commit.
        preedit = QInputMethodEvent('にほん', [])
        self.app.sendEvent(self.w.history_choices, preedit)
        self.app.processEvents()
        self.assertFalse(self.w.history_popup.isVisible())
        self.assertTrue(self.w.search.hasFocus())
        commit = QInputMethodEvent()
        commit.setCommitString('日本語')
        self.app.sendEvent(self.w.search, commit)
        self.assertIn('日本語', self.w.search.text())

    def test_typing_or_pasting_into_search_closes_history(self):
        QTest.keyClicks(self.w.search, '/')
        self.assertTrue(self.w.history_popup.isVisible())
        self.w.search.setText('日本語')
        self.assertFalse(self.w.history_popup.isVisible())

    def test_escape_preserves_existing_query(self):
        self.w.search.setText('MyCurrentQuery')
        QTest.keyClicks(self.w.search, '/')
        QTest.keyClick(self.w.history_choices, Qt.Key.Key_Escape)
        self.assertEqual(self.w.search.text(), 'MyCurrentQuery')

    def test_mouse_reorder_delete_and_json_reload(self):
        # History now appears as children of the fixed 未分類 folder. Manual
        # dragging persists *folder-local* order without scrambling the
        # original flat search_history.json data.
        QTest.keyClicks(self.w.search, '/')
        self.assertTrue(self.w.history_popup.isVisible())
        self.w.history_choices.structureChanged.emit('keyword', 'FRB*.md', 'uncategorized', 0)
        self.assertEqual(self.w.search_categories.group_items('uncategorized')[:2],
                         ['FRB*.md', '*.ps1'])
        self.w.history_choices.structureChanged.emit('keyword', '*.ps1', 'uncategorized', 0)
        self.assertEqual(self.w.search_categories.group_items('uncategorized')[:2],
                         ['*.ps1', 'FRB*.md'])
        view = self.w.history_choices
        first = self.w.history_category_row('uncategorized').child(0)
        rect = view.visualItemRect(first)
        x = view.columnWidth(0) + view.columnWidth(1) // 2
        QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=QPoint(x, rect.center().y()))
        self.app.processEvents()
        self.assertEqual(self.w.search_history.keywords, ['FRB*.md', 'make'])
        self.assertEqual(type(self.w.search_history)(self.w.search_history.path).keywords,
                         self.w.search_history.keywords)
        self.assertEqual(self.w.search_categories.group_items('uncategorized'),
                         ['FRB*.md', 'make'])

    def test_create_expand_collapse_and_reclassify(self):
        QTest.keyClicks(self.w.search, '/')
        self.assertTrue(self.w.history_popup.isVisible())
        self.assertEqual(self.w.history_choices.topLevelItem(0).data(0, 257), 'session_history')
        self.assertEqual(self.w.history_choices.topLevelItem(1).data(0, 257), 'uncategorized')
        self.w.history_choices.structureChanged.emit('keyword', '*.ps1', 'windows', 0)
        self.assertIn('*.ps1', self.w.search_categories.group_items('windows'))
        self.w.history_expand_button.click()
        self.assertTrue(self.w.search_categories.expanded('windows'))
        self.w.history_collapse_button.click()
        self.assertFalse(self.w.search_categories.expanded('windows'))
        self.w.history_expand_button.click()
        self.assertTrue(self.w.search_categories.expanded('windows'))

    def test_slash_paste_is_stripped_and_history_is_only_explicit(self):
        self.w.search.setText('ab/c')
        self.assertEqual(self.w.search.text(), 'abc')
        self.w.search.setText('*.xlsx')
        self.assertTrue(self.w.save_history_button.isVisible())
        self.w.dismiss()
        self.assertNotIn('*.xlsx', type(self.w.search_history)(self.w.search_history.path).keywords)
        self.w.show()
        self.w.save_history_button.click()
        self.assertIn('*.xlsx', type(self.w.search_history)(self.w.search_history.path).keywords)


if __name__ == '__main__':
    unittest.main()
