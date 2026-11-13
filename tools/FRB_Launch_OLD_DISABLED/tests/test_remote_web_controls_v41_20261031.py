"""Contract tests for v41, Qt-independent because Windows UI runs elsewhere."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_navigation import next_area, previous_area, starting_area, WEB_AREAS, EXPANDED_AREAS
from expanded_keyboard_model import tab_target, FOCUS_ORDER, WEB_FOCUS_ORDER
from webview_settings import read_webview_settings, DEFAULTS


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def test_files_remote_stays_backward_compatible():
    assert EXPANDED_AREAS == ('search', 'pages', 'roots', 'breadcrumb', 'files', 'directory', 'sort', 'bookmarks')
    assert next_area('directory') == 'sort'
    assert previous_area('bookmarks') == 'sort'
    assert starting_area(None) == 'directory'
    assert tab_target('sort') == 'bookmarks'


def test_web_remote_tab_forward_and_backward_ring():
    assert WEB_AREAS == WEB_FOCUS_ORDER
    for i, area in enumerate(WEB_AREAS):
        assert next_area(area, web=True) == WEB_AREAS[(i+1) % len(WEB_AREAS)]
        assert previous_area(area, web=True) == WEB_AREAS[(i-1) % len(WEB_AREAS)]
        assert tab_target(area, order=WEB_FOCUS_ORDER) == WEB_AREAS[(i+1) % len(WEB_AREAS)]
        assert tab_target(area, backward=True, order=WEB_FOCUS_ORDER) == WEB_AREAS[(i-1) % len(WEB_AREAS)]
    assert previous_area('bookmarks', web=True) == 'web_body'
    assert next_area('web_tabs', web=True) == 'web_body'
    assert next_area('web_body', web=True) == 'bookmarks'
    assert starting_area(None, web=True) == 'web_body'
    assert starting_area('bookmarks', web=True) == 'bookmarks'


def test_classic_remote_ignores_web_flag():
    assert next_area('pages', expanded=False, web=True) == 'list'
    assert starting_area(None, expanded=False, web=True) == 'list'


def test_webview_settings_defaults_and_valid_overrides(tmp_path):
    path = tmp_path / 'settings.json'
    assert read_webview_settings(path) == DEFAULTS
    path.write_text('{"new_tab_url":"https://example.com/", "bookmark_preview_delay_ms": 450, "keep_tabs_on_home": false}')
    value = read_webview_settings(path)
    assert value['new_tab_url'] == 'https://example.com/'
    assert value['bookmark_preview_delay_ms'] == 450
    assert value['keep_tabs_on_home'] is False
    path.write_text('{"new_tab_url":"javascript:alert(1)", "bookmark_preview_delay_ms": true, "keep_tabs_on_home": "false"}')
    assert read_webview_settings(path) == DEFAULTS
    path.write_text('bad json')
    assert read_webview_settings(path) == DEFAULTS
    shipped = json.loads(read('config/webview_settings.json'))
    assert shipped['new_tab_url'] == 'https://www.google.com/'


def test_app_routes_remote_commands_by_web_mode():
    src = read('src/app.py')
    tree = ast.parse(src)
    clazz = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    names = {method.name for method in clazz.body if isinstance(method, ast.FunctionDef)}
    for name in ('remote_web_context_menu', 'web_view_activated', 'web_surface_selected',
                 'web_keyboard_tab', 'remote_command', 'remote_mouse_click', 'navigate_home'):
        assert name in names
    assert 'previous_area(area, expanded=expanded, web=web_active)' in src
    assert 'next_area(area, expanded=expanded, web=web_active)' in src
    assert "browser.scroll_page(step)" in src
    assert "browser.select_tab(step)" in src
    assert "self.remote_web_context_menu(area)" in src
    assert "self.remote_focus_area('files')" in src


def test_webview_uses_native_html_tab_and_safe_page_scroll():
    src = read('src/launch_web_view.py')
    tree = ast.parse(src)
    assert any(isinstance(node, ast.ClassDef) and node.name == '_WebTabBar' for node in tree.body)
    assert 'area_tab_requested = Signal(bool)' in src
    assert 'window.scrollBy' in src
    assert 'runJavaScript' in src
    assert 'QKeyEvent' not in src and 'SendKeys' not in src
    assert 'set_remote_area' in src
    assert 'surface_selected.emit' in src


def test_remote_context_menu_has_page_and_tab_actions_near_pad():
    src = read('src/launch_web_view.py')
    assert "'現在のタブを閉じる'" in src
    assert "'他のタブを閉じる'" in src
    assert "'ページのURLをコピー'" in src
    assert "'現在のページを新しいタブで開く'" in src
    app = read('src/app.py')
    assert "pad.mapToGlobal(QPoint(pad.width() + 4, 0))" in app
    assert "menu.aboutToHide.connect(lambda: setattr(self, '_remote_web_popup', None))" in app
    assert 'menu.aboutToHide.connect(menu.deleteLater)' in app
    assert 'createStandardContextMenu()' not in app  # no fabricated DOM target


def test_web_mode_is_layer_not_a_replacement_for_files():
    src = read('src/expanded_view.py')
    assert 'self.files_content_stack.setCurrentWidget(self.web_view)' in src
    assert 'self.files_content_stack.setCurrentWidget(self.files_group)' in src
    assert 'self.web_view.surface_selected.connect(self.launcher.web_surface_selected)' in src
    assert "self.launcher.web_view_activated()" in src
    assert 'self.web_view.set_remote_area(None)' in src


def test_google_new_tab_and_link_open_in_new_tab_remains_separate():
    src = read('src/launch_web_view.py')
    assert "self.web_settings.get('new_tab_url', 'https://www.google.com/')" in src
    assert 'def createWindow(self, window_type):' in src
    assert 'return self._owner.add_tab(activate=not background)' in src
