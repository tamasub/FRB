"""v79: Remote Browser search magnifier is crisp, larger and centered.

Qt-free regression: verifies root-only rendering and layout geometry without
requiring QtWebEngine on the test host.
"""
import ast
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def _method(name):
    parsed = ast.parse(SRC)
    cls = next(node for node in parsed.body if isinstance(node, ast.ClassDef) and node.name == 'CascadeMenu')
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(SRC, method)


def test_only_bookmark_root_gets_drawn_magnifier():
    source = _method('_ensure_local_filter')
    assert "if bookmark_root:\n            # A proper magnifier" in source
    assert "else:\n            glyph = QLabel('⌕', container)" in source
    assert 'search_row.addWidget(glyph)' in source


def test_icon_is_larger_antialiased_and_centered():
    source = _method('_ensure_local_filter')
    assert 'icon_canvas = QPixmap(60, 60)' in source
    assert 'icon_canvas.setDevicePixelRatio(3)' in source
    assert 'painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)' in source
    assert 'painter.drawEllipse(QRectF(2.8, 2.8, 10.5, 10.5))' in source
    assert 'painter.drawLine(QPointF(12.2, 12.2), QPointF(17.3, 17.3))' in source
    assert 'glyph.setPixmap(icon_canvas)' in source
    assert 'glyph.setFixedSize(22, 30)' in source
    assert 'glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)' in source


def test_no_changes_to_search_alignment_and_tab_choice_layout():
    source = _method('_ensure_local_filter')
    assert 'search_row.insertWidget(1, self.filter_count)' in source
    assert 'search_row.addWidget(self.filter_edit, 1)' in source
    assert 'layout.setContentsMargins(7, 5, 7, 5)' in source
    assert 'target_row.setContentsMargins(0, 0, 0, 0)' in source
    assert 'self._select_remote_bookmark_tab(True)' in source


def test_icon_uses_palette_colors_for_both_themes():
    source = _method('_ensure_local_filter')
    assert "'#648071' if theme_family(getattr(self.launcher, 'color_theme', 'light')) == 'light' else '#9fb9d5'" in source
