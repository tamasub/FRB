"""v69: light-mode browser resize background + extra workspace drag band.

Qt-free source contract tests only.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')


def get_method_source(source, class_name, method_name):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    return ast.get_source_segment(source, fn)


def test_launcher_adds_passive_drag_to_workspace_strip_backgrounds_only():
    init = get_method_source(APP, 'Launcher', '__init__')
    assert 'for surface in (self.expanded_view.root_widget,' in init
    assert 'self.expanded_view.toolbar_scroller,' in init
    assert 'self.expanded_view.toolbar_scroller.viewport()' in init
    assert 'surface.installEventFilter(self._passive_header_drag)' in init
    # Existing header drag surfaces remain intact too.
    assert 'self._passive_header_drag = PassiveHeaderDrag(self)' in init


def test_webview_has_dedicated_background_filler_for_light_mode_resize():
    source = get_method_source(WEB, 'LaunchWebView', '_apply_view_backgrounds')
    assert "light = theme_family(theme) == 'light'" in source
    assert "self.setAutoFillBackground(light)" in source
    assert "self.tabs.setAutoFillBackground(light)" in source
    assert "view.page().setBackgroundColor(QColor(colors['panel']))" in source
    assert "view.page().setBackgroundColor(QColor(0, 0, 0, 0))" in source
    assert "view.setStyleSheet(f'background:{panel}; border:0;')" in source


def test_webview_theme_calls_background_filler_and_new_tabs_inherit_it():
    apply_theme = get_method_source(WEB, 'LaunchWebView', 'apply_theme')
    assert 'self._apply_view_backgrounds(theme)' in apply_theme
    add_tab = get_method_source(WEB, 'LaunchWebView', 'add_tab')
    assert "current_theme = getattr(self, '_current_theme', 'light')" in add_tab
    assert "view.page().setBackgroundColor(QColor(theme_palette(current_theme)['panel']))" in add_tab
    assert "view.setStyleSheet(f\"background:{theme_palette(current_theme)['panel'] if theme_family(current_theme) == 'light' else 'transparent'}; border:0;\")" in add_tab


def test_browser_chrome_keeps_frame_style_while_pane_background_is_explicit():
    apply_theme = get_method_source(WEB, 'LaunchWebView', 'apply_theme')
    assert 'QFrame#launchWebView {{background:{hdr};border:1px solid {border};border-top:0;' in apply_theme
    assert 'border-top-left-radius:0;border-top-right-radius:11px;' in apply_theme
    assert 'QTabWidget#launchWebTabs {{border:0;background:{bg};}}' in apply_theme
    assert 'QTabWidget#launchWebTabs::pane {{border:0;margin:0;padding:0;background:{bg};}}' in apply_theme
