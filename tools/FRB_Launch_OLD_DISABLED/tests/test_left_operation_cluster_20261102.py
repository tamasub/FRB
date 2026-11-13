"""UI contract regression for moving FRB Launch's primary operations left.

Qt is not installed in the packaging environment, so the UI wiring is
verified structurally. Routing is also exercised with a fake Launcher to
cover URL/open safety without triggering Windows or a WebEngine process.
"""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'

def code(file):
    return (SRC / file).read_text(encoding='utf-8')

def method(file, classname, name):
    source = code(file)
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == classname)
    func = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, func)


def test_bookmarks_no_indicator_and_smaller_font():
    source = code('browser_bookmark_bar.py')
    assert 'QToolButton#launchWebBookmarkEntry::menu-indicator { image: none; width: 0px; }' in source
    assert 'QToolButton#launchWebBookmarkEntry { font-size: 12px; }' in source
    assert 'font.setPointSizeF(max(8.0, font.pointSizeF() - 1.0))' in source
    assert 'flatten_bookmark_rows' in source  # All nested URL leaves display inline.
    assert 'button.setMenu(menu)' not in source  # No per-folder popup menus.


def test_browser_favorites_left_and_bookmark_navigation_unchanged():
    source = code('launch_web_view.py')
    assert 'address_row.insertWidget(0, self.favorite_dropdown)' in source
    assert 'address_row.insertWidget(0, self.favorite_save)' in source
    assert 'self.favorite_dropdown.clicked.connect(self.toggle_url_favorites)' in source
    assert 'self.favorite_save.clicked.connect(self.register_url_favorite)' in source


def test_files_breadcrumb_left_controls_and_up_button():
    source = code('expanded_view.py')
    assert 'self.editor.setTextMargins(left_margin, 0, 0, 0)' in source
    assert 'self.crumb_layout.setContentsMargins(left_margin, 1, 4, 1)' in source
    assert 'for button in (combo, favorite, apply):' in source
    assert 'shared_layout.insertWidget(shared_layout.indexOf(self.address_bar), self.middle.back)' in source
    assert 'self.middle.back.clicked.connect(self.go_up)' in source


def test_files_second_column_smaller_font_not_other_panes():
    source = code('expanded_view.py')
    assert "tree.setProperty('detailsColumns', True)" in source
    assert 'QTreeWidget#expandedTree[detailsColumns="true"] {{font-size:12px;}}' in source


def test_launch_pages_by_files_browser_and_no_second_layer_shortcuts():
    source = code('expanded_view.py')
    assert "self.workspace_page_buttons = []" in source
    assert "self.launcher.open_remote_page(pid, anchor=b)" in source
    assert "self.root_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignVCenter)" in source
    assert "# Root shortcuts remain in memory/search/keyboard routes" in source
    assert 'button.hide()\n                self.root_buttons.append(button)' in source
    assert 'self.open_cascade(row, anchor)' in source


def test_launcher_settings_after_home_and_page_cascade_works_without_remote():
    source = code('app.py')
    assert 'nav_layout.addWidget(self.theme_button)' in source
    assert 'search_row.removeWidget(self.theme_button)' in source
    assert 'def open_remote_page(self, page_id, anchor=None):' in source
    assert 'button = (anchor if anchor is not None else next' in source
    assert 'self.tabs.hide()\n            self.page_overflow_button.hide()\n            return' in source
    assert 'self.menu = menu' in method('app.py', 'Launcher', 'open_remote_page')


def test_remote_pages_removed_but_files_exp_and_history_retained():
    source = code('launch_remote.py')
    assert 'root.addLayout(self.page_column)' not in source
    assert 'self.page_separator.hide()' in source
    assert "'WORKSPACE_FILES'" in source
    assert "'FOLDER_HISTORY'" in source
    assert "'SEARCH_HISTORY'" in source
    assert "for page in list(pages)[:3]:" not in source


def test_global_url_search_uses_embedded_browser_and_preserves_files():
    from sys import path
    import sys
    sys.path.insert(0, str(SRC))
    from webview_routes import bookmark_web_url
    act = {'item_kind': 'command', 'launch_actions': [
        {'launch_action_type': 'Open', 'launch_target': 'https://example.com/a'}]}
    assert bookmark_web_url(act) == 'https://example.com/a'
    assert bookmark_web_url({'item_kind':'command','launch_actions':[
        {'launch_action_type':'Open','launch_target':'C:/Work/test.txt'}]}) is None
    assert bookmark_web_url({'item_kind':'command','launch_actions':[
        {'launch_action_type':'Run','launch_target':'https://example.com'}]}) is None
    assert bookmark_web_url({'item_kind':'command','launch_actions':[
        {'launch_action_type':'Open','launch_target':'javascript:alert(1)'}]}) is None

    class Search:
        def __init__(self): self.value = 'example'
        def text(self): return self.value
        def clear(self): self.value = ''
        def setText(self, text): self.value = text
    class View:
        def __init__(self): self.calls = []; self.bookmark_new_tab = True
        def isVisible(self): return True
        def show_web_url(self, url, *, new_tab=False):
            self.calls.append((url, new_tab))
            return True
    class Launcher:
        def set_view_mode(self, mode): self.view_mode = mode
    obj = Launcher()
    obj.search = Search()
    obj.selection = None
    obj.webview_settings = {'mode':'embedded'}
    obj.view_mode = 'expanded'
    obj.expanded_view = View()
    func_src = method('app.py','Launcher','open_search_url_in_browser')
    tree = ast.parse(func_src)
    namespace = {'bookmark_web_url':bookmark_web_url}
    exec(compile(tree, '<isolated route>', 'exec'),namespace)
    obj.open_search_url_in_browser = namespace['open_search_url_in_browser'].__get__(obj, Launcher)
    assert obj.open_search_url_in_browser(act)
    assert obj.expanded_view.calls == [('https://example.com/a', True)]
    assert obj.search.text() == ''
    obj.search.value = 'test'
    assert not obj.open_search_url_in_browser({'item_kind':'command','launch_actions':[
        {'launch_action_type':'Open','launch_target':'C:/Work/test.txt'}]})
    assert obj.search.text() == 'test'
