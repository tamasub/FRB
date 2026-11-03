"""Normal and floating Remote share Files target + Browser->Files behavior.

Test real Launcher methods extracted from source so Linux without PySide6
can verify contracts without claiming to test a Windows desktop rendering.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
VIEW = (Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
EXP = (Path(__file__).resolve().parents[1] / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')


def method(source, classname, name):
    root = ast.parse(source)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == classname)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    bare = ast.FunctionDef(name=fn.name, args=fn.args, body=fn.body,
                           decorator_list=[], returns=None, type_comment=None)
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[bare], type_ignores=[])),
                 '<actual source>', 'exec'), scope)
    return scope[name]


def stub(mode, target):
    selections = {'breadcrumb': 'F:/FRB/Launch/src',
                  'exp_branch': ['FRB', 'Launch', 'src'],
                  'list_item': 'app.py'}
    events = []
    view = NS(_workspace_mode=mode, isVisible=lambda: True, **selections)
    app = NS(isVisible=lambda: True, isMinimized=lambda: False,
             expanded_view=view, _remote_preserve_files_selection=False,
             _files_operating_target='directory',
             remote_15_mode=False,
             set_files_operating_target=lambda area: (events.append(('target', area)),
                 setattr(app, '_files_operating_target', area)),
             remote_focus_area=lambda area: events.append(('fallback', area)))

    def show_files_view():
        assert app._remote_preserve_files_selection is True
        view._workspace_mode = 'files'
        events.append(('show_files',))
    view.show_files_view = show_files_view
    return app, view, events, selections


def test_browser_exp_button_returns_to_files_and_targets_exp_without_navigation():
    fn = method(APP, 'Launcher', 'remote_command')
    app, view, events, snapshot = stub('browser', 'files_exp')
    fn(app, 'REMOTE_TARGET_EXP')
    assert view._workspace_mode == 'files'
    assert events == [('show_files',), ('target', 'files_exp')]
    assert app._remote_preserve_files_selection is False
    assert all(getattr(view, key) == value for key, value in snapshot.items())


def test_browser_list_button_returns_to_files_and_targets_list_without_navigation():
    fn = method(APP, 'Launcher', 'remote_command')
    app, view, events, snapshot = stub('browser', 'directory')
    fn(app, 'REMOTE_TARGET_LIST')
    assert view._workspace_mode == 'files'
    assert events == [('show_files',), ('target', 'directory')]
    assert app._remote_preserve_files_selection is False
    assert all(getattr(view, key) == value for key, value in snapshot.items())


def test_direct_target_buttons_do_not_reenter_files_or_navigate():
    fn = method(APP, 'Launcher', 'remote_command')
    app, view, events, snapshot = stub('files', 'files_exp')
    fn(app, 'REMOTE_TARGET_EXP')
    fn(app, 'REMOTE_TARGET_LIST')
    assert events == [('target', 'files_exp'), ('target', 'directory')]
    assert all(getattr(view, key) == value for key, value in snapshot.items())


def test_hidden_view_does_not_switch_target_or_change_workspace():
    fn = method(APP, 'Launcher', 'remote_command')
    app, view, events, snapshot = stub('browser', 'files_exp')
    view.isVisible = lambda: False
    fn(app, 'REMOTE_TARGET_EXP')
    assert events == []
    assert view._workspace_mode == 'browser'


def test_standard_remote_no_longer_gates_arrow_handoff_on_remote_15_mode():
    exp_right = method(APP, 'Launcher', 'remote_exp_right_to_list')
    list_left = method(APP, 'Launcher', 'remote_list_left_to_exp')
    root = ast.parse(APP)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    for name in ('remote_exp_right_to_list', 'remote_list_left_to_exp'):
        node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert 'remote_15_mode' not in ast.unparse(node)
    assert "if not view.isVisible() or view._workspace_mode != 'files':" in APP
    assert 'self._current_remote_files_exp()' in APP
    assert callable(exp_right) and callable(list_left)


def test_normal_and_floating_remote_same_warm_white_color():
    assert "operating_bg = '#FFFEF9' if light" in VIEW
    assert "operating_bg = '#FFFEF9' if theme_family(theme)" in EXP
    assert "operating_title = '#FFF9EF'" in VIEW
    assert "operating_title = '#FFF9EF'" in EXP
