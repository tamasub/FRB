"""Dark-theme polish: visual contracts without GUI dependencies."""
from pathlib import Path
import ast

from launch_appearance import history_popup_qss, theme_palette

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
EXPANDED = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def test_dark_secondary_layer_has_contrast_border_without_changing_selection():
    old = theme_palette('dark')['panel_border']
    new = theme_palette('dark')['root_button_border']
    assert old != new
    assert theme_palette('light')['root_button_border'] == theme_palette('light')['panel_border']
    assert 'border:1px solid {root_border};' in EXPANDED
    assert "root_border = colors['root_button_border']" in EXPANDED
    assert 'QPushButton#expandedRootButton:checked {{background:{active};border:1px solid #81bca4;font-weight:600;}}' in EXPANDED
    assert 'QPushButton#expandedRootButton:focus {{border:2px solid #56a88c;background:{active};}}' in EXPANDED


def test_main_search_history_and_folder_favorites_share_all_palette_roles():
    for theme in ('light', 'dark'):
        colors = theme_palette(theme)
        main = history_popup_qss(theme)
        favorites = history_popup_qss(
            theme, frame_name='expandedFavoritesPopup',
            tree_name='expandedFavoritesChoices', height=30, padding=5)
        for role in ('history_bg', 'history_border', 'history_text',
                     'history_selected', 'history_selected_text', 'history_hover'):
            assert colors[role] in main, (theme, role)
            assert colors[role] in favorites, (theme, role)
        assert '#223043' in favorites if theme == 'dark' else '#ffffff' in favorites
    assert "self._dark_history_qss = history_popup_qss('dark')" in APP
    assert 'self.favorite_popup.setStyleSheet(history_popup_qss(' in EXPANDED
    assert "scrollbar_for_theme(theme, colors['history_bg'])" in EXPANDED


def test_studio_menu_caption_only_changed_not_action():
    assert "self.theme_menu.addAction('メニュー設定 (FRB Studio)')" in APP
    tree = ast.parse(APP)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    init = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    init_source = ast.get_source_segment(APP, init)
    assert 'self.theme_studio_action.triggered.connect(' in init_source
    assert 'self.launch_configuration_studio(page_properties=True)' in init_source
