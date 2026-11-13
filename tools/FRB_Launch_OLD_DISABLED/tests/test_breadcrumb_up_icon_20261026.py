"""Regression tests: breadcrumb upward corner arrow and original back arrow."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src' / 'browser_nav_icons.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def _shape_commands(icon_name):
    tree = ast.parse(SOURCE)
    draw = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == '_draw_icon')
    branch = next(node for node in ast.walk(draw)
                  if isinstance(node, ast.If)
                  and isinstance(node.test, ast.Compare)
                  and isinstance(node.test.left, ast.Name)
                  and node.test.left.id == 'name'
                  and len(node.test.comparators) == 1
                  and isinstance(node.test.comparators[0], ast.Constant)
                  and node.test.comparators[0].value == icon_name)
    return [(line.value.func.attr,
             tuple(ast.literal_eval(arg) for arg in line.value.args))
            for line in branch.body if isinstance(line, ast.Expr)
            and isinstance(line.value, ast.Call)
            and isinstance(line.value.func, ast.Attribute)
            and line.value.func.value.id == 'shape']


def test_breadcrumb_up_icon_only_has_arrowhead_and_turning_shaft():
    assert _shape_commands('back') == [
        ('moveTo', (4.5, 10.0)),
        ('lineTo', (11.5, 4.5)),
        ('lineTo', (18.5, 10.0)),
        ('moveTo', (11.5, 4.5)),
        ('lineTo', (11.5, 19.0)),
        ('lineTo', (20.0, 19.0)),
    ]


def test_old_left_arrow_drawing_preserved_without_modifications():
    assert _shape_commands('back_arrow') == [
        ('moveTo', (20, 12)),
        ('lineTo', (4.5, 12)),
        ('moveTo', (11, 5.5)),
        ('lineTo', (4.5, 12)),
        ('lineTo', (11, 18.5)),
    ]


def test_no_change_to_original_sizing_stroke_theme_or_action():
    assert '_ICON_SIDE = 24' in SOURCE
    assert '_ICON_SCALE = 2' in SOURCE
    assert "pen.setWidthF(1.0 if name == 'home' else 2.0)" in SOURCE
    assert "(self.nav_back_button, 'back_arrow')" in APP
    assert "pane.back.setIcon(browser_navigation_icon('back', theme_family(theme)))" in (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'self.nav_back_button.clicked.connect(self.navigate_back)' in APP
