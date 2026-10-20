"""Global search finds selection choices, without inventing actions for them."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import load, searchable_rows

DATA = load(Path(__file__).resolve().parents[1] / 'config/frb_launch_sample_data_v0_1.json')


class ChoiceSearchCoreTests(unittest.TestCase):
    def hits(self, data, query):
        return [(r, path) for r, path in searchable_rows(data, query)
                if r.get('_search_selection_owner')]

    def test_find_people_by_name_from_main_search(self):
        hits = self.hits(DATA, '田中')
        self.assertEqual(len(hits), 1)
        person, path = hits[0]
        self.assertEqual(person['choice_id'], next(c['choice_id'] for c in DATA['launch_choices'] if c['title'].startswith('田中')))
        self.assertEqual(person['_search_selection_owner'], 'sales')
        self.assertEqual(person['item_kind'], 'choice')
        self.assertIn('メール宛先', path)
        self.assertIn('営業部 E-MAIL', path)

    def test_find_people_by_email_and_group_name(self):
        self.assertEqual([r['choice_id'] for r, _ in self.hits(DATA, 'sato@example.invalid')], [next(c['choice_id'] for c in DATA['launch_choices'] if c['title'].startswith('佐藤'))])
        self.assertEqual([r['choice_id'] for r, _ in self.hits(DATA, '営業部 鈴木')], [next(c['choice_id'] for c in DATA['launch_choices'] if c['title'].startswith('鈴木'))])

    def test_regular_search_results_remain_available(self):
        self.assertEqual({r['item_id'] for r, _ in searchable_rows(DATA, 'appdata')}, {'roaming', 'local'})

    def test_disabled_choice_owner_ancestor_and_page_are_ignored(self):
        for kind in ('choice', 'owner', 'ancestor', 'page'):
            with self.subTest(kind=kind):
                data = copy.deepcopy(DATA)
                if kind == 'choice':
                    next(c for c in data['launch_choices'] if c['title'].startswith('田中'))['enabled'] = False
                elif kind == 'owner':
                    next(i for i in data['items'] if i['item_id'] == 'sales')['enabled'] = False
                elif kind == 'ancestor':
                    next(i for i in data['items'] if i['item_id'] == 'mail')['enabled'] = False
                else:
                    next(p for p in data['pages'] if p['page_id'] == 'work')['enabled'] = False
                self.assertEqual(self.hits(data, '田中'), [])

    def test_additional_selection_group_can_be_found_without_code_changes(self):
        data = copy.deepcopy(DATA)
        owner = copy.deepcopy(next(i for i in data['items'] if i['item_id'] == 'sales'))
        owner.update(item_id='frb_contacts', page_id='frb', parent_item_id='',
                     title='FRB担当者', launch_selection_group_id='frb_contacts')
        data['items'].append(owner)
        data['launch_choices'].append({'choice_id': 'frb_1', 'group_id': 'frb_contacts',
                                       'title': '研究担当 山田', 'description': 'yamada@example.invalid',
                                       'value': 'yamada@example.invalid', 'sort_order': 1,
                                       'enabled': True})
        hits = self.hits(data, '山田')
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0]['_search_selection_owner'], 'frb_contacts')
        self.assertIn('FRB実験', hits[0][1])


try:
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from PySide6.QtTest import QTest
    import tempfile
    import app as module
except ImportError:
    module = None


@unittest.skipUnless(module is not None, 'PySide6 is required for GUI tests')
class ChoiceSearchUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.prev_state = module.STATE
        module.STATE = Path(cls.tmp.name)
        module.windows.hotkey = lambda *args: None
        module.windows.unhotkey = lambda *args: None

    @classmethod
    def tearDownClass(cls):
        module.STATE = cls.prev_state
        cls.tmp.cleanup()

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

    def test_search_space_is_text_and_enter_f12_reuses_original_selection_action(self):
        tanaka_id = next(c['choice_id'] for c in self.w.data['launch_choices']
                         if c['title'].startswith('田中'))
        sato_id = next(c['choice_id'] for c in self.w.data['launch_choices']
                       if c['title'].startswith('佐藤'))
        self.w.search.setText('田中')
        self.app.processEvents()
        self.assertEqual(self.w.list.topLevelItemCount(), 1)
        hit = self.w.list.currentItem()
        self.assertEqual(hit.data(0, Qt.ItemDataRole.UserRole)['choice_id'], tanaka_id)
        self.assertEqual(hit.checkState(0), Qt.CheckState.Unchecked)

        QTest.keyClick(self.w.search, Qt.Key.Key_Space)
        self.assertEqual(self.w.search.text(), '田中 ')
        self.assertIsNone(self.w.selection)
        self.assertEqual(self.w.list.currentItem().checkState(0), Qt.CheckState.Unchecked)
        QTest.keyClick(self.w.search, Qt.Key.Key_Return)
        self.assertEqual(self.w.selection['item_id'], 'sales')
        self.assertEqual(self.w.checked, {tanaka_id})

        # Preserve the previously selected recipient while searching for another.
        self.w.search.setText('佐藤')
        self.w.search.setFocus()
        self.app.processEvents()
        QTest.keyClick(self.w.search, Qt.Key.Key_Space)
        self.assertEqual(self.w.search.text(), '佐藤 ')
        self.assertEqual(self.w.checked, {tanaka_id})
        QTest.keyClick(self.w.search, Qt.Key.Key_Return)
        self.assertEqual(self.w.checked, {tanaka_id, sato_id})
        sent = []
        self.w.execute = lambda row, values=None: sent.append((row, values))
        QTest.keyClick(self.w.list, Qt.Key.Key_F12)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0][0]['item_id'], 'sales')
        self.assertEqual(sent[0][1], {'recipients': 'tanaka@example.invalid; sato@example.invalid'})

    def test_nonchoice_search_keeps_spaces_as_search_text(self):
        self.w.search.setText('appdata')
        self.app.processEvents()
        self.assertIsNone(self.w.selection)
        QTest.keyClick(self.w.search, Qt.Key.Key_Space)
        self.assertIsNone(self.w.selection)
        self.assertEqual(self.w.search.text(), 'appdata ')

    def test_mouse_checkbox_on_global_result_enters_selection(self):
        self.w.search.setText('鈴木')
        self.app.processEvents()
        item = self.w.list.currentItem()
        item.setCheckState(0, Qt.CheckState.Checked)
        self.assertEqual(self.w.selection['item_id'], 'sales')
        self.assertEqual(self.w.checked, {next(c['choice_id'] for c in self.w.data['launch_choices'] if c['title'].startswith('鈴木'))})


if __name__ == '__main__':
    unittest.main()
