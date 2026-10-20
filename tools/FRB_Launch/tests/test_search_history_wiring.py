"""Static integration contract checks when PySide6 is not installed."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src/app.py').read_text(encoding='utf8')
TREE = ast.parse(SOURCE)
LAUNCHER = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
FUNCS = {x.name: x for x in LAUNCHER.body if isinstance(x, ast.FunctionDef)}


def body(name):
    return ast.get_source_segment(SOURCE, FUNCS[name])


class HistoryWiringTests(unittest.TestCase):
    def test_popup_before_normal_keyboard_activation(self):
        handler = body('eventFilter')
        self.assertLess(handler.index('self.handle_history_event(obj, event)'),
                        handler.index('if k in (Qt.Key.Key_Return,Qt.Key.Key_Enter):'))

    def test_search_uses_new_text_changed_handler(self):
        self.assertIn('self.search.textChanged.connect(self.search_text_changed)', SOURCE)
        self.assertIn('self.history_choices.installEventFilter(self)', SOURCE)
        self.assertIn('self.history_choices.viewport().installEventFilter(self)', SOURCE)
        self.assertIn('self.history_choices.itemClicked.connect(self.history_row_clicked)', SOURCE)

    def test_keyboard_confirm_sets_search_before_list_focus(self):
        handler = body('select_history_keyword')
        self.assertLess(handler.index('self.search.setText(keyword)'), handler.index('self.list.setFocus('))
        self.assertNotIn('self.activate(', handler)
        self.assertNotIn('self.execute(', handler)

    def test_only_button_registers_search_history(self):
        self.assertIn('self.save_history_button.clicked.connect(', SOURCE)
        self.assertIn('self.remember_search()', SOURCE)
        self.assertIn("setVisible(bool(value.strip()))", body('search_text_changed'))
        for name in ('dismiss', 'activate', 'confirm_selection', 'search_text_changed'):
            self.assertNotIn('self.remember_search(', body(name))

    def test_slash_removal_and_reserved_hotkey(self):
        self.assertIn("value.replace('/', '')", body('search_text_changed'))
        self.assertIn("event.text() == '/'", body('handle_history_event'))
        for key in ('Key_Right', 'Key_Tab', 'Key_Return', 'Key_Enter', 'Key_Escape',
                    'Key_Up', 'Key_Down'):
            self.assertIn(key, body('handle_history_event'))


if __name__ == '__main__':
    unittest.main()
