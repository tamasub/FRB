"""Exercise REAL Launcher key handlers with lightweight Qt substitutes.

Do not instantiate Windows shell or QApplication on this non-Windows CI runner.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_keyboard_model import tab_target, root_step, middle_back_target, row_right_action
from navigation_wrap import move_tree_selection

KEYS = {'Tab': 1, 'Backtab': 2, 'Left': 3, 'Right': 4, 'Up': 5, 'Down': 6,
        'Return': 7, 'Enter': 8, 'Space': 9, 'Escape': 10, 'F': 11}
Qt = SimpleNamespace(
    Key=SimpleNamespace(**{'Key_' + k: v for k, v in KEYS.items()}),
    KeyboardModifier=SimpleNamespace(NoModifier=0, ShiftModifier=1, ControlModifier=2, AltModifier=4),
    FocusReason=SimpleNamespace(TabFocusReason=1),
    ItemDataRole=SimpleNamespace(UserRole=32),
)


def event(key, mods=0):
    class E:
        accepted = False
        def key(self): return KEYS[key]
        def modifiers(self): return mods
        def accept(self): self.accepted = True
    return E()


def dispatch_class():
    src = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf8'))
    launcher = next(n for n in src.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    names = ('expanded_focus_area', 'expanded_focus_key', 'expanded_root_key',
             'expanded_tab_key', 'expanded_tree_key')
    cls = ast.ClassDef(name='Dispatch', bases=[], keywords=[],
                       body=[n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name in names],
                       decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[]))
    ns = {'Qt': Qt, 'tab_target': tab_target, 'root_step': root_step,
          'middle_back_target': middle_back_target, 'row_right_action': row_right_action,
          'move_tree_selection': move_tree_selection}
    exec(compile(module, str(ROOT / 'src/app.py'), 'exec'), ns)
    return ns['Dispatch']


class TreeItem:
    def __init__(self, data): self.value = data
    def data(self, *_): return self.value
    def isHidden(self): return False
    def isDisabled(self): return False


class Tree:
    def __init__(self, items):
        self.items = [TreeItem(x) for x in items]
        self.selected = self.items[0] if self.items else None
        self.viewport_ref = object()
        self.scrolled = None
    def currentItem(self): return self.selected
    def setCurrentItem(self, x): self.selected = x
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, i): return self.items[i]
    def scrollToItem(self, item): self.scrolled = item
    def viewport(self): return self.viewport_ref


class Panel:
    def __init__(self, rows): self.tree = Tree(rows)


class View:
    def __init__(self):
        self.left = Panel([{'item_kind': 'directory', 'item_id': 'files', 'title': 'Files'}])
        self.middle = Panel([{'item_kind': 'directory', 'item_id': 'child', 'title': 'child'},
                             {'item_kind': 'command', 'item_id': 'run', 'title': 'run'}])
        self.right = Panel([{'item_kind': 'category', 'item_id': 'bookmarks'}])
        self.root_buttons = [object(), object(), object()]
        self.root_rows = [{'item_id': 'settings', 'item_kind': 'command'},
                          {'item_id': 'files_root', 'item_kind': 'category'},
                          {'item_id': 'bookmarks_root', 'item_kind': 'category'}]
        self.files_root = {'item_id': 'files_root'}
        self.bookmarks_root = {'item_id': 'bookmarks_root'}
        self.path = [{'item_id': 'files'}]
        self.actions = []
        self.launcher = SimpleNamespace(activate=lambda row: self.actions.append(('execute', row['item_id'])))
    def isVisible(self): return True
    def focus_panel(self, panel): self.actions.append(('focus', panel))
    def focus_root(self, **kwargs): self.actions.append(('root_focus', kwargs))
    def choose_files(self, item, _): self.actions.append(('preview', item.value['item_id']))
    def navigate_middle(self, row): self.actions.append(('descend', row['item_id']))
    def go_up(self, **kwargs): self.actions.append(('up', kwargs))
    def history_back(self): self.actions.append(('history_back',))
    def history_forward(self): self.actions.append(('history_forward',))
    def row_data(self, item): return item.value
    def enter_row(self, panel, item): self.actions.append(('enter', item.value['item_id']))
    def open_cascade(self, row, *_): self.actions.append(('cascade', row['item_id']))
    def root_action(self, row, *_): self.actions.append(('root_enter', row['item_id']))


def instance():
    d = dispatch_class()()
    d.expanded_view = View()
    d.search = SimpleNamespace(setFocus=lambda *_: None)
    d.tabs = SimpleNamespace(setFocus=lambda *_: None)
    d.menu = None
    d.page_key = lambda e: False
    d.focus_search = lambda: None
    d.dismiss = lambda: None
    return d


def test_right_from_files_previews_then_focus_middle():
    d = instance()
    e = event('Right')
    assert d.expanded_tree_key(d.expanded_view.left.tree, e)
    assert d.expanded_view.actions == [('preview', 'files'), ('focus', d.expanded_view.middle)]
    assert e.accepted


def test_right_from_middle_descends_but_does_not_execute():
    d = instance()
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Right'))
    assert d.expanded_view.actions == [('descend', 'child')]
    d.expanded_view.middle.tree.setCurrentItem(d.expanded_view.middle.tree.items[1])
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Right'))
    assert d.expanded_view.actions[-1] == ('execute', 'run')


def test_left_from_middle_and_files_returns_to_explorer_history():
    d = instance()
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Left'))
    assert d.expanded_tree_key(d.expanded_view.left.tree, event('Left'))
    assert d.expanded_view.actions == [('history_back',), ('history_back',)]


def test_alt_right_forward_but_plain_right_enters_directory():
    d = instance()
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Right', 4))
    assert d.expanded_view.actions == [('history_forward',)]
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Right'))
    assert d.expanded_view.actions[-1] == ('descend', 'child')


def test_arrows_wrap_rows_without_leaving_panel():
    d = instance()
    tree = d.expanded_view.middle.tree
    assert d.expanded_tree_key(tree, event('Up'))
    assert tree.currentItem().value['item_id'] == 'run'
    assert d.expanded_tree_key(tree, event('Down'))
    assert tree.currentItem().value['item_id'] == 'child'


def test_first_level_down_executes_leaf_command_and_enters_categories():
    d = instance()
    b = d.expanded_view.root_buttons[0]
    assert d.expanded_root_key(b, event('Down'))
    assert d.expanded_view.actions == [('root_enter', 'settings')]
    assert d.expanded_root_key(b, event('Return'))
    assert d.expanded_view.actions == [('root_enter', 'settings'), ('root_enter', 'settings')]
    b = d.expanded_view.root_buttons[1]
    assert d.expanded_root_key(b, event('Down'))
    assert d.expanded_view.actions[-1] == ('focus', d.expanded_view.left)


def test_tab_from_files_goes_middle_and_shift_tab_goes_first_level():
    d = instance()
    t = d.expanded_view.left.tree
    assert d.expanded_focus_key(t, event('Tab'))
    assert d.expanded_view.actions[-1] == ('focus', d.expanded_view.middle)
    assert d.expanded_focus_key(t, event('Backtab', 1))
    assert d.expanded_view.actions[-1] == ('root_focus', {})


def test_enter_in_middle_delegates_to_explicit_enter_contract():
    d = instance()
    assert d.expanded_tree_key(d.expanded_view.middle.tree, event('Return'))
    assert d.expanded_view.actions == [('enter', 'child')]


def test_files_up_down_previews_without_moving_keyboard_focus():
    d = instance()
    tree = d.expanded_view.left.tree
    assert d.expanded_tree_key(tree, event('Down'))
    assert d.expanded_view.actions == [('preview', 'files')]
