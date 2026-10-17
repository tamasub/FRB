"""Regression: all Launcher scrollable views share the same themed scrollbars.

The pure style contract runs without Qt.  The optional widget test uses Qt's
'offscreen' platform and checks the actual child QScrollBar style sheets.
"""
import ast
import os
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1] / 'app.py'
SOURCE = APP.read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def _style_api():
    assignments = [node for node in TREE.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'MAIN_LIST_SCROLLBAR_QSS'
                           for t in node.targets)]
    functions = [node for node in TREE.body if isinstance(node, ast.FunctionDef)
                 and node.name in ('scrollbar_qss', 'apply_scrollbar_theme')]
    scope = {}
    exec(compile(ast.Module(body=[*assignments, *functions], type_ignores=[]), str(APP), 'exec'), scope)
    return scope


class FakeBar:
    def __init__(self):
        self.style = None

    def setStyleSheet(self, value):
        self.style = value


class FakeView:
    def __init__(self):
        self.v = FakeBar()
        self.h = FakeBar()

    def verticalScrollBar(self):
        return self.v

    def horizontalScrollBar(self):
        return self.h


class UnifiedScrollbarTests(unittest.TestCase):
    def test_all_surfaces_and_both_axes_explicitly_styled(self):
        scope = _style_api()
        for bg in ('#202b29', '#223043', '#202b39'):
            with self.subTest(background=bg):
                v = FakeView()
                scope['apply_scrollbar_theme'](v, bg)
                self.assertEqual(v.v.style, v.h.style)
                for rule in ('QScrollBar:vertical', 'QScrollBar:horizontal',
                             'QScrollBar::handle:vertical', 'QScrollBar::handle:horizontal',
                             'QScrollBar::add-line:vertical', 'QScrollBar::sub-line:horizontal',
                             'QScrollBar::up-arrow:vertical', 'QScrollBar::right-arrow:horizontal'):
                    self.assertIn(rule, v.v.style)
                self.assertIn(f'background:{bg}', v.v.style)
                self.assertIn('width:8px', v.v.style)
                self.assertIn('height:8px', v.v.style)

    def test_history_explicitly_themed_after_widget_constructed(self):
        creation = SOURCE.index('self.history_choices = QTreeWidget(self.history_popup)')
        styling = SOURCE.index("apply_scrollbar_theme(self.history_choices, '#223043')")
        self.assertLess(creation, styling)
        self.assertIn('self.history_choices.setVerticalScrollMode(', SOURCE)

    def test_popup_and_app_catalog_covered(self):
        self.assertIn("apply_scrollbar_theme(tree, '#202b39')", SOURCE)
        self.assertIn('apply_scrollbar_theme(self.tree)', SOURCE)
        self.assertNotIn('width:9px', SOURCE)  # no alternate legacy scrollbar width

    def test_search_list_both_axes_still_themed(self):
        self.assertIn('self.list.verticalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)', SOURCE)
        self.assertIn('self.list.horizontalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)', SOURCE)

    def test_application_fallback_for_new_widgets(self):
        self.assertIn('app.setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)', SOURCE)

    def test_no_scrollbar_interaction_logic_changed(self):
        self.assertIn('self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded if query else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)', SOURCE)
        self.assertIn('self.history_choices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)', SOURCE)


try:
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication, QTreeWidget
except ImportError:
    QApplication = None


@unittest.skipIf(QApplication is None, 'PySide6 unavailable in this environment')
class QtScrollbarSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_explicit_theme_on_real_tree_scrollbars(self):
        style = _style_api()['apply_scrollbar_theme']
        for bg in ('#202b29', '#223043', '#202b39'):
            tree = QTreeWidget()
            style(tree, bg)
            for bar in (tree.verticalScrollBar(), tree.horizontalScrollBar()):
                self.assertIn(bg, bar.styleSheet())
                self.assertIn('QScrollBar::handle:vertical', bar.styleSheet())
            tree.deleteLater()


if __name__ == '__main__':
    unittest.main()
