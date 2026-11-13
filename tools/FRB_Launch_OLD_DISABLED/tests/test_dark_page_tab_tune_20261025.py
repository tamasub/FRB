"""Regression for the 2026-10-25 dark second-row Page tab polish."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_QSS = (ROOT / 'src/page_tab_theme.py').read_text(encoding='utf-8')
FOCUS = (ROOT / 'src/page_tab_focus.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def _state_qss(state):
    # Extract literal CSS block from the triple quoted PAGE_TABS_QSS.
    m = re.search(r'QTabBar::tab' + re.escape(state) + r'\s*\{([^}]*)\}', PAGE_QSS)
    assert m, state
    return dict(re.findall(r'(background|border|border-bottom|border-color|border-bottom-color|color):\s*([^;]+);', m.group(1)))


def _rgb(hexcolor):
    return tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))


def test_idle_background_is_just_below_hover():
    base = _state_qss('')['background']
    hovered = _state_qss(':hover:!selected')['background']
    assert base == '#304340'
    assert hovered == '#344746'
    assert all(0 <= b-a <= 8 for a, b in zip(_rgb(base), _rgb(hovered)))


def test_idle_border_is_visible_but_still_changes_slightly_on_hover():
    base = _state_qss('')['border'].split()[-1]
    hovered = _state_qss(':hover:!selected')['border-color']
    assert base == '#42595b'
    assert hovered == '#465e61'
    assert all(0 <= b-a <= 8 for a, b in zip(_rgb(base), _rgb(hovered)))
    assert _state_qss('')['border-bottom'].endswith('#42595b')


def test_selected_gradient_and_bottom_marker_are_preserved():
    selected = _state_qss(':selected')
    assert 'qlineargradient(' in selected['background']
    assert selected['border-bottom'] == '2px solid #8ab9ff'


def test_dark_focus_ring_is_thinner_but_light_keeps_original_weight():
    assert "focus_width = 1.8 if getattr(self, '_light_theme', False) else 0.75" in FOCUS
    assert "'#82958c' if getattr(self, '_light_theme', False) else '#d2e6ff'" in FOCUS
    assert 'painter.drawRoundedRect(inner, 4, 4)' in FOCUS


def test_app_still_applies_both_styles_through_original_focus_tabbar():
    assert 'self.tabs.setStyleSheet(LIGHT_TABS_QSS if light else PAGE_TABS_QSS)' in APP
    assert 'self.tabs.set_light_theme(light)' in APP
