"""v59 visual contract: Web URL text and Files toolbar buttons share Web chrome.

Static checks run even on systems without PySide6; verify the semantic theme
references and the actual fixed dimensions in source, not screenshot pixels.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
FILES = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def _method_source(source, class_name, function_name):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == class_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name == function_name)
    return ast.get_source_segment(source, node)


def test_url_font_and_color_are_subtle_and_theme_aware():
    style = _method_source(WEB, 'LaunchWebView', 'apply_theme')
    assert "muted = colors['muted_text']" in style
    assert "QLineEdit#launchWebAddress {{background:{colors['search_bg']};color:{muted};" in style
    assert 'padding:4px 10px;font-size:12px;' in style
    assert "border-radius:12px" in style
    assert "QLineEdit#launchWebAddress:focus" in style


def test_files_buttons_match_web_button_geometry():
    navigation = _method_source(WEB, 'LaunchWebView', '_nav_button')
    files_panel = _method_source(FILES, 'ExpandedPanel', '__init__')
    expanded = _method_source(FILES, 'ExpandedLauncherView', '__init__')
    assert 'button.setFixedSize(30, 29)' in navigation
    assert 'button.setIconSize(QSize(19, 19))' in navigation
    assert 'self.back.setFixedSize(30, 29)' in files_panel
    assert 'self.back.setIconSize(QSize(19, 19))' in files_panel
    assert 'self.density_button.setFixedSize(30, 29)' in expanded
    assert 'self.density_button.setIconSize(QSize(19, 19))' in expanded


def test_files_toolbar_uses_the_web_nav_style_tokens():
    files_theme = FILES[FILES.index('QToolButton#expandedDensityToggle {{'):]
    assert 'background:{bg};border:1px solid {border};' in files_theme
    assert 'border-radius:7px;color:{text};padding:0;' in files_theme
    up_style = FILES[FILES.index('QPushButton#expandedBack {{'):]
    assert 'background:{bg};border:1px solid {border};' in up_style
    assert 'border-radius:7px;padding:0;' in up_style
    web_theme = _method_source(WEB, 'LaunchWebView', 'apply_theme')
    assert 'QToolButton {{background:{bg};color:{text};border:1px solid {border};border-radius:7px;}}' in web_theme


def test_density_glyph_is_centered_on_hidpi_canvas():
    method = ast.parse(FILES)
    node = next(n for n in method.body if isinstance(n, ast.FunctionDef)
                and n.name == 'density_lines_icon')
    source = ast.get_source_segment(FILES, node)
    assert 'QPixmap(48, 48)' in source
    assert 'pix.setDevicePixelRatio(2)' in source
    # Qt applies the DPR transform itself; a manual scale would shift the glyph.
    assert 'painter.scale(2, 2)' not in source
    assert 'QPointF(5.5, y), QPointF(18.5, y)' in source
    assert "'#425750' if theme == 'light' else '#d5e3ed'" in source


def test_original_actions_and_theme_icon_updates_stay_wired():
    assert 'self.density_button.clicked.connect(self.toggle_row_density)' in FILES
    assert 'self.middle.back.clicked.connect(self.go_up)' in FILES
    assert "pane.back.setIcon(browser_navigation_icon('back', theme_family(theme)))" in FILES
    assert 'self.density_button.setIcon(density_lines_icon(theme_family(theme)))' in FILES
    assert 'self.address.returnPressed.connect(self.open_address)' in WEB
