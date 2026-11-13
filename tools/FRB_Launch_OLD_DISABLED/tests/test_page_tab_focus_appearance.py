"""Static regression for the visible Page-tab focus outline in both themes."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'src'

class PageTabFocusAppearanceTests(unittest.TestCase):
    def test_light_theme_has_gray_keyboard_focus_ring(self):
        src = (ROOT / 'page_tab_focus.py').read_text(encoding='utf-8')
        self.assertIn('def set_light_theme(self, light):', src)
        self.assertIn("'#82958c' if getattr(self, '_light_theme', False) else '#d2e6ff'", src)
        self.assertIn('not self.hasFocus()', src)
        self.assertIn('self.tabRect(index)', src)

    def test_theme_updates_existing_page_bar_without_recreating_it(self):
        src = (ROOT / 'app.py').read_text(encoding='utf-8')
        self.assertIn('self.tabs.set_light_theme(light)', src)
        self.assertIn('self.tabs.setStyleSheet(LIGHT_TABS_QSS if light else PAGE_TABS_QSS)', src)

if __name__ == '__main__':
    unittest.main()
