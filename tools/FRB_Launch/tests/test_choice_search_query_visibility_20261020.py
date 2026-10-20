"""2026-10-20 regression: recipient OR search and Space focus ownership."""
import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import load, searchable_rows
from search_matching import choice_search_content, matches_choice_search

DATA = load(ROOT / 'config' / 'frb_launch_sample_data_v0_1.json')


class ChoiceSearchVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(DATA)
        self.se = [choice for choice in self.data['launch_choices']
                   if choice['group_id'] == 'se']

    def test_se001_internal_choice_id_must_not_match_004(self):
        se001 = next(choice for choice in self.se if choice['title'] == 'se001')
        self.assertIn('004', se001['choice_id'])
        self.assertNotIn('004', choice_search_content(se001))
        self.assertFalse(matches_choice_search(se001, '(003 or 004)'))

    def test_or_returns_only_se003_and_se004_in_recipient_picker(self):
        results = {choice['title'] for choice in self.se
                   if matches_choice_search(choice, '(003 or 004)')}
        self.assertEqual(results, {'se003', 'se004'})
        # A leading term is ANDed with the OR alternatives.
        self.assertEqual({c['title'] for c in self.se
                          if matches_choice_search(c, 'se (003 or 004)')},
                         {'se003', 'se004'})

    def test_search_ignores_internal_fields_but_keeps_user_fields(self):
        choice = next(c for c in self.se if c['title'] == 'se001')
        choice['group_id'] = 'secret_foobar'
        choice['sort_order'] = 34567
        choice['choice_id'] = 'internal_only_004'
        choice['action'] = 'secret_mail_action'
        for term in ('foobar', '34567', 'internal_only', 'secret_mail_action'):
            self.assertFalse(matches_choice_search(choice, term), term)
        for term in ('se001', 'se001@example.invalid', 'example.invalid'):
            self.assertTrue(matches_choice_search(choice, term), term)
        choice['keywords'] = ['営業', '一次窓口']
        self.assertTrue(matches_choice_search(choice, '一次窓口'))

    def test_global_search_does_not_leak_choice_ids(self):
        hits = [row['title'] for row, _ in searchable_rows(self.data, '(003 or 004)')
                if row.get('_search_selection_owner') and row.get('group_id') == 'se']
        self.assertEqual(set(hits), {'se003', 'se004'})
        self.assertEqual(len(hits), 2)

    def test_global_search_can_use_selection_owner_display_path(self):
        hits = [row['title'] for row, _ in searchable_rows(self.data, 'SE部 se003')
                if row.get('_search_selection_owner')]
        self.assertEqual(hits, ['se003'])


os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import app as module
except ImportError:
    module = None


@unittest.skipUnless(module is not None, 'PySide6 is required for GUI tests')
class ChoiceSearchSpaceUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.temp = tempfile.TemporaryDirectory()
        cls.orig_state = module.STATE
        module.STATE = Path(cls.temp.name)
        module.windows.hotkey = lambda *args: None
        module.windows.unhotkey = lambda *args: None

    @classmethod
    def tearDownClass(cls):
        module.STATE = cls.orig_state
        cls.temp.cleanup()

    def setUp(self):
        self.w = module.Launcher()
        self.w.show()
        self.w.search.setFocus()
        self.app.processEvents()

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.app.processEvents()

    def test_space_always_types_in_search_box_even_with_visible_checkboxes(self):
        owner = next(row for row in self.w.data['items']
                     if row['item_kind'] == 'selection' and row['launch_selection_group_id'] == 'se')
        self.w.activate(owner)
        self.w.search.setText('(003 or 004)')
        self.w.search.setFocus()
        self.app.processEvents()
        self.assertEqual(self.w.list.topLevelItemCount(), 2)
        self.assertEqual(self.w.checked, set())
        QTest.keyClick(self.w.search, Qt.Key.Key_Space)
        self.app.processEvents()
        self.assertEqual(self.w.search.text(), '(003 or 004) ')
        self.assertEqual(self.w.checked, set())
        self.assertEqual(self.w.list.topLevelItemCount(), 2)
        # Space still toggles the selected recipient with list focus.
        self.w.list.setFocus()
        self.app.processEvents()
        QTest.keyClick(self.w.list, Qt.Key.Key_Space)
        self.assertEqual(len(self.w.checked), 1)

    def test_global_choice_search_space_is_text_and_enter_selects(self):
        self.w.search.setText('se003')
        self.w.search.setFocus()
        self.app.processEvents()
        self.assertIsNone(self.w.selection)
        self.assertGreater(self.w.list.topLevelItemCount(), 0)
        QTest.keyClick(self.w.search, Qt.Key.Key_Space)
        self.assertEqual(self.w.search.text(), 'se003 ')
        self.assertIsNone(self.w.selection)
        QTest.keyClick(self.w.search, Qt.Key.Key_Return)
        self.assertIsNotNone(self.w.selection)
        self.assertEqual(self.w.checked,
                         {next(c['choice_id'] for c in self.w.data['launch_choices']
                               if c['title'] == 'se003')})


if __name__ == '__main__':
    unittest.main()
