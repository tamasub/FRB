"""Files middle-pane: date, size and type are read-only even on editable file rows.

No Qt dependency: exercise the real delegate source and inspect its actual wiring.
"""
import ast
from pathlib import Path


VIEW = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
MODULE = ast.parse(VIEW)


def test_metadata_delegate_refuses_all_editors():
    class BaseDelegate:
        def __init__(self, parent=None):
            self.parent = parent

    node = next(n for n in MODULE.body if isinstance(n, ast.ClassDef)
                and n.name == '_ReadOnlyMetadataDelegate')
    isolated = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    scope = {'QStyledItemDelegate': BaseDelegate}
    exec(compile(isolated, '<actual expanded_view.py>', 'exec'), scope)
    delegate = scope['_ReadOnlyMetadataDelegate']()
    # A filesystem row is still Qt ItemIsEditable for its filename. Metadata
    # must be non-editable irrespective of that row-wide flag.
    for col in (1, 2, 3):
        index = type('Index', (), {'column': lambda self, c=col: c})()
        assert delegate.createEditor(object(), object(), index) is None


def test_all_metadata_columns_get_readonly_delegate():
    cls = next(n for n in MODULE.body if isinstance(n, ast.ClassDef)
               and n.name == 'ExpandedLauncherView')
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name == '__init__')
    loops = [n for n in ast.walk(init) if isinstance(n, ast.For)]
    metadata_loop = next(n for n in loops
                         if isinstance(n.target, ast.Name) and n.target.id == 'metadata_column')
    assert ast.literal_eval(metadata_loop.iter) == (1, 2, 3)
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == 'setItemDelegateForColumn'
               and len(n.args) == 2
               and isinstance(n.args[1], ast.Call)
               and isinstance(n.args[1].func, ast.Name)
               and n.args[1].func.id == '_ReadOnlyMetadataDelegate'
               for n in ast.walk(metadata_loop))


def test_filename_rename_and_header_sort_resize_are_preserved():
    assert 'tree.setItemDelegateForColumn(0, _InlineRenameDelegate(tree))' in VIEW
    assert 'tree.setItemDelegateForColumn(4, _NavigationChevronDelegate(tree, right_inset=15))' in VIEW
    assert 'tree.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked)' in VIEW
    assert 'tree.header().setSectionsClickable(True)' not in VIEW or 'header.setSectionsClickable(True)' in VIEW
    assert 'header.setSectionsMovable(True)' in VIEW
    assert 'header.sectionResized.connect(self._save_middle_header_state)' in VIEW
    assert 'tree.editItem(item, 0)' in VIEW
    assert 'if column != 0:' in VIEW
