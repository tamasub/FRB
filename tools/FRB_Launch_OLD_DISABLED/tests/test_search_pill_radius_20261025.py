"""Guard against reducing the search height without its pill radius.

Qt's stylesheet rounded border has to fit the widget's geometry.  This is
kept source-only so it also runs without PySide6 installed on CI.
"""
import re
from pathlib import Path

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def test_main_search_corner_radius_fits_36px_height_in_both_themes():
    height = int(re.search(r'self\.search\.setMinimumHeight\((\d+)\)', APP).group(1))
    max_height = int(re.search(r'self\.search\.setMaximumHeight\((\d+)\)', APP).group(1))
    assert height == max_height == 36
    radius_rules = re.findall(r"border-radius:(\d+)px; padding:5px 14px; font-size:15px;", APP)
    assert radius_rules == ['17', '17']  # light and dark QLineEdit#mainSearchField
    assert all(2 * int(radius) <= height for radius in radius_rules)


def test_main_search_control_placement_and_header_margins_unchanged():
    assert 'search_row.setContentsMargins(10, 3, 8, 3)' in APP
    assert 'self.search_glyph.move(11,' in APP
    assert 'combo_chevron_icon(self.color_theme, offset_x=-1)' in APP
