"""Regression: a recreated Qt.Tool column must never be orphaned by a modal dialog.

Controller and mouse-hook wiring are testable without PySide6. Real Qt window
focus and activation require a Windows smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))


def method(name, scope):
    cls = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
    fn = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(SOURCE), 'exec'), scope)
    return scope[name]


def hook_functions(window, modal=None):
    # The factory is in the executable main() flow, NOT the desktop hook itself.
    functions = {}
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name in (
                'launcher_surface_visible', 'dismiss_from_outside_click'):
            functions[node.name] = node
    assert len(functions) == 2
    scope = {'window': window,
             'QApplication': SimpleNamespace(activeModalWidget=lambda: modal),
             'DIAG': Mock()}
    compiled = ast.Module(body=list(functions.values()), type_ignores=[])
    exec(compile(ast.fix_missing_locations(compiled), str(SOURCE), 'exec'), scope)
    return scope


def test_restores_main_tool_window_without_restarting_or_resetting_navigation():
    state = {'visible': False}
    def show(): state['visible'] = True
    launcher = SimpleNamespace(isVisible=lambda: state['visible'],
                               show=Mock(side_effect=show), raise_=Mock(),
                               activateWindow=Mock(), summon=Mock(), render=Mock())
    restore = method('restore_launcher_for_transfer_review', {})
    restore(launcher)
    assert state['visible']
    launcher.show.assert_called_once()
    launcher.raise_.assert_called_once()
    launcher.activateWindow.assert_called_once()
    launcher.summon.assert_not_called()  # summon() would reset the user's folder.
    launcher.render.assert_not_called()
    restore(launcher)
    launcher.show.assert_called_once()  # no unnecessary re-show when already visible


def test_mouse_hook_treats_orphaned_folder_column_as_visible_launcher():
    column = SimpleNamespace(isVisible=lambda: True)
    launcher = SimpleNamespace(isVisible=lambda: False, menu=column,
                               _filesystem_dialog_depth=0, dismiss=Mock())
    functions = hook_functions(launcher)
    assert functions['launcher_surface_visible']() is True
    functions['dismiss_from_outside_click']()
    launcher.dismiss.assert_called_once()


def test_mouse_hook_ignores_outside_click_while_delete_confirmation_active():
    launcher = SimpleNamespace(isVisible=lambda: False,
                               menu=SimpleNamespace(isVisible=lambda: True),
                               _filesystem_dialog_depth=1, dismiss=Mock())
    functions = hook_functions(launcher)
    functions['dismiss_from_outside_click']()
    launcher.dismiss.assert_not_called()
    launcher._filesystem_dialog_depth = 0
    functions = hook_functions(launcher, modal=object())
    functions['dismiss_from_outside_click']()
    launcher.dismiss.assert_not_called()


def test_hook_wiring_uses_same_visibility_check_as_outside_callback():
    source = SOURCE.read_text(encoding='utf-8')
    assert 'is_launcher_visible=launcher_surface_visible' in source
    assert 'if (launcher_surface_visible()' in source
    assert 'self.restore_launcher_for_transfer_review()' in source
