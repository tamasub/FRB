"""Normal-window/desktop activation and bookmark one-click regression (no Qt required)."""
import ast
from enum import IntFlag
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]


def isolated_method(cls, name, file='app.py', scope=None):
    tree = ast.parse((ROOT / 'src' / file).read_text(encoding='utf-8'))
    kind = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    fn = next(node for node in kind.body if isinstance(node, ast.FunctionDef) and node.name == name)
    env = dict(scope or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), file, 'exec'), env)
    return env[name]


def desktop_callback(window):
    tree = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    fn = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'open_from_desktop')
    queued = []
    env = {
        'DIAG': SimpleNamespace(info=Mock()),
        'window': window,
        'windows': SimpleNamespace(foreground=lambda: 9876, raise_normal_window=lambda hwnd: True),
        'QTimer': SimpleNamespace(singleShot=lambda delay, action: queued.append((delay, action))),
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'app.py', 'exec'), env)
    return env['open_from_desktop'], queued


def test_desktop_double_click_brings_visible_normal_window_forward_without_dismissal():
    window = SimpleNamespace(
        isVisible=lambda: True, isMinimized=lambda: False,
        dismiss_on_outside_click=False, summon=Mock(),
        raise_=Mock(), activateWindow=Mock(),
        restore_keyboard_focus=Mock(), isActiveWindow=lambda: True, winId=lambda: 300,
    )
    action, callbacks = desktop_callback(window)
    action()
    window.summon.assert_not_called()  # summon() would hide a visible window
    window.raise_.assert_called_once()
    window.activateWindow.assert_called_once()
    for delay, work in callbacks:
        if delay in (0, 120): work()
    assert window.restore_keyboard_focus.call_count == 2
    assert window.restore_keyboard_focus.call_args_list[0].args[:2] == (9876, 'desktop_first')
    assert window.restore_keyboard_focus.call_args_list[1].kwargs == {'restore_current': False}


def test_desktop_double_click_restores_minimized_normal_window_and_hidden_legacy_window():
    for visible, minimized, dismiss in ((True, True, False), (False, False, True)):
        window = SimpleNamespace(
            isVisible=lambda: visible, isMinimized=lambda: minimized,
            dismiss_on_outside_click=dismiss, summon=Mock(),
            raise_=Mock(), activateWindow=Mock(),
            restore_keyboard_focus=Mock(), isActiveWindow=lambda: True, winId=lambda: 300)
        action, callbacks = desktop_callback(window)
        action()
        window.summon.assert_called_once()
        for delay, work in callbacks:
            if delay in (0, 120): work()
        assert window.restore_keyboard_focus.call_count == 2
        assert window.restore_keyboard_focus.call_args_list[0].kwargs == {'restore_current': True}


def test_desktop_double_click_does_not_toggle_visible_legacy_launcher():
    window = SimpleNamespace(
        isVisible=lambda: True, isMinimized=lambda: False,
        dismiss_on_outside_click=True, summon=Mock(),
        raise_=Mock(), activateWindow=Mock(), isActiveWindow=lambda: True)
    action, callbacks = desktop_callback(window)
    action()
    window.summon.assert_not_called()
    window.raise_.assert_not_called()
    assert all(delay == 400 for delay, _ in callbacks)


def test_keyboard_foreground_restore_can_preserve_visible_navigation():
    status = SimpleNamespace(foreground=lambda: 77, activate_keyboard_window=lambda *args, **kwargs: True)
    window = SimpleNamespace(isVisible=lambda: True, menu=None, winId=lambda: 123,
                             activateWindow=Mock(), restore_last_current=Mock(), _last_focus_area='files')
    fn = isolated_method('Launcher', 'restore_keyboard_focus', scope={'windows': status, 'DIAG': SimpleNamespace(info=Mock())})
    fn(window, expected_foreground=77, reason='desktop_first', restore_current=False)
    window.activateWindow.assert_called_once()
    window.restore_last_current.assert_not_called()
    fn(window, expected_foreground=77, reason='desktop_first', restore_current=True)
    window.restore_last_current.assert_called_once()


class WindowType(IntFlag):
    FramelessWindowHint = 1
    Tool = 2
    WindowStaysOnTopHint = 4
    Window = 8


def test_window_modes_are_normal_non_topmost_and_legacy_tool_topmost():
    qt = SimpleNamespace(WindowType=WindowType)
    flags = []
    min_btn = SimpleNamespace(setVisible=Mock())
    wnd = SimpleNamespace(
        dismiss_on_outside_click=False, isVisible=lambda: True,
        isMaximized=lambda: False, pos=lambda: (12, 34), size=lambda: (640, 440),
        setWindowFlags=lambda value: flags.append(value),
        showNormal=Mock(), showMaximized=Mock(), resize=Mock(), move=Mock(),
        minimize_button=min_btn, maximize_button=object(), update_header_icons=Mock(),
        _cloud_link_handoff=False,
    )
    fn = isolated_method('Launcher', '_apply_window_mode', scope={'Qt': qt})
    fn(wnd)
    assert flags[-1] & WindowType.Window
    assert not flags[-1] & WindowType.WindowStaysOnTopHint
    assert not flags[-1] & WindowType.Tool
    wnd.showNormal.assert_called_once()
    min_btn.setVisible.assert_called_with(True)
    wnd.dismiss_on_outside_click = True
    fn(wnd)
    assert flags[-1] & WindowType.Tool
    assert flags[-1] & WindowType.WindowStaysOnTopHint
    min_btn.setVisible.assert_called_with(False)


def test_minimize_only_in_normal_window_mode():
    qt = SimpleNamespace()
    actions = []
    window = SimpleNamespace(
        dismiss_on_outside_click=False,
        hide_history_popup=lambda: actions.append('hide_history'),
        expanded_view=SimpleNamespace(hide_favorite_popup=lambda: actions.append('hide_fav')),
        menu=SimpleNamespace(close=lambda: actions.append('close_menu')),
        isMaximized=lambda: False,
        showMinimized=lambda: actions.append('minimized'),
    )
    fn = isolated_method('Launcher', 'minimize_launcher')
    fn(window)
    assert actions == ['hide_history', 'hide_fav', 'close_menu', 'minimized']
    window.dismiss_on_outside_click = True
    actions.clear()
    fn(window)
    assert actions == []


def test_bookmark_tree_is_one_click_even_in_double_mode():
    row = {'item_kind': 'directory', 'item_id': 'links'}
    calls = []
    node = object()
    tree = object()
    view = SimpleNamespace(row_data=lambda value: row,
                           launcher=SimpleNamespace(folder_open_mode='double'),
                           right=SimpleNamespace(tree=tree),
                           open_cascade=lambda *args: calls.append(args))
    fn = isolated_method('ExpandedLauncherView', 'choose_bookmark', file='expanded_view.py')
    fn(view, node, 0)
    assert calls == [(row, tree, node)]


def test_cascade_bookmarks_are_one_click_not_hover_or_double_click_to_explorer():
    menu = SimpleNamespace(launcher=SimpleNamespace(folder_open_mode='double'), bookmark_navigation=True)
    fn_double_mode = isolated_method('CascadeMenu', '_double_folder_mode')
    fn_manual_mode = isolated_method('CascadeMenu', '_manual_bookmark_mode')
    assert fn_double_mode(menu) is False
    assert fn_manual_mode(menu) is True
    calls = []
    item = object()
    action = object()
    class Event:
        def button(self): return 'left'
        def position(self): return SimpleNamespace(toPoint=lambda: item)
        def accept(self): calls.append('accepted')
    qt = SimpleNamespace(MouseButton=SimpleNamespace(LeftButton='left'))
    menu._manual_bookmark_mode = lambda: True
    menu.actionAt = lambda pos: action
    menu.openers = {action: Mock()}
    menu._folder_row = Mock()
    fn = isolated_method('CascadeMenu', 'mouseDoubleClickEvent', scope={'Qt': qt})
    fn(menu, Event())
    assert calls == ['accepted']
    menu._folder_row.assert_not_called()  # no Explorer execution on second click


def test_compact_bookmark_folder_first_click_keeps_parent_menu_open():
    actions = []
    class Action:
        def data(self): return {'item_kind': 'directory'}
    action = Action()
    point = object()
    event = SimpleNamespace(button=lambda: 'left', position=lambda: SimpleNamespace(toPoint=lambda: point),
                            accept=lambda: actions.append('accept'))
    qt = SimpleNamespace(MouseButton=SimpleNamespace(LeftButton='left'))
    menu = SimpleNamespace(
        order_press=(point, action),
        _bookmark_ignore_double_release=False,
        _folder_double_click_action=None,
        _folder_double_click_row=None,
        _folder_container_row=Mock(return_value=None),
        openers={action: lambda mode: actions.append(('opened', mode))},
        actionAt=lambda pos: action,
        _double_folder_mode=lambda: False,
        _manual_bookmark_mode=lambda: True,
        setActiveAction=lambda a: actions.append('selected'),
        hover_timer=SimpleNamespace(stop=lambda: actions.append('stop')),
    )
    fn = isolated_method('CascadeMenu', 'mouseReleaseEvent', scope={'Qt': qt})
    fn(menu, event)
    assert actions == ['stop', 'selected', ('opened', 'keyboard'), 'accept']
    # A second click's double-click/release must not trigger directory execution.
    menu._bookmark_ignore_double_release = True
    actions.clear()
    fn(menu, event)
    assert actions == ['accept']
    assert menu._bookmark_ignore_double_release is False
