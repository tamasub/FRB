"""Remote current selection and dismissal contracts; headless/no Qt required.

A Windows GUI smoke test is still required for native focus, mouse hook timing.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(APP)
LAUNCHER = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == 'Launcher')
MAIN = next(x for x in TREE.body if isinstance(x, ast.FunctionDef) and x.name == 'main')


def method(class_node, name, env=None):
    env = {} if env is None else env
    node = next(x for x in class_node.body if isinstance(x, ast.FunctionDef) and x.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<method>', 'exec'), env)
    return env[name]


def native_callbacks(window, surface=lambda: True):
    env = {'window':window, 'launcher_surface_visible':surface,
           'QApplication':NS(activeModalWidget=lambda:None), 'DIAG':NS(info=Mock())}
    functions = [x for x in MAIN.body if isinstance(x, ast.FunctionDef) and x.name in
                 ('remote_visible', 'remote_folder_popup_visible', 'remote_page_popup_visible',
                  'dismiss_from_outside_click')]
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])), '<main>', 'exec'), env)
    return env


def test_visible_launcher_live_second_column_survives_remote_summon():
    show = method(LAUNCHER, 'show_remote_at', {'normalize_focus_state':lambda x:x})
    middle = NS(currentItem=lambda:object(), hasFocus=lambda:False, remote_logical_active=False)
    view = NS(isVisible=lambda:True, _workspace_mode='files', middle=NS(tree=middle),
              current_directory=lambda:'/current')
    remote = NS(set_pages=Mock(), apply_theme=Mock(), set_workspace=Mock(),
                show_at=Mock(), focus_cursor_on_files_exp=Mock())
    launcher = NS(remote_on_desktop_double_click=True, isVisible=lambda:True,
                  isMinimized=lambda:False, remote_window=remote, pages=[],
                  color_theme='light', expanded_view=view,
                  _saved_focus_state={'area':'files'}, _last_focus_area='directory',
                  remote_focus_area=Mock(), _remote_popup_area=None)
    show(launcher, 'point')
    launcher.remote_focus_area.assert_called_once_with('directory')
    remote.show_at.assert_called_once_with('point')
    remote.focus_cursor_on_files_exp.assert_called_once_with()
    # If the user has moved back to column 1, stale saved state must not override it.
    launcher._last_focus_area='files'
    launcher._saved_focus_state={'area':'directory','middle_path':'/current'}
    launcher.remote_focus_area.reset_mock()
    show(launcher,'point')
    launcher.remote_focus_area.assert_called_once_with('files')


def test_desktop_click_always_hides_remote_even_in_keep_open_mode():
    for keep_main_open in (True, False):
        remote = NS(isVisible=lambda:True)
        launcher=NS(remote_window=remote, dismiss_on_outside_click=not keep_main_open,
                    hide_remote=Mock(), dismiss=Mock(),
                    _remote_folder_root_menu=None, _remote_folder_opener=None,
                    _remote_page_menu=None)
        env=native_callbacks(launcher)
        assert env['remote_visible']()
        env['dismiss_from_outside_click']()
        launcher.hide_remote.assert_called_once()
        if keep_main_open:
            launcher.dismiss.assert_not_called()
        else:
            launcher.dismiss.assert_called_once()


def test_desktop_click_closes_orphaned_page_popup():
    launcher = NS(remote_window=None, _remote_folder_opener=None,
                  _remote_folder_root_menu=None,
                  _remote_page_menu=NS(isVisible=lambda:True),
                  dismiss_on_outside_click=False,
                  close_remote_folder_menu=Mock(), close_remote_page_menu=Mock(),
                  dismiss=Mock())
    env=native_callbacks(launcher)
    env['dismiss_from_outside_click']()
    launcher.close_remote_page_menu.assert_called_once()
    launcher.close_remote_folder_menu.assert_called_once()
    launcher.dismiss.assert_not_called()


def test_remote_mouse_press_closes_both_types_of_cascades_without_swallowing_click():
    node=next(x for x in TREE.body if isinstance(x, ast.ClassDef)
              and x.name=='CascadeOutsideClickFilter')
    source=ast.get_source_segment(APP, next(x for x in node.body
                                  if isinstance(x, ast.FunctionDef) and x.name=='eventFilter'))
    assert 'launcher.close_remote_folder_menu()' in source
    assert 'launcher.close_remote_page_menu()' in source
    assert "return False" in source
    assert 'obj is remote or remote.isAncestorOf(obj)' in source


def test_native_mouse_hook_checks_remote_even_when_main_is_keep_open():
    main=ast.get_source_segment(APP, MAIN)
    assert 'is_launcher_visible=lambda: (remote_visible()' in main
    assert 'or remote_page_popup_visible()' in main
    assert 'REMOTE_OUTSIDE_CLICK_HIDE' in main
