"""Files Exp multi-column breadcrumb trail; tests run without PySide6.

The Qt paint itself needs Windows inspection, while menu/scroll route state
and the shared menu title are mechanically verified here.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
CLASS = next(node for node in TREE.body if isinstance(node, ast.ClassDef) and node.name == 'CascadeMenu')


def extract(name, environment=None):
    node = next(node for node in CLASS.body if isinstance(node, ast.FunctionDef) and node.name == name)
    namespace = dict(environment or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<extracted method>', 'exec'), namespace)
    return namespace[name]


def test_visible_open_child_pins_its_exact_owner_even_if_parent_has_no_focus():
    route = object()
    fn = extract('_visible_route_action')
    menu = NS(remote_folder_navigation=True,
              child=NS(owner_action=route, isVisible=lambda: True))
    assert fn(menu) is route
    menu.child.isVisible = lambda: False
    assert fn(menu) is None
    menu.child.isVisible = lambda: True
    menu.remote_folder_navigation = False
    menu.remote_context_root = False
    assert fn(menu) is None
    menu.remote_context_root = True  # Context menu itself is first column.
    assert fn(menu) is route


class FakeItem:
    def __init__(self, action):
        self.action = action
        self.props = {}
        self.background = None

    def data(self, column, role):
        return self.props.get((column, role))

    def setData(self, column, role, value):
        self.props[(column, role)] = value

    def setBackground(self, column, brush):
        assert column == 0
        self.background = brush


class FakeTree:
    def __init__(self, actions):
        self.items = [FakeItem(action) for action in actions]
        self.viewport_updates = 0

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, i):
        return self.items[i]

    def viewport(self):
        return NS(update=self.update)

    def update(self):
        self.viewport_updates += 1


def test_tall_scroll_columns_keep_only_opened_folder_blue_and_clear_on_close():
    role = 32
    selected, other = object(), object()
    tree = FakeTree([other, selected])
    current = [selected]
    redraws = []
    menu = NS(
        scroll_tree=tree,
        launcher=NS(color_theme='light'),
        _visible_route_action=lambda: current[0],
        _scroll_item_action=lambda item: item.action,
        update=lambda: redraws.append('update'),
    )
    fn = extract('_refresh_route_highlight', {
        'QBrush': lambda c=None: ('brush', c),
        'QColor': lambda c: c,
        'theme_family': lambda theme: theme,
        'Qt': NS(ItemDataRole=NS(UserRole=role)),
    })
    fn(menu)
    assert tree.items[1].background == ('brush', '#d6e7f8')
    assert tree.items[0].background is None
    current[0] = other
    fn(menu)
    assert tree.items[0].background == ('brush', '#d6e7f8')
    assert tree.items[1].background == ('brush', None)
    current[0] = None
    fn(menu)
    assert tree.items[0].background == ('brush', None)
    assert tree.viewport_updates == 3 and len(redraws) == 3


def test_parent_refresh_is_triggered_on_child_show_and_hide():
    show = ast.get_source_segment(SOURCE, next(node for node in CLASS.body
        if isinstance(node, ast.FunctionDef) and node.name == 'showEvent'))
    hide = ast.get_source_segment(SOURCE, next(node for node in CLASS.body
        if isinstance(node, ast.FunctionDef) and node.name == 'hideEvent'))
    draw = ast.get_source_segment(SOURCE, next(node for node in CLASS.body
        if isinstance(node, ast.FunctionDef) and node.name == 'paintEvent'))
    assert 'self._refresh_parent_route_highlight()' in show
    assert 'self._refresh_parent_route_highlight()' in hide
    assert 'route = self._visible_route_action()' in draw
    assert 'painter.fillRect(rect.adjusted(1, 1, -1, -1)' in draw


def test_shared_folder_menu_is_renamed_once_without_changing_action_id():
    assert "folder_list_action = menu.addAction('Filesリスト')" in SOURCE
    assert "menu.addAction('フォルダー・ファイルリスト')" not in SOURCE
    assert "'item_id': 'remote-folder-list'" in SOURCE
    assert 'menu.openers[folder_list_action]' in SOURCE
