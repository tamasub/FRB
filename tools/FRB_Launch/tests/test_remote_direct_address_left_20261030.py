"""Direct breadcrumb navigation must retarget a visible FRB Remote.

Extract the shipping methods without importing PySide6 (not available here).
Remote Left and the physical Left must use the same hierarchy navigator.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]


def load_method(filename, class_name, name, namespace):
    module = ast.parse((ROOT / 'src' / filename).read_text(encoding='utf-8'))
    klass = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 filename, 'exec'), namespace)
    return namespace[name]


GOTO = load_method('expanded_view.py', 'ExpandedLauncherView', 'go_to_directory', {
    'normalized_directory': lambda p: p,
    'directory_row': lambda p: {'item_kind': 'directory', 'item_id': p},
})
REMOTE_LEFT = load_method('app.py', 'Launcher', 'remote_command', {
    'starting_area': lambda old, expanded: old,
})


def fake_launcher(*, remote_visible, starting_area='files'):
    remote = NS(isVisible=lambda: remote_visible, set_area=Mock())
    navigator = Mock(return_value='directory')
    view = NS(isVisible=lambda: True, path=[], refresh_middle=Mock(),
              middle=NS(tree=NS()), left=NS(tree=NS()), right=NS(tree=NS()),
              focus_panel=Mock(), navigate_left_from_middle=navigator)
    app = NS(remote_window=remote, expanded_view=view, _remote_area=starting_area,
             _last_focus_area=starting_area, _remote_popup_area=None,
             _remote_mouse_last_click=None, _remote_mouse_menu_click=None,
             isVisible=lambda: True, isMinimized=lambda: False,
             remote_cascade_command=lambda cmd: False)
    def update_remote_area(area):
        app._remote_area = area
        remote.set_area(area)
    app.remote_focus_area = Mock(side_effect=update_remote_area)
    view.launcher = app
    return app, view, navigator


def test_direct_address_updates_visible_remote_to_directory(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda p: True)
    app, view, navigator = fake_launcher(remote_visible=True, starting_area='files')
    address = r'G:\not-registered\child'
    assert GOTO(view, address) is True
    assert view.path == [{'item_kind': 'directory', 'item_id': address}]
    app.remote_focus_area.assert_called_once_with('directory')
    app.remote_window.set_area.assert_called_once_with('directory')
    REMOTE_LEFT(app, 'LEFT')
    navigator.assert_called_once_with()


def test_address_navigation_is_independent_of_remote_initial_area(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda p: True)
    for area in ('pages', 'roots', 'files', 'bookmarks', 'search'):
        app, view, navigator = fake_launcher(remote_visible=True, starting_area=area)
        assert GOTO(view, r'G:\anything') is True
        assert app._remote_area == 'directory'
        REMOTE_LEFT(app, 'LEFT')
        navigator.assert_called_once_with()


def test_hidden_remote_does_not_change_stored_target(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda p: True)
    app, view, _ = fake_launcher(remote_visible=False, starting_area='files')
    assert GOTO(view, r'G:\other') is True
    app.remote_focus_area.assert_not_called()
    assert app._remote_area == 'files'


def test_invalid_address_does_not_change_remote_focus(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda p: False)
    app, view, _ = fake_launcher(remote_visible=True, starting_area='files')
    assert GOTO(view, r'G:\not_there') is False
    app.remote_focus_area.assert_not_called()
    assert view.path == []
