"""Release-level contracts for folder Enter and hybrid context wheels.

Qt-free checks execute the real Files List/Exp handlers, so this file is
runnable without Windows or PySide6. Win11 input routing still needs a smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text('utf-8')
EXP = (ROOT / 'src' / 'remote_files_explorer.py').read_text('utf-8')


def extract(source, owner, method, scope):
    parsed = ast.parse(source)
    cls = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == owner)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<extracted>', 'exec'), scope)
    return scope[method]


def test_list_enter_folder_descends_inside_list_without_external_execution():
    qt = NS(State=NS(EditingState='editing'))
    go = extract(VIEW, 'ExpandedLauncherView', 'enter_row', {'QAbstractItemView': qt})
    tree = NS(_rename_enter_guard=False, state=lambda: 'idle')
    middle = NS(tree=tree)
    row = {'item_kind': 'directory', 'item_id': 'folder123'}
    view = NS(middle=middle, left=object(), row_data=lambda item: row,
              navigate_middle=Mock(), launcher=NS(execute=Mock(), activate=Mock()))
    go(view, middle, object())
    view.navigate_middle.assert_called_once_with(row)
    view.launcher.execute.assert_not_called()
    view.launcher.activate.assert_not_called()


def test_list_enter_file_still_opens_file_not_directory():
    qt = NS(State=NS(EditingState='editing'))
    go = extract(VIEW, 'ExpandedLauncherView', 'enter_row', {'QAbstractItemView': qt})
    middle = NS(tree=NS(_rename_enter_guard=False, state=lambda: 'idle'))
    row = {'item_kind': 'file', 'item_id': 'file123'}
    view = NS(middle=middle, row_data=lambda item: row,
              navigate_middle=Mock(), launcher=NS(activate=Mock(), execute=Mock()))
    go(view, middle, object())
    view.launcher.activate.assert_called_once_with(row)
    view.navigate_middle.assert_not_called()
    view.launcher.execute.assert_not_called()


def test_list_enter_does_not_navigate_during_inline_rename():
    qt = NS(State=NS(EditingState='editing'))
    go = extract(VIEW, 'ExpandedLauncherView', 'enter_row', {'QAbstractItemView': qt})
    tree = NS(_rename_enter_guard=True, state=lambda: 'idle')
    middle = NS(tree=tree)
    view = NS(middle=middle, row_data=lambda item: {'item_kind': 'directory'},
              navigate_middle=Mock(), launcher=NS(activate=Mock(), execute=Mock()))
    go(view, middle, object())
    view.navigate_middle.assert_not_called()
    tree._rename_enter_guard = False
    tree.state = lambda: 'editing'
    go(view, middle, object())
    view.navigate_middle.assert_not_called()


def test_exp_enter_uses_existing_branch_activation_not_list_focus():
    qt = NS(Key=NS(Key_Return=5, Key_Enter=6, Key_Right=7),
            KeyboardModifier=NS(NoModifier=0))
    go = extract(EXP, 'FilesExpWheelTree', 'keyPressEvent',
                 {'Qt': qt, 'QAbstractItemView': NS(State=NS(EditingState='editing'))})
    panel = NS(_rename_in_progress=None, remote_activate_current=Mock(return_value=True))
    tree = NS(parentWidget=lambda: panel, state=lambda: 'idle')
    key = NS(key=lambda: 5, modifiers=lambda: 0, accept=Mock())
    go(tree, key)
    panel.remote_activate_current.assert_called_once_with()
    key.accept.assert_called_once_with()
