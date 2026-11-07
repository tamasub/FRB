"""Crash regression: native Qt may delete CascadeMenu before Remote callback.

These tests run without PySide6 so Windows/GUI machines are not required.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def _method(name):
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    code = compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                   f'<Launcher.{name}>', 'exec')
    scope = {}
    exec(code, scope)
    return scope[name]


class DeletedMenu:
    """Live Python wrapper for a C++ QMenu that was already destroyed."""
    def isVisible(self):
        raise RuntimeError('Internal C++ object (CascadeMenu) already deleted.')
    def close(self):
        raise RuntimeError('Internal C++ object (CascadeMenu) already deleted.')


def _purge(window, menu_token):
    _method('_on_remote_page_menu_destroyed')(window, menu_token)


def test_remote_click_does_not_crash_on_deleted_page_menu():
    dead = DeletedMenu()
    window = NS(expanded_view=NS(isVisible=lambda: False),
                _remote_page_menu=dead, menu=dead,
                _on_remote_page_menu_destroyed=lambda token: _purge(window, token),
                _remote_area='pages', _last_focus_area='pages',
                _remote_popup_area=None, remote_15_mode=False,
                _remote_mouse_last_click=None,
                remote_cascade_command=lambda command: False)
    click = _method('remote_mouse_click')
    click(window, double=False)
    assert window._remote_page_menu is None
    assert window.menu is None
    # It must stay safe on repeated events, including native double clicks.
    click(window, double=True)


def test_remote_page_command_path_is_defensively_guarded_twice():
    click = _method('remote_mouse_click')
    command = _method('remote_command')
    assert click is not None and command is not None
    assert APP.count('remote_page_visible = remote_page is not None and remote_page.isVisible()') == 2
    assert APP.count('self._on_remote_page_menu_destroyed(id(remote_page))') == 2


def test_native_destroyed_slot_drops_only_the_matching_refs():
    first, newer = object(), object()
    window = NS(_remote_page_menu=first, menu=first)
    _purge(window, id(first))
    assert window._remote_page_menu is None and window.menu is None
    window._remote_page_menu = newer
    window.menu = newer
    _purge(window, id(first))  # Late callback from an earlier menu
    assert window._remote_page_menu is newer and window.menu is newer


def test_closing_an_already_deleted_page_is_safe_and_clears_reference():
    dead = DeletedMenu()
    window = NS(_remote_page_menu=dead, menu=dead)
    _method('close_remote_page_menu')(window)
    assert window._remote_page_menu is None and window.menu is None
    _method('close_remote_page_menu')(window)


def test_remote_cascade_dispatch_skips_deleted_native_menu():
    dead = DeletedMenu()
    window = NS(menu=dead, _remote_page_menu=dead,
                _on_remote_page_menu_destroyed=lambda token: _purge(window, token))
    assert _method('remote_cascade_command')(window, 'CLICK') is False
    assert window.menu is None and window._remote_page_menu is None


def test_remote_page_registrations_and_cascade_replacement_manage_lifetime():
    assert APP.count('menu.destroyed.connect(') >= 2
    assert 'if previous is getattr(self, \'_remote_page_menu\', None)' in APP
    assert 'self.close_remote_page_menu()' in APP


def test_corner_indicator_coordinates_support_sibling_widgets():
    # files_content_stack and root_widget have different parents. Calling
    # QWidget.mapTo(target_sibling, ...) emitted the observed Qt warning.
    assert 'self.root_widget.mapFromGlobal(' in EXP
    assert 'self.files_content_stack.mapToGlobal(' in EXP
    assert 'self.files_content_stack.mapTo(\n                         self.root_widget,' not in EXP
