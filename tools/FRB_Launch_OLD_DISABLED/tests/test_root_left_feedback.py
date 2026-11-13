"""Boundary-balloon regressions; run GUI cases with QT_QPA_PLATFORM=offscreen."""
import ast
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
LAUNCHER = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
METHODS = {n.name: n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef)}


class TestRootLeftPredicateWithoutQt(unittest.TestCase):
    """Exercise the real source method using small Qt-free fake objects."""

    @classmethod
    def setUpClass(cls):
        method = METHODS['at_root_first_row']
        ns = {}
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), ns)
        cls.predicate = staticmethod(ns['at_root_first_row'])

    def make(self, root, count, current_index):
        rows = [object() for _ in range(count)]
        selection = rows[current_index] if current_index is not None else None
        view = SimpleNamespace(topLevelItemCount=lambda: len(rows),
                               currentItem=lambda: selection,
                               topLevelItem=lambda n: rows[n])
        return SimpleNamespace(in_root_page_navigation=lambda: root, list=view)

    def test_root_first_row_only(self):
        self.assertTrue(self.predicate(self.make(True, 3, 0)))
        self.assertFalse(self.predicate(self.make(True, 3, 1)))
        self.assertFalse(self.predicate(self.make(True, 0, None)))
        self.assertFalse(self.predicate(self.make(True, 3, None)))
        self.assertFalse(self.predicate(self.make(False, 3, 0)))

    def test_left_key_route_does_not_override_tabs(self):
        event_filter = ast.get_source_segment(SOURCE.read_text(encoding='utf-8'), METHODS['eventFilter'])
        self.assertIn('obj is self.list', event_filter)
        self.assertIn('self.at_root_first_row()', event_filter)
        self.assertIn('self.show_root_left_feedback()', event_filter)
        self.assertIn('self.go_back();return True', event_filter)
        self.assertLess(event_filter.index('if obj==self.tabs:'),
                        event_filter.index('self.show_root_left_feedback()'))
        self.assertLess(event_filter.index('self.show_root_left_feedback()'),
                        event_filter.index('self.go_back();return True'))

    def test_balloon_is_silent_non_focus_stealing_and_timed(self):
        text = ast.get_source_segment(SOURCE.read_text(encoding='utf-8'), METHODS['show_root_left_feedback'])
        self.assertIn('🎺 ぱふぅ〜！！', text)
        self.assertIn('Qt.FocusPolicy.NoFocus', text)
        self.assertIn('WA_TransparentForMouseEvents', text)
        self.assertIn('self._root_left_feedback_timer.start(800)', text)
        self.assertNotIn('playSound', text)
        self.assertNotIn('showMessage(', text)


try:
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    sys.path.insert(0, str(SOURCE.parent))
    import app as module
    HAS_QT = True
except ImportError:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, 'PySide6 not available in this environment')
class TestRootLeftFeedbackWithQt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)
        import tempfile
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_state = module.STATE
        cls.old_hotkey, cls.old_unhotkey = module.windows.hotkey, module.windows.unhotkey
        module.STATE = Path(cls.temp.name)
        module.windows.hotkey = lambda *args: None
        module.windows.unhotkey = lambda *args: None

    @classmethod
    def tearDownClass(cls):
        module.STATE = cls.old_state
        module.windows.hotkey, module.windows.unhotkey = cls.old_hotkey, cls.old_unhotkey
        cls.temp.cleanup()

    def setUp(self):
        self.w = module.Launcher()
        self.w.show()
        self.w.search.clear()
        self.w.stack = []
        self.w.selection = None
        self.w.render()
        self.assertGreater(self.w.list.topLevelItemCount(), 0)
        self.w.list.setCurrentItem(self.w.list.topLevelItem(0))
        self.w.list.setFocus()
        self.qt.processEvents()

    def tearDown(self):
        self.w.dismiss()
        self.w.tray.hide()
        self.w.deleteLater()
        self.qt.processEvents()

    def test_left_at_root_shows_and_expires_without_changing_focus(self):
        original_row = self.w.list.currentItem()
        original_page = self.w.tabs.currentIndex()
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        bubble = self.w._root_left_feedback
        self.assertTrue(bubble.isVisible())
        self.assertEqual(bubble.text(), '🎺 ぱふぅ〜！！')
        self.assertIs(self.w.list.currentItem(), original_row)
        self.assertEqual(self.w.tabs.currentIndex(), original_page)
        self.assertTrue(self.w.list.hasFocus())
        QTest.qWait(880)
        self.assertFalse(bubble.isVisible())

    def test_repeated_left_restarts_the_timeout(self):
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        QTest.qWait(400)
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        QTest.qWait(450)
        self.assertTrue(self.w._root_left_feedback.isVisible())
        QTest.qWait(440)
        self.assertFalse(self.w._root_left_feedback.isVisible())

    def test_page_tab_left_still_changes_page_without_balloon(self):
        self.w.tabs.setCurrentIndex(min(1, self.w.tabs.count() - 1))
        self.w.tabs.setFocus()
        QTest.keyClick(self.w.tabs, Qt.Key.Key_Left)
        self.assertEqual(self.w.tabs.currentIndex(), 0)
        self.assertFalse(hasattr(self.w, '_root_left_feedback'))
        self.assertTrue(self.w.tabs.hasFocus())

    def test_submenu_back_does_not_show_balloon(self):
        self.w.stack = [self.w.children()[0]]
        self.w.render()
        self.w.list.setFocus()
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        self.assertEqual(self.w.stack, [])
        self.assertFalse(hasattr(self.w, '_root_left_feedback'))

    def test_search_does_not_trigger_balloon(self):
        self.w.search.setText('frb')
        self.w.list.setFocus()
        QTest.keyClick(self.w.list, Qt.Key.Key_Left)
        self.assertFalse(hasattr(self.w, '_root_left_feedback'))


if __name__ == '__main__':
    unittest.main()
