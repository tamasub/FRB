"""Contract checks for appearance toggle; no Qt needed on CI."""
from pathlib import Path
import unittest

from launch_appearance import (normalize_theme, LIGHT_MAIN_QSS, LIGHT_TABS_QSS,
    LIGHT_MENU_QSS, LIGHT_HISTORY_QSS, LIGHT_CASCADE_TREE_QSS,
    LIGHT_COLUMN_FILTER_QSS, FRAME_COLORS, light_scrollbar_qss)

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


class LaunchAppearanceTests(unittest.TestCase):
    def test_dark_is_original_default_and_invalid_values_fallback_safely(self):
        for raw in (None, 'unknown', 'Dark', '', 123):
            self.assertEqual(normalize_theme(raw), 'dark')
        self.assertEqual(normalize_theme(' LIGHT '), 'light')
        self.assertIn("self.settings.value('appearance_theme', 'dark')", APP)

    def test_search_history_arrow_remains_inside_input_and_menu_is_adjacent(self):
        self.assertIn('self.search.addAction(QIcon(chevron), QLineEdit.ActionPosition.TrailingPosition)', APP)
        self.assertIn('search_row.addWidget(self.search, 1)', APP)
        self.assertIn('search_row.addWidget(self.theme_button)', APP)
        self.assertIn('mode_row.addWidget(self.tabs, 1)', APP)
        self.assertIn('for w in (self.search_bar, self.mode_bar, self.selection_tools, self.list,', APP)
        self.assertIn("self.theme_button = QPushButton('⋯'", APP)
        self.assertIn("self.light_theme_action = self.theme_menu.addAction('ライトモード')", APP)
        self.assertIn("self.dark_theme_action = self.theme_menu.addAction('ダークモード')", APP)

    def test_compact_geometry_and_presentation_are_independent(self):
        self.assertIn('self.theme_button.setFixedSize(34, 32)', APP)
        self.assertIn('self.search.mapTo(self, QPoint(0, self.search.height() + 4))', APP)
        self.assertIn("self.settings.setValue('appearance_theme', resolved)", APP)
        self.assertIn('self.apply_color_theme()', APP)
        self.assertIn('self.tabs.setStyleSheet(LIGHT_TABS_QSS if light else PAGE_TABS_QSS)', APP)
        self.assertIn('self.history_popup.setStyleSheet(LIGHT_HISTORY_QSS if light else self._dark_history_qss)', APP)
        self.assertIn('self.list.topLevelItem(index).setForeground(', APP)
        self.assertNotIn('CONFIG.write_text', APP)

    def test_light_palette_covers_popups_scrollbars_and_frame(self):
        for qss in (LIGHT_MAIN_QSS, LIGHT_TABS_QSS, LIGHT_MENU_QSS,
                    LIGHT_HISTORY_QSS, LIGHT_CASCADE_TREE_QSS,
                    LIGHT_COLUMN_FILTER_QSS):
            self.assertIn('#', qss)
            self.assertNotIn('#202b29', qss)
        self.assertIn('light', FRAME_COLORS)
        self.assertIn('dark', FRAME_COLORS)
        style = light_scrollbar_qss('#ffffff')
        for key in ('QScrollBar:vertical', 'QScrollBar:horizontal',
                    'QScrollBar::handle:vertical', 'QScrollBar::handle:horizontal'):
            self.assertIn(key, style)
        self.assertIn('width:8px', style)
        self.assertIn('height:8px', style)

    def test_studio_theme_hint_still_independent(self):
        self.assertIn('studio_launch_arguments(program, step.get(\'launch_arguments\',[]))', APP)
        self.assertIn('self.search.textChanged.connect(self.search_text_changed)', APP)
        self.assertIn('self.tabs.currentChanged.connect(self.page_changed)', APP)


if __name__ == '__main__':
    unittest.main()
