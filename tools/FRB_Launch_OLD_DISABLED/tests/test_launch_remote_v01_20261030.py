"""Remote v0.1 regression tests: pure rules + semantic dispatch without PySide6."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from remote_navigation import next_area, starting_area, popup_position, popup_at_hotspot
from expanded_keyboard_model import row_right_action, root_step


def launcher_method(name):
    tree = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == 'Launcher')
    target = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == name)
    env = {'Qt': SimpleNamespace(FocusReason=SimpleNamespace(OtherFocusReason=1),
                                 ItemDataRole=SimpleNamespace(UserRole=17)),
           'move_tree_selection': Mock(), 'root_step': root_step,
           'row_right_action': row_right_action, 'next_area': next_area,
           'starting_area': starting_area,
           'QTimer': SimpleNamespace(singleShot=lambda delay, callback: None),
           'windows': SimpleNamespace(raise_normal_window=Mock(return_value=True))}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[target],
                        type_ignores=[])), 'app.py', 'exec'), env)
    return env[name], env


def test_focus_ring_wraps_and_respects_view_mode():
    assert next_area('search', expanded=True) == 'pages'
    assert next_area('pages', expanded=True) == 'roots'
    assert next_area('directory', expanded=True) == 'bookmarks'
    assert next_area('bookmarks', expanded=True) == 'search'
    assert next_area('list', expanded=False) == 'search'
    assert next_area('search', expanded=False) == 'pages'
    assert next_area('nonsense', expanded=True) == 'search'


def test_remote_starts_on_current_list_not_search_editor():
    assert starting_area('search', expanded=True) == 'directory'
    assert starting_area('search', expanded=False) == 'list'
    assert starting_area('bookmarks', expanded=True) == 'bookmarks'
    assert starting_area('list', expanded=True) == 'directory'
    assert starting_area('directory', expanded=False) == 'list'


def test_popup_never_runs_off_screen():
    bounds = (0, 0, 800, 600)
    for pointer in ((0, 0), (799, 599), (790, 10), (10, 590), (400, 300)):
        x, y = popup_position(*pointer, 236, 250, *bounds)
        assert 0 <= x <= 564
        assert 0 <= y <= 350
    assert popup_position(400, 300, 236, 250, *bounds) == (414, 314)
    x, y = popup_position(-1900, 800, 236, 250, -1920, 0, 0, 1080)
    assert -1920 <= x <= -236 and 0 <= y <= 830


def test_remote_wheel_pad_is_under_pointer_when_screen_allows():
    # Mouse is inside pad immediately when the popup first appears.
    x, y = popup_at_hotspot(600, 450, 236, 260, 0, 0, 1400, 900, 115, 215)
    assert (x, y) == (485, 235)
    assert (x + 115, y + 215) == (600, 450)
    # Clamp on edges and negative-coordinate second monitor too.
    x, y = popup_at_hotspot(-1890, 12, 236, 260, -1920, 0, 0, 1080, 115, 215)
    assert -1920 <= x <= -236 and 0 <= y <= 820


def fake_launcher(area, expanded):
    window = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
                             _remote_area=area, _last_focus_area='search',
                             hide_remote=Mock(), focus_search=Mock(), raise_=Mock(),
                             activateWindow=Mock(), dismiss_on_outside_click=True,
                             remote_focus_area=Mock(), go_back=Mock(),
                             activate=Mock())
    window.expanded_view = SimpleNamespace(isVisible=lambda: expanded)
    return window


def test_tab_dispatches_to_next_area_without_keyboard_injection():
    dispatch, _ = launcher_method('remote_command')
    window = fake_launcher('files', True)
    dispatch(window, 'TAB')
    window.remote_focus_area.assert_called_once_with('directory')
    window.focus_search.assert_not_called()
    window.hide_remote.assert_not_called()


def test_search_button_returns_focus_to_real_editor_and_closes_remote():
    dispatch, _ = launcher_method('remote_command')
    window = fake_launcher('directory', True)
    dispatch(window, 'SEARCH')
    window.hide_remote.assert_called_once_with()
    window.focus_search.assert_called_once_with()


def test_wheel_navigates_expanded_directory_model_not_windows_keys():
    dispatch, env = launcher_method('remote_command')
    item = SimpleNamespace()
    tree = SimpleNamespace(currentItem=lambda: item)
    window = fake_launcher('directory', True)
    window.expanded_view.middle = SimpleNamespace(tree=tree)
    window.expanded_view.left = SimpleNamespace(tree=SimpleNamespace())
    window.expanded_view.right = SimpleNamespace(tree=SimpleNamespace())
    env['move_tree_selection'].return_value = item
    dispatch(window, 'DOWN')
    dispatch(window, 'UP')
    assert env['move_tree_selection'].call_count == 2
    assert env['move_tree_selection'].call_args_list[0].args == (tree, 1)
    assert env['move_tree_selection'].call_args_list[1].args == (tree, -1)


def test_files_right_descends_and_changes_remote_target():
    dispatch, env = launcher_method('remote_command')
    item = SimpleNamespace()
    row = {'item_kind': 'category', 'title': 'work'}
    files_tree = SimpleNamespace(currentItem=lambda: item)
    view = SimpleNamespace(isVisible=lambda: True,
                           left=SimpleNamespace(tree=files_tree),
                           middle=SimpleNamespace(tree=SimpleNamespace()),
                           right=SimpleNamespace(tree=SimpleNamespace()),
                           row_data=lambda target: row, choose_files=Mock(),
                           navigate_middle=Mock(), enter_row=Mock(),
                           open_cascade=Mock())
    window = fake_launcher('files', True)
    window.expanded_view = view
    dispatch(window, 'RIGHT')
    view.choose_files.assert_called_once_with(item, 0)
    window.remote_focus_area.assert_called_once_with('directory')
    view.navigate_middle.assert_not_called()


def test_directory_right_descends_enter_reuses_existing_action():
    dispatch, _ = launcher_method('remote_command')
    item = SimpleNamespace()
    row = {'item_kind': 'directory', 'title': 'child'}
    view = SimpleNamespace(isVisible=lambda: True,
                           left=SimpleNamespace(tree=SimpleNamespace()),
                           middle=SimpleNamespace(tree=SimpleNamespace(currentItem=lambda: item)),
                           right=SimpleNamespace(tree=SimpleNamespace()),
                           row_data=lambda target: row, choose_files=Mock(),
                           navigate_middle=Mock(), enter_row=Mock(), open_cascade=Mock())
    window = fake_launcher('directory', True)
    window.expanded_view = view
    dispatch(window, 'RIGHT')
    view.navigate_middle.assert_called_once_with(row)
    dispatch(window, 'ENTER')
    view.enter_row.assert_called_once_with(view.middle, item)


def test_original_desktop_behavior_stays_off_by_default():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    assert "'desktop_remote_enabled', 'false'" in source
    assert "self.settings.setValue('desktop_remote_enabled'" in source
    assert "getattr(window, 'remote_on_desktop_double_click', False)" in source
    assert "if reason == 'desktop_first'" in source


def test_remote_uses_semantic_signals_only():
    source = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
    assert 'Signal(str)' in source
    assert 'self.command.emit(' in source
    for forbidden in ('SendKeys(', 'keybd_event(', 'SendInput(', 'QKeyEvent('):
        assert forbidden not in source


def test_enabled_desktop_double_click_opens_remote_once_after_first_focus_pass():
    tree = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    callback = next(n for n in main.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'open_from_desktop')
    tasks = []
    expected = 501
    def fg():
        return expected
    win = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
                          dismiss_on_outside_click=False,
                          remote_on_desktop_double_click=True,
                          raise_=Mock(), activateWindow=Mock(),
                          restore_keyboard_focus=Mock(),
                          isActiveWindow=lambda: True, winId=lambda: 777,
                          show_remote_at=Mock())
    pointer = SimpleNamespace(x=220, y=340, tick=123, view=456)
    env = {'window': win,
           'windows': SimpleNamespace(foreground=fg,
                       desktop_click_still_last_input=lambda tick: tick == 123,
                       raise_normal_window=lambda hwnd: True),
           'QTimer': SimpleNamespace(singleShot=lambda ms, fn: tasks.append((ms, fn))),
           'QPoint': lambda x, y: (x, y),
           'QCursor': SimpleNamespace(pos=lambda: (-1, -1)),
           'DIAG': SimpleNamespace(info=Mock())}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[callback], type_ignores=[])),
                 'app.py', 'exec'), env)
    env['open_from_desktop'](pointer)
    for delay, fn in list(tasks):
        if delay in (0, 120):
            fn()
    win.show_remote_at.assert_called_once_with((220, 340))
    win.restore_keyboard_focus.assert_called()


def test_remote_hide_on_launch_dismissal():
    tree = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == 'dismiss')
    assert isinstance(fn.body[0], ast.Expr)
    call = fn.body[0].value
    assert isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
    assert call.func.attr == 'hide_remote'
