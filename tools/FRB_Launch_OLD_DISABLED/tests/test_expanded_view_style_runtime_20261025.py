"""Prevent the launch-breaking QSS f-string NameError from returning.

These tests evaluate each real expanded-view stylesheet f-string without Qt:
py_compile alone is insufficient because {background:...} parses but throws
NameError only when apply_theme() runs on startup.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def test_apply_theme_stylesheets_evaluate_at_runtime_without_nameerror():
    module = ast.parse(VIEW)
    owner = next(n for n in module.body
                 if isinstance(n, ast.ClassDef) and n.name == 'ExpandedLauncherView')
    method = next(n for n in owner.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'apply_theme')
    css_calls = [n for n in ast.walk(method)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == 'setStyleSheet' and n.args and
                 isinstance(n.args[0], ast.JoinedStr)]
    assert len(css_calls) >= 2
    for scheme in ('light', 'dark'):
        values = dict(
            bg='#fcfffd' if scheme == 'light' else '#222e2c',
            border='#bbd8c7', root_border='#bbd8c7' if scheme == 'light' else '#698779',
            hdr='#eaf6ec', text='#233e32',
            hover='#ecf7f1', active='#d7ece1', stripe='#e7f3ed',
            height=29, pad=3)
        sheets = []
        for call in css_calls:
            expr = ast.Expression(body=call.args[0])
            css = eval(compile(expr, '<real expanded-view stylesheet>', 'eval'), {}, values)
            assert css.count('{') == css.count('}')  # CSS braces are well formed
            sheets.append(css)
        assert any('QTreeWidget#expandedTree::item:selected:!active '
                   '{background:transparent;' in css for css in sheets)


def test_inactive_pane_current_row_is_outlined_not_filled():
    assert 'row_option = QStyleOptionViewItem(option)' in VIEW
    assert 'QStyleOptionViewItem, QStyle)' in VIEW
    assert 'QTimer, QEvent, QRectF' in VIEW
    assert 'row_option.state &= ~QStyle.StateFlag.State_Selected' in VIEW
    assert 'self._column_is_focused()' in VIEW
    assert 'self.indexOfTopLevelItem(current) == index.row()' in VIEW
    assert 'painter.drawRoundedRect(rect, 6.5, 6.5)' in VIEW
    assert 'self.viewport().update()' in VIEW


def test_mode_toggle_has_vector_icons_and_current_label():
    assert "def view_mode_icon(mode, theme='light'):" in APP
    assert 'pix.setDevicePixelRatio(scale)' in APP
    assert "self.mode_button.setIconSize(QSize(22, 22))" in APP
    assert "self.mode_button.setText('Compact' if showing_classic else 'Three-layer')" in APP
    assert "self.mode_button.setIcon(view_mode_icon('classic' if showing_classic else 'expanded'," in APP
    assert 'self.mode_button.setIcon(view_mode_icon(' in APP


def test_density_three_strokes_have_requested_optical_offset():
    assert 'for y in (10, 16, 22):' in VIEW
    assert 'painter.drawLine(7, y, 23, y)' in VIEW
