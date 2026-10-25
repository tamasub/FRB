"""Theme catalog / wiring regressions that run without Windows or PySide6."""
import ast
from pathlib import Path

from launch_appearance import (
    THEME_REGISTRY, available_themes, context_menu_spacing_qss,
    normalize_theme, theme_family, theme_palette, scrollbar_for_theme,
)

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
EXPANDED = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def method(name):
    tree = ast.parse(APP)
    launcher = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                    and node.name == 'Launcher')
    fn = next(node for node in launcher.body if isinstance(node, ast.FunctionDef)
              and node.name == name)
    return ast.get_source_segment(APP, fn)


def test_registry_normalizes_and_covers_required_roles():
    assert available_themes() == ('light', 'dark')
    assert normalize_theme(' DARK ') == 'dark'
    assert normalize_theme('light') == 'light'
    assert normalize_theme('invalid') == 'dark'
    roles = ('window', 'header', 'subheader', 'panel', 'panel_border',
             'panel_header', 'text', 'hover', 'selection', 'stripe',
             'focus_outline', 'row_separator', 'search_bg', 'search_fg',
             'root_button_border', 'history_bg', 'history_border', 'history_text',
             'history_selected', 'history_selected_text', 'history_hover')
    for name, pal in THEME_REGISTRY.items():
        assert all(pal[role].startswith('#') for role in roles), name
        assert theme_palette(name) == pal
        assert theme_family(name) in ('light', 'dark')
    assert theme_palette('light')['panel'] != theme_palette('dark')['panel']


def test_theme_catalog_automatically_drives_gear_menu():
    assert 'self.theme_button.clicked.connect(self.open_theme_menu)' in APP
    assert 'for theme_id in available_themes():' in APP
    assert 'self.theme_action_group.setExclusive(True)' in APP
    assert "self.theme_studio_action = self.theme_menu.addAction(" in APP
    assert 'self.launch_configuration_studio(page_properties=True)' in APP


def test_theme_choice_persists_without_mutating_launch_data():
    body = method('set_color_theme')
    assert 'self.settings.setValue(\'appearance_theme\', resolved)' in body
    assert 'self.settings.sync()' in body
    assert 'self.apply_color_theme()' in body
    assert 'CONFIG.write_text' not in body


def test_three_layer_uses_shared_semantic_colors_instead_of_duplicate_palette():
    assert 'colors = theme_palette(theme)' in EXPANDED
    assert "colors['row_separator']" in EXPANDED
    assert "colors['focus_outline']" in EXPANDED
    assert "colors[key] for key in ('panel', 'panel_border', 'panel_header'," in EXPANDED
    assert 'pane.tree.viewport().update()' in EXPANDED
    assert 'scrollbar_for_theme(theme, bg)' in EXPANDED
    assert "if pane.kind == 'bookmark':" in EXPANDED
    assert 'item.setIcon(0, link_icon(theme_family(theme)))' in EXPANDED


def test_compact_header_theme_and_search_pill_remain_intact():
    body = method('apply_color_theme')
    assert "header_fill = colors['header']" in body
    assert "subheader_fill = colors['subheader']" in body
    assert 'border-radius:17px' in body
    assert 'self.expanded_view.apply_theme(self.color_theme)' in body
    assert 'self.tabs.setStyleSheet(LIGHT_TABS_QSS if light else PAGE_TABS_QSS)' in body


def test_popup_and_scrollbar_contrast_in_both_themes():
    assert '#e1e5e2' in context_menu_spacing_qss('light')
    assert '#4b5b56' in context_menu_spacing_qss('dark')
    light = scrollbar_for_theme('light', '#ffffff')
    dark = scrollbar_for_theme('dark', '#222e2c')
    assert '#a5bfb0' in light
    assert '#607c71' in dark
    assert 'QScrollBar:vertical' in light and 'QScrollBar:vertical' in dark


def test_no_double_click_execution_for_theme_menu_actions():
    assert "self.theme_button.clicked.connect(self.open_theme_menu)" in APP
    assert "self.theme_studio_action.triggered.connect(" in APP
    assert 'self.set_color_theme(key)' in APP


def test_runtime_qss_expressions_evaluate_in_both_modes_without_name_errors():
    """py_compile misses errors inside live f-string evaluation (the 657 issue)."""
    app_tree = ast.parse(APP)
    launch = next(n for n in app_tree.body if isinstance(n, ast.ClassDef)
                  and n.name == 'Launcher')
    apply = next(n for n in launch.body if isinstance(n, ast.FunctionDef)
                 and n.name == 'apply_color_theme')
    search_css_call = next(
        n for n in ast.walk(apply)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == 'setStyleSheet' and isinstance(n.func.value, ast.Attribute)
        and n.func.value.attr == 'search'
    )
    view_tree = ast.parse(EXPANDED)
    expanded = next(n for n in view_tree.body if isinstance(n, ast.ClassDef)
                    and n.name == 'ExpandedLauncherView')
    theme_apply = next(n for n in expanded.body if isinstance(n, ast.FunctionDef)
                       and n.name == 'apply_theme')
    panel_css = next(
        n for n in ast.walk(theme_apply)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == 'setStyleSheet'
        and isinstance(n.func.value, ast.Name) and n.func.value.id == 'self'
    )
    for theme in available_themes():
        c = theme_palette(theme)
        search_expr = ast.Expression(search_css_call.args[0])
        panel_expr = ast.Expression(panel_css.args[0])
        search_css = eval(compile(search_expr, '<search-qss>', 'eval'),
                          {'colors': c})
        local = dict(bg=c['panel'], border=c['panel_border'],
                     root_border=c['root_button_border'],
                     hdr=c['panel_header'], text=c['text'], hover=c['hover'],
                     active=c['selection'], stripe=c['stripe'], height=29, pad=3)
        panel_css_text = eval(compile(panel_expr, '<panel-qss>', 'eval'), local)
        assert 'QLineEdit#mainSearchField {' in search_css
        assert 'border-radius:17px' in search_css
        assert 'QTreeWidget#expandedTree' in panel_css_text
        assert c['panel'] in panel_css_text
        assert c['panel_border'] in panel_css_text
