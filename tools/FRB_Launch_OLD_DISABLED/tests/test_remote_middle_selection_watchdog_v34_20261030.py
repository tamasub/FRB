"""v34: recover the actionable current row in column 2, Qt-free policy tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from middle_selection_guard import repair_middle_selection, row_key


class Row:
    def __init__(self, name, selectable=True):
        self.data = {'item_id': name, 'title': name} if selectable else None
        self.selected = False
    def isSelected(self): return self.selected
    def setSelected(self, value): self.selected = value


class Tree:
    def __init__(self, rows, current=None):
        self.rows = rows
        self.current = current
        self.scrolled = []
        self.updated = 0
    def topLevelItemCount(self): return len(self.rows)
    def topLevelItem(self, index): return self.rows[index]
    def currentItem(self): return self.current
    def setCurrentItem(self, item):
        self.current = item
        item.selected = True
    def selectedItems(self): return [item for item in self.rows if item.selected]
    def scrollToItem(self, item): self.scrolled.append(item)
    def viewport(self): return self
    def update(self): self.updated += 1


def restore(tree, remembered=None):
    return repair_middle_selection(tree, lambda item: item.data, remembered)


def test_missing_current_restores_previous_file():
    a, b = Row('one'), Row('two')
    tree = Tree([a,b])
    current, recovered = restore(tree, 'two')
    assert current is b and tree.current is b and b.selected and recovered
    assert tree.scrolled == [b]


def test_fallback_to_first_actionable_and_never_choose_heading():
    heading, a, b = Row('heading', False), Row('one'), Row('two')
    tree = Tree([heading,a,b])
    current, recovered = restore(tree, 'gone')
    assert current is a and recovered


def test_missing_current_recovers_selected_row_without_destroying_multi_selection():
    a, b, c = Row('one'), Row('two'), Row('three')
    a.selected = c.selected = True
    tree = Tree([a,b,c])
    current, recovered = restore(tree)
    assert current is a and recovered
    assert [x.data['item_id'] for x in tree.selectedItems()] == ['one', 'three']


def test_current_unselected_preserves_keyboard_cursor_and_existing_multiselection():
    a, b = Row('one'), Row('two')
    b.selected = True
    tree = Tree([a,b], a)
    current, recovered = restore(tree)
    assert current is a and not recovered
    assert [x.data['item_id'] for x in tree.selectedItems()] == ['two']


def test_existing_current_but_no_selection_regains_fill_without_row_change():
    a, b = Row('one'), Row('two')
    tree = Tree([a,b], b)
    current, recovered = restore(tree)
    assert current is b and b.selected and recovered
    assert tree.current is b


def test_existing_healthy_current_not_changed():
    a = Row('one')
    a.selected = True
    tree = Tree([a],a)
    current, recovered = restore(tree)
    assert current is a and not recovered and not tree.scrolled and not tree.updated


def test_empty_directory_is_not_fabricated():
    tree = Tree([])
    assert restore(tree) == (None, False)
    assert tree.current is None


def test_renamed_item_key_only_matched_in_current_folder_by_caller():
    assert row_key({'item_id':'abc', 'title':'x'}) == 'abc'
    assert row_key({'title':'x'}) == 'x'
    assert row_key(None) is None


def test_production_guard_is_wired_at_remote_click_wheel_context_and_refresh():
    app = (ROOT/'src/app.py').read_text(encoding='utf-8')
    view = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
    assert app.count('ensure_middle_current_selection()') >= 3
    assert "repair = getattr(self.expanded_view, 'ensure_middle_current_selection', None)" in app
    assert 'self.middle.tree.itemSelectionChanged.connect(self._queue_middle_selection_repair)' in view
    assert 'self.middle.tree.model().modelReset.connect(self._queue_middle_selection_repair)' in view
    assert 'self._middle_selection_watchdog.timeout.connect(self.ensure_middle_current_selection)' in view
    assert 'tree.state() == QAbstractItemView.State.EditingState' in view


def test_view_guard_defers_while_rename_is_editing_and_recovers_when_idle():
    """Execute the production view guard without importing Qt."""
    import ast
    from types import SimpleNamespace as NS
    from unittest.mock import Mock
    module = ast.parse((ROOT/'src/expanded_view.py').read_text(encoding='utf-8'))
    cls = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == 'ExpandedLauncherView')
    method = next(x for x in cls.body if isinstance(x, ast.FunctionDef)
                  and x.name == 'ensure_middle_current_selection')
    env = {'QAbstractItemView': NS(State=NS(EditingState='editing')),
           'repair_middle_selection': repair_middle_selection,
           'row_key': row_key}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<production-guard>', 'exec'), env)
    guard = env['ensure_middle_current_selection']
    a, b = Row('one'), Row('two')
    tree = Tree([a, b])
    tree._state = 'editing'
    tree.state = lambda: tree._state
    view = NS(middle=NS(tree=tree), _middle_selection_repair_running=False,
              _middle_current_memory=('folder', 'two'),
              _middle_selection_is_active=Mock(return_value=True),
              current_directory=lambda: 'folder', row_data=lambda item: item.data)
    assert guard(view) is None
    assert tree.current is None
    tree._state = 'idle'
    assert guard(view) is b and b.isSelected()
    assert view._middle_current_memory == ('folder', 'two')
    assert not view._middle_selection_repair_running


def test_view_guard_does_not_change_column_when_not_active():
    import ast
    from types import SimpleNamespace as NS
    module = ast.parse((ROOT/'src/expanded_view.py').read_text(encoding='utf-8'))
    cls = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == 'ExpandedLauncherView')
    method = next(x for x in cls.body if isinstance(x, ast.FunctionDef)
                  and x.name == 'ensure_middle_current_selection')
    env = {'QAbstractItemView': NS(State=NS(EditingState='editing')),
           'repair_middle_selection': repair_middle_selection, 'row_key': row_key}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<production-guard>', 'exec'), env)
    tree = Tree([Row('one')]); tree.state = lambda: 'idle'
    view = NS(middle=NS(tree=tree), _middle_selection_repair_running=False,
              _middle_selection_is_active=lambda: False)
    assert env['ensure_middle_current_selection'](view) is None
    assert tree.current is None
