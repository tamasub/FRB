"""Content-sized history/favorites popups (without a PySide6 dependency)."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from popup_sizing import popup_available_height, popup_tree_height


class _Size:
    def __init__(self, height):
        self._height = height
    def height(self):
        return self._height


class _Tree:
    def indexFromItem(self, item):
        return item
    def sizeHintForIndex(self, item):
        return _Size(item)


def test_popup_available_area_stops_just_above_status_bar():
    assert popup_available_height(750, 55, 718) == 659
    assert popup_available_height(750, 55) == 683
    assert popup_available_height(750, 55, 900) == 683
    assert popup_available_height(80, 90, 75) == 1


def test_history_uses_visible_rows_and_footer_limit():
    tree = _Tree()
    # Six collapsed folders: minimal popup rather than an empty 395px panel.
    assert popup_tree_height(tree, [31] * 6, 35, 48, 800) == 258
    # Expanding two folders adds three history entries, with no reordering.
    assert popup_tree_height(tree, [31] * 9, 35, 48, 800) == 363
    # Many history entries: cap at available height, not 395/600px.
    assert popup_tree_height(tree, [31] * 100, 35, 48, 659) == 659
    # Font/DPI size hints bigger than the CSS minimum take precedence.
    assert popup_tree_height(tree, [43] * 2, 35, 48, 800) == 134


def test_breadcrumb_popup_ends_just_below_last_entry():
    tree = _Tree()
    assert popup_tree_height(tree, [30], 34, 16, 600) == 50
    assert popup_tree_height(tree, [30] * 3, 34, 16, 600) == 118
    assert popup_tree_height(tree, [36] * 3, 34, 16, 100) == 100


def test_popup_integration_tracks_resize_expansion_and_content():
    app = (ROOT / 'src' / 'app.py').read_text('utf-8')
    expanded = (ROOT / 'src' / 'expanded_view.py').read_text('utf-8')
    ast.parse(app)
    ast.parse(expanded)
    assert 'self.search.setTextMargins(32, 0, 165 if is_visible else 0, 0)' in app
    assert 'height = popup_tree_height(self.history_choices, self.history_visible_rows()' in app
    assert 'height = popup_tree_height(self.favorite_choices, rows,' in expanded
    assert 'footer_top = self.footer.mapTo(self, QPoint(0, 0)).y()' in app
    assert 'footer_top = self.launcher.footer.mapTo(self.launcher, QPoint(0, 0)).y()' in expanded
    assert "if self.history_popup.isVisible():\n                self.position_history_popup()" in app
    assert "if self.favorite_popup.isVisible():\n            self.position_directory_favorites()" in expanded
    assert 'min(395' not in app
    assert 'desired_height = max(180' not in expanded
