"""v73 Browser button right-click shows first-column bookmark cascade.

Pure-Python regression tests: Qt/Windows interaction still requires manual check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def method(source, cls, name, env=None):
    tree = ast.parse(source)
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 f'<{cls}.{name}>', 'exec'), scope)
    return scope[name]


def source_method(source, cls, name):
    tree = ast.parse(source)
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(source, fn)


def test_browser_right_click_is_independent_of_left_workspace_switch():
    init = source_method(REMOTE, 'LaunchRemote', '__init__')
    assert "'WORKSPACE_BROWSER', width=85" in init
    assert 'self.browser_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)' in init
    assert "self.command.emit('REMOTE_BROWSER_BOOKMARK_MENU')" in init
    remote_command = source_method(APP, 'Launcher', 'remote_command')
    assert "if command == 'REMOTE_BROWSER_BOOKMARK_MENU':" in remote_command
    assert 'self.show_remote_browser_bookmark_menu()' in remote_command


def test_first_column_is_exactly_rendered_bookmarks_not_an_independent_store():
    fn = method(APP, 'Launcher', '_remote_browser_bookmark_rows')
    folders = [
        {'item_kind': 'command', 'title': 'GA_Zenn', '_browser_bookmark': True},
        None,  # visual section header (not a real bookmark)
        {'item_kind': 'category', 'title': 'Studioくん', '_browser_bookmark': True},
        {'title': 'invalid'},
    ]
    tree = NS(topLevelItemCount=lambda: len(folders), topLevelItem=lambda i: i)
    view = NS(right=NS(tree=tree), row_data=lambda i: folders[i])
    result = fn(NS(expanded_view=view))
    assert [row['title'] for row in result] == ['GA_Zenn', 'Studioくん']


def test_browser_menu_reuses_remote_page_navigation_and_bookmark_semantics():
    created = []

    class DummyCascade:
        def __init__(self, parent, launcher):
            created.append(self)
            self.max_width = 450
        def maximumWidth(self):
            return self.max_width
        def setMaximumWidth(self, value):
            self.max_width = value
        def popup(self, pos):
            self.popup_position = pos
        def close(self):
            self.closed = True

    class Button:
        def width(self):
            return 85
        def mapToGlobal(self, pos):
            return ('browser_right_edge', pos)

    remote = NS(isVisible=lambda: True, browser_button=Button())
    view = NS(isVisible=lambda: True, bookmarks_root={'item_id': 'root'})
    filled = []
    root = NS(remote_window=remote, expanded_view=view, menu=None,
              close_remote_page_menu=Mock(), close_remote_folder_menu=Mock(),
              _apply_remote_popup_bounds=lambda menu: menu,
              fill_cascade=lambda menu, row: filled.append((menu, row)))
    fn = method(APP, 'Launcher', 'show_remote_browser_bookmark_menu', {
        'CascadeMenu': DummyCascade, 'CASCADE_MAX_WIDTH': 450,
        'QPoint': lambda x, y: (x, y)})
    fn(root)
    assert len(created) == 1
    menu = created[0]
    assert menu.remote_page_navigation is True
    assert menu.bookmark_navigation is True
    assert menu.bookmark_compact_width is True
    assert menu.max_width == round(450 * 0.7)
    assert root._remote_page_menu is menu and root.menu is menu
    assert menu.popup_position == ('browser_right_edge', (84, 0))
    assert filled[0][1]['launch_source'] == 'remote_browser_bookmark_roots'
    root.close_remote_folder_menu.assert_called_once()
    root.close_remote_page_menu.assert_called_once()


def test_no_browser_popup_without_visible_remote_or_expanded_workspace():
    fn = method(APP, 'Launcher', 'show_remote_browser_bookmark_menu', {
        'CascadeMenu': lambda **kwargs: None})
    for visible_remote, visible_expanded, bookmark_root in (
        (False, True, {}), (True, False, {}), (True, True, None)):
        root = NS(remote_window=NS(isVisible=lambda: visible_remote),
                  expanded_view=NS(isVisible=lambda: visible_expanded,
                                   bookmarks_root=bookmark_root),
                  close_remote_folder_menu=Mock())
        fn(root)
        root.close_remote_folder_menu.assert_not_called()


def test_cascade_builder_uses_bookmark_rows_only_for_browser_root():
    fill = source_method(APP, 'Launcher', 'fill_cascade')
    assert "elif parent.get('launch_source') == 'remote_browser_bookmark_roots':" in fill
    assert 'rows = self._remote_browser_bookmark_rows()' in fill
    assert "'remote_browser_bookmark_roots'" in fill
    assert 'm.child.bookmark_navigation = getattr(m, \'bookmark_navigation\', False)' in fill
    assert 'm.child.remote_page_navigation = getattr(m, \'remote_page_navigation\', False)' in fill
    assert 'm.child.remote_popup_bounds = m.remote_popup_bounds' in fill
    assert 'action.triggered.connect(lambda checked=False,r=row:self.run_menu_item(r))' in fill


def test_existing_bookmark_click_routing_is_used():
    assert 'if self.open_bookmark_web_view(row):' in APP
    assert 'return self.expanded_view.show_web_url(url)' in APP
    assert 'if self.menu:self.menu.close()\n        self.activate(row)' in APP
