"""Regression guards for the paired search and breadcrumb combo controls.

The GUI-specific hit target and high-DPI rendering still need Windows testing.
"""
import ast
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
APP = (PROJECT/'src/app.py').read_text('utf-8')
VIEW = (PROJECT/'src/expanded_view.py').read_text('utf-8')
CHEVRON = (PROJECT/'src/combo_chevron_icon.py').read_text('utf-8')


def test_the_source_is_valid_python_and_the_shared_icon_is_imported():
    for script in (APP, VIEW, CHEVRON):
        ast.parse(script)
    assert 'from combo_chevron_icon import combo_chevron_icon' in APP
    assert 'from combo_chevron_icon import combo_chevron_icon' in VIEW
    assert 'self.history_action.setIcon(combo_chevron_icon(self.color_theme, offset_x=-1))' in APP
    assert 'self.favorite_dropdown.setIcon(combo_chevron_icon(theme))' in VIEW


def test_magnifier_is_offset_left_and_down_from_original():
    assert 'self.search_glyph.move(11,' in APP
    assert '(height - self.search_glyph.height()) // 2 + 2' in APP


def test_the_search_combo_is_nudged_left_inside_its_image():
    assert 'painter.drawLine(QPointF(1 + offset_x, 5), QPointF(5 + offset_x, 9))' in CHEVRON
    assert 'painter.drawLine(QPointF(5 + offset_x, 9), QPointF(9 + offset_x, 5))' in CHEVRON


def test_favorites_combo_is_overlay_inside_breadcrumb_not_an_external_sibling():
    assert 'self.favorite_dropdown = QToolButton(self.address_bar)' in VIEW
    assert 'self.address_bar.attach_history_dropdown(self.favorite_dropdown)' in VIEW
    assert 'shared_layout.addWidget(self.favorite_dropdown)' not in VIEW
    assert 'self.crumb_layout.setContentsMargins(4, 1, 64, 1)' in VIEW
    assert 'self.editor.setTextMargins(0, 0, 60, 0)' in VIEW
    assert 'combo.move(max(0, self.width() - combo.width() - 4)' in VIEW
    assert 'self._position_dropdown()' in VIEW


def test_favorites_navigation_and_popup_reorder_are_preserved():
    assert 'self.favorite_dropdown.clicked.connect(self.toggle_directory_favorites)' in VIEW
    assert 'self.favorite_choices.orderChanged.connect(self.directory_favorites_reordered)' in VIEW
    assert 'if not self.go_to_directory(path):' in VIEW
    assert "self.favorite_save.setText('🩶' if registered else '💛')" in VIEW
