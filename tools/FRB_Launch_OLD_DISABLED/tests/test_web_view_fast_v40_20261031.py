"""Fast WebView challenge: route and UI integration checks (no Qt needed)."""
import ast
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'src'))
from webview_routes import bookmark_web_url


def _text(name):
    return (BASE / name).read_text(encoding='utf-8')


def test_native_bookmark_percent_escapes_roundtrip():
    row = {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': 'https://example.org/a%%20b?x=100%%25'}]}
    assert bookmark_web_url(row) == 'https://example.org/a%20b?x=100%25'


def test_regular_url_command_allowed():
    row = {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': 'https://zenn.dev/frb_tamasub/articles/demo'}]}
    assert bookmark_web_url(row) == 'https://zenn.dev/frb_tamasub/articles/demo'


def test_non_web_actions_never_hijacked():
    bad = [
        {'item_kind': 'category', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'https://example.org'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Run', 'launch_target': 'https://example.org'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'C:\\files\\a.html'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'javascript:alert(1)'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'file:///C:/secret'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'https://example.org'}, {'launch_action_type': 'SendKey', 'launch_text': 'x'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'https://example.org/a\nmalicious'}]},
        {'item_kind': 'command', 'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'http:///no-host'}]},
        {'item_kind': 'command', 'launch_actions': []},
        {'item_kind': 'command', 'launch_actions': 'not-list'},
    ]
    assert all(bookmark_web_url(row) is None for row in bad)


def test_source_files_parse():
    for path in ['src/webview_routes.py', 'src/launch_web_view.py', 'src/expanded_view.py', 'src/app.py']:
        ast.parse(_text(path), filename=path)


def test_webview_is_stacked_over_existing_files_without_replacing_them():
    src = _text('src/expanded_view.py')
    assert 'self.files_content_stack = QStackedWidget(self.splitter)' in src
    assert 'self.files_content_stack.addWidget(self.files_group)' in src
    assert 'self.splitter.addWidget(self.files_content_stack)' in src
    assert 'self.files_content_stack.setCurrentWidget(self.web_view)' in src
    assert 'self.files_content_stack.setCurrentWidget(self.files_group)' in src
    assert 'self.splitter.addWidget(self.right)' in src


def test_home_exits_web_first_and_remote_uses_home():
    src = _text('src/app.py')
    start = src.index('    def navigate_home(')
    end = src.index('\n    def ', start + 8)
    assert 'view.show_files_view()' in src[start:end]
    assert 'self.navigate_home()' in src[src.index("if command == 'HOME':"):]
    assert 'self.nav_home_button.clicked.connect(self.navigate_home)' in src


def test_native_browser_tab_requests_use_same_tab_widget():
    src = _text('src/launch_web_view.py')
    assert 'def createWindow(self, window_type)' in src
    assert 'WebBrowserBackgroundTab' in src
    assert 'return self._owner.add_tab(activate=not background)' in src
    assert 'self.tabs.setTabsClosable(True)' in src
    assert 'self.tabs.tabCloseRequested.connect(self.close_tab)' in src
    assert 'self.tabs.setMovable(True)' in src
    assert 'self.external' in src


def test_v49_bookmark_selection_only_does_not_navigate():
    # v49 intentionally replaces v40's auto-preview with explicit opening.
    src = _text('src/expanded_view.py')
    assert 'self.right.tree.currentItemChanged.connect(self.schedule_web_bookmark_preview)' not in src
    assert 'self.right.tree.itemClicked.connect(self.choose_bookmark)' in src
    assert 'self._web_selection_timer.stop()' in src
    assert 'self.web_view.show_url(url)' in src


def test_existing_launch_path_only_intercepted_in_expanded_mode():
    src = _text('src/app.py')
    assert 'not self.expanded_view.isVisible()' in src[src.index('    def open_bookmark_web_view'):src.index('    def navigate_home')]
    assert 'self.expanded_view.is_bookmark_row(row)' in src
    assert 'if self.open_bookmark_web_view(row):' in src
    assert 'self.next_step()' in src  # normal launch path retained


def test_existing_quick_web_shortcuts_stay_external():
    src = _text('src/expanded_view.py')
    assert 'def is_bookmark_row(self, row)' in src
    assert "bookmark_id = self.bookmarks_root.get('item_id')" in src
    assert 'while parent_id and parent_id not in seen:' in src
    assert 'if url and self.is_bookmark_row(row):' in src
    assert 'self.launcher.open_target(' in src
