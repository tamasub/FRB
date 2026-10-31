"""v61: Bookmarks-left Browser, Remote workspace switches, focus per HTML tab.

This suite deliberately uses Python-only navigation contracts because PySide6
is unavailable in the packaging environment; Windows UI still needs testing.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_navigation import navigation_order, next_area, previous_area, starting_area


def test_browser_tab_order_is_left_to_right_and_skips_web_tab_buttons():
    assert navigation_order(web=True, web_tab_count=3) == (
        'search', 'pages', 'workspace_files', 'workspace_browser',
        'bookmarks', 'web_body:0', 'web_body:1', 'web_body:2')
    assert next_area('bookmarks', web=True, web_tab_count=3) == 'web_body:0'
    assert next_area('web_body:0', web=True, web_tab_count=3) == 'web_body:1'
    assert next_area('web_body:2', web=True, web_tab_count=3) == 'search'
    assert previous_area('web_body:0', web=True, web_tab_count=3) == 'bookmarks'
    assert previous_area('bookmarks', web=True, web_tab_count=3) == 'workspace_browser'


def test_browser_empty_external_mode_has_bookmarks_but_no_page():
    assert navigation_order(web=True, web_tab_count=0) == (
        'search', 'pages', 'workspace_files', 'workspace_browser', 'bookmarks')
    assert next_area('workspace_browser', web=True, web_tab_count=0) == 'bookmarks'


def test_files_ring_keeps_directory_and_second_layer():
    areas = navigation_order()
    assert areas[:4] == ('search', 'pages', 'workspace_files', 'workspace_browser')
    assert areas.index('files') < areas.index('directory')
    assert 'roots' in areas
    assert 'bookmarks' not in areas


def test_backward_and_legacy_area_fallback():
    assert previous_area('web_body:1', web=True, web_tab_count=2) == 'web_body:0'
    assert next_area('web_body', web=True, web_tab_count=2, current_tab=0) == 'web_body:1'
    assert starting_area('web_tabs', web=True, web_tab_count=2, current_tab=1) == 'web_body:1'
    assert starting_area('search', web=True, web_tab_count=0) == 'bookmarks'


def test_browser_splitter_order_and_legacy_widths():
    source = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert source.index('self.splitter.addWidget(self.right)') < source.index(
        'self.splitter.addWidget(self.files_content_stack)')
    assert 'self.splitter.setSizes([350, 660])' in source
    assert "self._browser_splitter_sizes = [values[2], values[0] + values[1]]" in source
    assert 'widths = file_widths + self.splitter.sizes()[:1]' in source
    assert "self.right.hide()  # Bookmarks belong to Browser" in source


def test_remote_new_buttons_and_more_menu_switch():
    source = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
    assert 'row_workspaces.addWidget(self.files_button)' in source
    assert 'row_workspaces.addWidget(self.browser_button)' in source
    assert source.index('root.addLayout(row_workspaces)') < source.index('root.addLayout(row_top)')
    assert "'WORKSPACE_FILES'" in source and "'WORKSPACE_BROWSER'" in source
    assert "self.more_new_tab_action = self.more_menu.addAction('新規タブ追加')" in source
    assert 'self.more_new_tab_action.setVisible(browser)' in source
    assert 'self.more_favorite_action.setVisible(not browser)' in source
    assert 'self.more_category_action.setVisible(not browser)' in source


def test_launcher_routes_tab_and_new_web_page_without_destruction():
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    assert "if command == 'REMOTE_NEW_WEB_TAB':" in source
    assert "if command in ('WORKSPACE_FILES', 'WORKSPACE_BROWSER'):" in source
    assert "view.web_view.tabs.setCurrentIndex(int(target.split(':', 1)[1]))" in source
    assert "self._focus_bookmark_first()" in source
    assert 'web_tab_count=self._web_tab_count()' in source
    assert "if obj is self.expanded_view.files_mode_tab:" in source
    assert "if obj is self.expanded_view.browser_mode_tab:" in source
    assert 'view.web_view.tabs.tabBar().setFocus(' not in source[source.index('    def expanded_focus_key('):source.index('    def execute_expanded_root_shortcut(')]


def test_remote_bookmark_click_activates_but_selection_does_not():
    source = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
    start = source.index('        elif pane is view.right:', source.index('    def remote_mouse_click('))
    end = source.index('    def remote_web_context_menu', start)
    code = source[start:end]
    assert 'if not double:' in code
    assert 'view.activate_row(pane, item)' in code
    assert 'view.choose_bookmark(item, 0)' in code
    expanded = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'def schedule_web_bookmark_preview' in expanded
    assert 'self._web_selection_timer.stop()' in expanded
