"""Run with QT_QPA_PLATFORM=offscreen for a headless UI regression check."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from pathlib import Path
import tempfile
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import app as module

class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.temp = tempfile.TemporaryDirectory()
        module.STATE = Path(cls.temp.name)
        module.windows.hotkey = lambda *args: None
        module.windows.unhotkey = lambda *args: None

    def setUp(self):
        self.w = module.Launcher()
        self.w.page_id = 'work'
        self.w.render(); self.w.show(); self.w.search.setFocus()
        self.app.processEvents()

    def tearDown(self):
        self.w.dismiss(); self.w.tray.hide(); self.w.deleteLater()
        self.app.processEvents()

    def test_immediate_right_and_left(self):
        QTest.keyClick(self.w.search, Qt.Key.Key_Right)
        menu = self.w.menu
        self.assertTrue(menu.isVisible())
        self.assertEqual(menu.activeAction(), menu.actions()[0])
        QTest.keyClick(menu, Qt.Key.Key_Left)
        self.assertFalse(menu.isVisible())

    def test_nested_and_directory_single_column(self):
        root = Path(self.temp.name) / 'files'; root.mkdir(exist_ok=True)
        (root/'child').mkdir(exist_ok=True)
        for n in range(70): (root/f'file{n:03}.txt').touch()
        row = dict(item_kind='directory', launch_browse_target=str(root))
        self.w.cascade(row)
        menu = self.w.menu
        self.assertEqual(menu.columnCount(), 1)
        self.assertTrue(any(a.text()=='file000.txt' for a in menu.actions()))
        QTest.qWait(400)
        self.assertIsNone(menu.child)
        QTest.keyClick(menu, Qt.Key.Key_Right)
        sub = menu.child
        self.assertTrue(sub.isVisible())
        self.assertIsNotNone(sub.activeAction())
        QTest.keyClick(sub, Qt.Key.Key_Left)
        self.assertFalse(sub.isVisible())
        self.assertTrue(menu.isVisible())
        QTest.qWait(400)
        self.assertFalse(sub.isVisible())
        QTest.keyClick(menu, Qt.Key.Key_Right)
        self.assertTrue(menu.child.isVisible())
        QTest.keyClick(menu.child, Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier)
        self.assertFalse(menu.isVisible())
        self.assertEqual(QApplication.focusWidget(), self.w.search)
        self.w.cascade(row)
        QTest.keyClicks(self.w.menu, 'appdata')
        self.assertEqual(self.w.menu.filter_edit.text(), 'appdata')
        self.assertEqual(self.w.search.text(), '')
        self.assertTrue(self.w.menu.isVisible())

    def test_function_page_keys(self):
        ctrl = Qt.KeyboardModifier.ControlModifier
        QTest.keyClick(self.w.search, Qt.Key.Key_F2, ctrl)
        self.assertEqual(self.w.tabs.currentIndex(), 1)
        QTest.keyClick(self.w.list, Qt.Key.Key_F3, ctrl)
        self.assertEqual(self.w.tabs.currentIndex(), 2)
        QTest.keyClick(self.w.search, Qt.Key.Key_F1, ctrl)
        self.assertEqual(self.w.tabs.currentIndex(), 0)
        self.w.cascade(self.w.children()[0])
        menu = self.w.menu
        QTest.keyClick(menu, Qt.Key.Key_F2, ctrl)
        self.assertFalse(menu.isVisible())
        self.assertEqual(self.w.tabs.currentIndex(), 1)
        QTest.keyClick(self.w.search, Qt.Key.Key_F11, ctrl)
        self.assertEqual(self.w.tabs.currentIndex(), 1)
        self.w.search.setText('test')
        QTest.keyClick(self.w.search, Qt.Key.Key_F1, ctrl)
        self.assertEqual(self.w.search.text(), '')
        # Bare F2/F5 must not alter Page; F12 is selection confirm.
        QTest.keyClick(self.w.search, Qt.Key.Key_F2)
        QTest.keyClick(self.w.search, Qt.Key.Key_F5)
        self.assertEqual(self.w.tabs.currentIndex(), 0)
        row = next(x for x in self.w.data['items'] if x['item_kind'] == 'selection')
        self.w.activate(row)
        sent = []
        self.w.confirm_selection = lambda: sent.append(True)
        QTest.keyClick(self.w.list, Qt.Key.Key_F12)
        self.assertEqual(sent, [True])

    def test_main_list_right_executes_leaf(self):
        row = next(x for x in self.w.data['items'] if x['page_id']=='work' and x['item_kind'] not in {'category','directory'})
        self.w.search.setText(row['title'])
        current = self.w.list.currentItem()
        self.assertIsNotNone(current)
        sent=[]
        self.w.execute=lambda item,*args:sent.append(item)
        QTest.keyClick(self.w.search, Qt.Key.Key_Right)
        self.assertEqual(sent[0]['item_id'], row['item_id'])

    def test_selection_right_toggles_recipients_and_keeps_f12(self):
        row = next(x for x in self.w.data['items'] if x['item_kind']=='selection')
        self.w.activate(row)
        self.assertIs(self.w.selection,row)
        first = self.w.list.currentItem()
        first_id = first.data(0,Qt.ItemDataRole.UserRole)['choice_id']
        self.w.list.setFocus()
        QTest.keyClick(self.w.list, Qt.Key.Key_Right)
        self.assertIn(first_id,self.w.checked)
        self.assertEqual(first.checkState(0),Qt.CheckState.Checked)
        QTest.keyClick(self.w.list, Qt.Key.Key_Down)
        second = self.w.list.currentItem()
        second_id = second.data(0,Qt.ItemDataRole.UserRole)['choice_id']
        self.assertNotEqual(first_id,second_id)
        QTest.keyClick(self.w.list, Qt.Key.Key_Right)
        self.assertEqual(self.w.checked,{first_id,second_id})
        QTest.keyClick(self.w.list, Qt.Key.Key_Up)
        QTest.keyClick(self.w.list, Qt.Key.Key_Right)
        self.assertEqual(self.w.checked,{second_id})
        sent = []
        self.w.execute=lambda item,values=None:sent.append((item,values))
        QTest.keyClick(self.w.list, Qt.Key.Key_F12)
        self.assertEqual(len(sent),1)
        self.assertEqual(sent[0][0]['item_id'],row['item_id'])
        selected = next(c for c in self.w.data['launch_choices'] if c['choice_id']==second_id)
        self.assertEqual(sent[0][1][row.get('launch_selection_result_name','recipients')],
                         selected.get(row.get('launch_selection_value_field','value'),''))

    def test_selection_right_from_search_preserves_text_caret(self):
        row=next(x for x in self.w.data['items'] if x['item_kind']=='selection')
        self.w.activate(row)
        self.w.search.setText('田中')
        self.w.search.setFocus()
        self.w.search.setCursorPosition(0)
        QTest.keyClick(self.w.search,Qt.Key.Key_Right)
        self.assertEqual(self.w.search.cursorPosition(),1)
        self.assertEqual(self.w.checked,set())
        self.w.list.setFocus()
        QTest.keyClick(self.w.list,Qt.Key.Key_Right)
        self.assertEqual(len(self.w.checked),1)

    def test_selection_all_clear_and_back(self):
        row = next(x for x in self.w.data['items'] if x['item_kind']=='selection')
        self.w.activate(row)
        self.w.search.setText('nonmatching')
        QTest.keyClick(self.w.search, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        expected = {c['choice_id'] for c in self.w.data['launch_choices'] if c.get('enabled',True) and c['group_id']==row['launch_selection_group_id']}
        self.assertEqual(self.w.checked, expected)
        QTest.keyClick(self.w.list, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(self.w.checked, set())
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        self.assertIsNone(self.w.selection)
        self.assertFalse(self.w.selection_tools.isVisible())

if __name__=='__main__': unittest.main()
