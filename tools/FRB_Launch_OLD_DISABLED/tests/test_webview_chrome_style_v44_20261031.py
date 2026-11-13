"""WebView chrome-like styling contract; runnable without PySide6 installed."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
ICONS = (ROOT / 'src' / 'browser_nav_icons.py').read_text(encoding='utf-8')


def test_modified_sources_are_valid_python():
    ast.parse(WEB)
    ast.parse(ICONS)


def test_normal_weight_on_all_web_tabs_including_active_tab():
    assert 'font-weight:600' not in WEB
    assert 'QTabBar#launchWebTabBar::tab:selected {{background:{bg};font-weight:400;}}' in WEB
    assert 'font-weight:400;min-height:20px' in WEB


def test_icons_use_main_launcher_vector_provider():
    assert 'from browser_nav_icons import browser_navigation_icon' in WEB
    for name in ('back_arrow', 'forward', 'reload', 'external', 'download'):
        assert f"self._nav_button('{name}'" in WEB
    assert "button.setIcon(browser_navigation_icon(button.property('webIconName'), family))" in WEB
    assert "self.new_tab_button.setIcon(browser_navigation_icon('plus', family))" in WEB


def test_close_button_is_small_unboxed_x_and_closes_correct_tab_after_reorder():
    assert 'class _WebCloseButton(QToolButton)' in WEB
    assert "self.setObjectName('launchWebCloseButton')" in WEB
    assert 'self.setFocusPolicy(Qt.FocusPolicy.NoFocus)' in WEB
    assert "self.close_tab(self.tabs.indexOf(v))" in WEB
    assert 'setTabButton(index, QTabBar.ButtonPosition.RightSide,' in WEB
    assert "QToolButton#launchWebCloseButton {{background:transparent;border:0;" in WEB
    assert 'QToolButton#launchWebCloseButton:hover {{background:{hover};}}' in WEB
    assert 'self.tabs.setTabsClosable(True)' in WEB


def test_site_favicon_with_globe_fallback_and_updates():
    assert 'view.iconChanged.connect(lambda icon, v=view: self.update_tab_icon(v, icon))' in WEB
    assert 'if icon is not None and not icon.isNull():' in WEB
    assert 'self.tabs.setTabIcon(index, icon)' in WEB
    assert "self.tabs.setTabIcon(index, browser_navigation_icon('globe', family))" in WEB


def test_vector_paths_are_theme_aware_and_dpi_aware():
    for name in ('reload', 'plus', 'external', 'download', 'close', 'globe'):
        assert f"name == '{name}'" in ICONS
    assert "pen.setWidthF(1.0 if name == 'home' else 1.6 if name == 'close' else 2.0)" in ICONS
    assert 'pixmap.setDevicePixelRatio(_ICON_SCALE)' in ICONS
    assert 'QIcon.Mode.Disabled' in ICONS


def test_tab_navigation_and_webview_behavior_preserved():
    for fragment in ('self.tabs.setMovable(True)',
                     'self.tabs.tabCloseRequested.connect(self.close_tab)',
                     'def createWindow(self, window_type):',
                     'def select_tab(self, step):',
                     'def scroll_page(self, step):',
                     'def tab_context_menu(self):',
                     'def page_context_menu(self):'):
        assert fragment in WEB


def test_tab_css_uses_background_not_bold_for_current():
    assert 'QTabBar#launchWebTabBar::tab:hover:!selected {{background:{hover};}}' in WEB
    assert 'QTabBar#launchWebTabBar[remoteWebActive="true"]::tab:selected' in WEB
    assert 'self._refresh_icons(theme)' in WEB
