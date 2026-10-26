"""Visual regression contracts for group headings and navigation toolbar.

Qt-free checks protect the deliberate painting order and color differences.
The actual Windows/Qt painting must still be checked on a Windows machine.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_appearance import bookmark_section_colors, theme_palette

EXPANDED = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def test_heading_colors_differ_from_panel_and_selection_for_both_themes():
    for theme in ('light', 'dark'):
        section = bookmark_section_colors(theme)
        normal = theme_palette(theme)
        assert section['background'].lower() not in {
            normal['panel'].lower(), normal['selection'].lower(), normal['hover'].lower()}
        assert section['background'] != section['accent']
        assert section['divider'] != section['background']
        assert section['text'] != section['background']


def test_heading_is_drawn_after_qt_default_row_so_qss_cannot_erase_it():
    method = EXPANDED.split('    def drawRow(self, painter, option, index):', 1)[1]
    method = method.split('class _BreadcrumbSurface', 1)[0]
    assert "getattr(self.parentWidget(), 'kind', None) == 'bookmark'" in method
    assert 'item.data(0, Qt.ItemDataRole.UserRole + 1)' in method
    assert method.index('super().drawRow(painter, option, index)') < method.index(
        "QColor(palette['background'])")
    assert "QColor(palette['accent'])" in method
    assert 'painter.drawText(label_rect,' in method
    assert '                return\n        # Keep a single pale-green active column.' in method
    # Group rows are still inert/transparent to all bookmark actions.
    assert 'item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)' in EXPANDED


def test_navigation_toolbar_has_no_global_widget_fill_and_buttons_use_page_color():
    assert "self.nav_toolbar.setObjectName('navigationToolbar')" in APP
    assert 'QWidget#navigationToolbar {{ background:transparent; border:0; }}' in APP
    assert 'nav_fill = subheader_fill' in APP
    for key in ('navBackButton', 'navForwardButton', 'navHomeButton'):
        assert f'QPushButton#{key}' in APP
    assert 'button.setFixedSize(40, 40)' in APP
    assert 'button.setIcon(browser_navigation_icon(name, theme_family(self.color_theme)))' in APP
