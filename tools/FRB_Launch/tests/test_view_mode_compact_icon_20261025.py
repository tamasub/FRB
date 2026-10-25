"""Protect the tiny view-toggle icon against accidental enlargement/misalignment."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def _view_icon():
    mod = ast.parse(APP)
    return next(n for n in mod.body if isinstance(n, ast.FunctionDef)
                and n.name == 'view_mode_icon')


def test_toggle_size_is_same_as_files_density_button():
    assert 'self.mode_button.setIconSize(QSize(22, 22))' in APP
    assert 'self.density_button.setIconSize(QSize(22, 22))' in VIEW
    assert "side, scale = 28, 2" in APP
    assert 'QPixmap(side * scale, side * scale)' in APP
    assert 'self.mode_button.setText(\'Compact\' if showing_classic else \'Three-layer\')' in APP
    assert "self.mode_button = QPushButton('Three-layer', self.mode_bar)" in APP


def test_compact_is_four_identical_centered_lines():
    node = _view_icon()
    block = next(n for n in ast.walk(node)
                 if isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)
                 and len(n.iter.elts) == 4)
    assert [n.value for n in block.iter.elts] == [6.5, 11.5, 16.5, 21.5]
    line = next(n for n in ast.walk(block)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == 'drawLine')
    assert ast.unparse(line) == 'painter.drawLine(QPointF(7, y), QPointF(23, y))'
    assert '2.0' in ast.get_source_segment(APP, node)


def test_three_layer_drawing_keeps_same_outer_span():
    source = ast.get_source_segment(APP, _view_icon())
    assert 'for y in (9, 14, 19):' in source
    assert 'painter.drawLine(QPointF(7, y), QPointF(13, y))' in source
    assert 'painter.drawLine(QPointF(17, y), QPointF(23, y))' in source


def test_toggle_stays_compact_not_38px_wide_glyph():
    assert 'QSize(38, 24)' not in APP
    assert 'padding:5px 8px;' in APP
