"""Column-local cascade search. Run with QT_QPA_PLATFORM=offscreen."""
import unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import test_navigation
import app as module


class ColumnFilterTests(test_navigation.NavigationTests):
    # Reuse the real launcher setup, but not the inherited test cases.
    test_immediate_right_and_left = None
    test_nested_and_directory_single_column = None
    test_function_page_keys = None
    test_selection_all_clear_and_back = None

    def make_menu(self):
        path = Path(self.temp.name) / 'column_fixture'
        path.mkdir(exist_ok=True)
        for folder in ('FRB_Alpha', 'FRB_Beta', 'Other'):
            (path / folder).mkdir(exist_ok=True)
        (path / 'FRB_Alpha' / 'depth.txt').touch()
        (path / 'launch.txt').touch()
        self.w.cascade(dict(item_kind='directory', launch_browse_target=str(path)))
        self.app.processEvents()
        return self.w.menu

    @staticmethod
    def visible_titles(menu):
        return [a.data()['title'] for a in menu.actions()
                if a.isVisible() and isinstance(a.data(), dict)]

    def test_search_is_visible_immediately_and_is_local(self):
        menu = self.make_menu()
        self.assertIsNotNone(menu.filter_edit)
        self.assertTrue(menu.filter_edit.isVisible())
        QTest.keyClicks(menu.filter_edit, 'frb')
        self.app.processEvents()
        self.assertEqual(menu.filter_edit.text(), 'frb')
        self.assertEqual(self.visible_titles(menu), ['FRB_Alpha', 'FRB_Beta'])
        self.assertTrue(menu.isVisible())
        self.assertEqual(self.w.search.text(), '')
        self.assertEqual(menu.filter_count.text(), '2/4')
        self.assertFalse(menu.order_enabled)

    def test_arrow_right_enters_matching_child(self):
        menu = self.make_menu()
        QTest.keyClicks(menu.filter_edit, 'alpha')
        edit = menu.filter_edit
        self.assertEqual(menu.activeAction().data()['title'], 'FRB_Alpha')
        # Right inside the editor moves the caret, not the cascade.
        QTest.keyClick(edit, Qt.Key.Key_Right)
        self.assertIsNone(menu.child)
        QTest.keyClick(edit, Qt.Key.Key_Return)
        self.app.processEvents()
        self.assertIsNotNone(menu.child)
        self.assertTrue(menu.child.isVisible())
        self.assertIsNotNone(menu.child.filter_edit)
        QTest.keyClicks(menu.child.filter_edit, 'depth')
        self.assertEqual(self.visible_titles(menu.child), ['depth.txt'])
        self.assertEqual(self.visible_titles(menu), ['FRB_Alpha'])

    def test_escape_resets_filter_without_closing_menu(self):
        menu = self.make_menu()
        original = self.visible_titles(menu)
        QTest.keyClicks(menu.filter_edit, 'frb')
        QTest.keyClick(menu.filter_edit, Qt.Key.Key_Escape)
        self.app.processEvents()
        self.assertIsNotNone(menu.filter_edit)
        self.assertEqual(menu.filter_edit.text(), '')
        self.assertEqual(self.visible_titles(menu), original)
        self.assertTrue(menu.isVisible())
        QTest.keyClick(menu, Qt.Key.Key_Escape)
        self.assertFalse(menu.isVisible())

    def test_zero_hit_and_edit_clear(self):
        menu = self.make_menu()
        QTest.keyClicks(menu.filter_edit, 'zzzx')
        self.assertEqual(self.visible_titles(menu), [])
        self.assertIsNone(menu.activeAction())
        QTest.keyClick(menu.filter_edit, Qt.Key.Key_Right)
        self.assertIsNone(menu.child)
        menu.filter_edit.clear()
        self.app.processEvents()
        self.assertIsNotNone(menu.filter_edit)
        self.assertEqual(len(self.visible_titles(menu)), 4)

    def test_filter_does_not_shrink_popup_frame(self):
        # Regression: filtering a long folder to a handful of matches made its
        # menu window collapse next to an open nested menu.
        path = Path(self.temp.name) / 'long_column_fixture'
        path.mkdir(exist_ok=True)
        for index in range(39):
            (path / f'entry_{index:02}.txt').touch()
        (path / 'tools').mkdir(exist_ok=True)
        self.w.cascade(dict(item_kind='directory', launch_browse_target=str(path)))
        self.app.processEvents()
        menu = self.w.menu
        original_size = menu.size()
        original_minimum = menu.minimumSize()
        QTest.keyClicks(menu.filter_edit, 'tools')
        self.app.processEvents()
        self.assertEqual(self.visible_titles(menu), ['tools'])
        self.assertGreaterEqual(menu.height(), original_size.height())
        self.assertGreaterEqual(menu.width(), original_size.width())
        menu.filter_edit.setText('unmatched-search-word')
        self.app.processEvents()
        self.assertEqual(self.visible_titles(menu), [])
        self.assertGreaterEqual(menu.height(), original_size.height())
        self.assertGreaterEqual(menu.width(), original_size.width())
        QTest.keyClick(menu.filter_edit, Qt.Key.Key_Escape)
        self.app.processEvents()
        self.assertEqual(menu.minimumSize(), original_minimum)
        self.assertIsNotNone(menu.filter_edit)
        self.assertEqual(len(self.visible_titles(menu)), 40)

    def test_regular_category_and_apps_exclusion(self):
        root = next(row for row in self.w.data['items'] if row.get('item_kind')=='category'
                    and row.get('launch_source')!='installed_apps')
        self.w.cascade(root)
        menu = self.w.menu
        QTest.keyClicks(menu.filter_edit, 'test')
        self.assertIsNotNone(menu.filter_edit)
        self.assertEqual(self.w.search.text(), '')
        self.w.cascade(dict(item_kind='category', item_id='app_fixture', page_id=self.w.page_id,
                            launch_source='installed_apps'))
        appmenu = self.w.menu
        self.assertIsInstance(appmenu, module.AppCascadeMenu)
        self.assertIsNone(appmenu.filter_edit)

if __name__ == '__main__':
    unittest.main()
