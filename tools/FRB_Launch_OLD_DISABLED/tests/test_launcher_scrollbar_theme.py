"""Guard the main list scrollbar theme without needing a native Qt environment."""
import ast
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1] / 'src/app.py'


class MainListScrollbarThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.style = next(node.value.value for node in cls.tree.body
                         if isinstance(node, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == 'MAIN_LIST_SCROLLBAR_QSS'
                                 for t in node.targets))

    def test_both_axes_have_dark_thin_scrollbars(self):
        for rule in ('QScrollBar:vertical', 'QScrollBar:horizontal',
                     'QScrollBar::handle:vertical', 'QScrollBar::handle:horizontal',
                     'QScrollBar::add-line:horizontal', 'QScrollBar::sub-line:vertical',
                     'QScrollBar::add-page:horizontal', 'QScrollBar::sub-page:vertical'):
            self.assertIn(rule, self.style)
        self.assertIn('width:8px', self.style)
        self.assertIn('height:8px', self.style)
        self.assertIn('#202b29', self.style)
        self.assertIn('#929894', self.style)

    def test_styles_are_applied_to_results_list_both_scrollbars(self):
        cls = next(n for n in self.tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
        code = ast.get_source_segment(self.source, init)
        self.assertIn('self.list.verticalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)', code)
        self.assertIn('self.list.horizontalScrollBar().setStyleSheet(MAIN_LIST_SCROLLBAR_QSS)', code)
        self.assertIn('QAbstractScrollArea::corner{background:#202b29;border:0;}', code)

    def test_columns_sort_and_horizontal_scroll_policy_unchanged(self):
        cls = next(n for n in self.tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        render = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'render')
        render_source = ast.get_source_segment(self.source, render)
        self.assertIn('ScrollBarAsNeeded if query else Qt.ScrollBarPolicy.ScrollBarAlwaysOff', render_source)
        self.assertIn('self.apply_search_sort()', render_source)


if __name__ == '__main__':
    unittest.main()
