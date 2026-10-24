"""Static regression checks for the inline search pill and header assets.

No PySide6 needed: validates the wiring even on CI hosts without Qt.
"""
from pathlib import Path
import ast
import unittest

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(APP)
LAUNCHER = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
FUNCS = {n.name: n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef)}


def method(name):
    return ast.get_source_segment(APP, FUNCS[name])


class ModernHeaderControlsTests(unittest.TestCase):
    def test_history_register_is_inside_search(self):
        self.assertIn("QPushButton('履歴登録', self.search)", APP)
        self.assertNotIn('search_row.addWidget(self.save_history_button', APP)
        self.assertIn('self.layout_search_inner_controls()', method('search_text_changed'))
        self.assertIn('right_space = 71', method('layout_search_inner_controls'))
        self.assertIn('self.search.setTextMargins(', method('layout_search_inner_controls'))

    def test_search_glyph_is_not_forced_to_native_16dp(self):
        self.assertIn('self.search_glyph = QToolButton(self.search)', APP)
        self.assertIn('self.search_glyph.setIconSize(QSize(28, 28))', APP)
        self.assertNotIn("self.search.addAction(toolbar_outline_icon('search'", APP)
        self.assertIn('self.search_glyph.move(13,', method('layout_search_inner_controls'))

    def test_header_repaint_and_resize_wiring(self):
        self.assertIn("QWidget#brandWidget { background:transparent", method('apply_color_theme'))
        self.assertIn("QLabel#brandIconLabel { background:transparent", method('apply_color_theme'))
        self.assertIn("subheader_fill = '#f8fcfa'", method('apply_color_theme'))
        self.assertIn('event.type() == QEvent.Type.Resize', method('eventFilter'))
        self.assertIn('self.layout_search_inner_controls()', method('eventFilter'))

    def test_setting_glyph_draws_a_closed_gear(self):
        function = next(n for n in TREE.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'toolbar_outline_icon')
        code = ast.get_source_segment(APP, function)
        self.assertIn('outline.closeSubpath()', code)
        self.assertIn('for tooth in range(8)', code)
        self.assertIn("if name == 'search'", code)
        self.assertIn('QPointF(20.2, 20.0)', code)


if __name__ == '__main__':
    unittest.main()
