"""2026-10-30: Window summon/click focus without PySide6 or Windows."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def method(cls, name):
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    obj = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    return next(node for node in obj.body if isinstance(node, ast.FunctionDef) and node.name == name)


def isolated(node, scope):
    env = dict(scope)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), 'app.py', 'exec'), env)
    return env[node.name]


def desktop_callback(window, fg):
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    node = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'open_from_desktop')
    tasks = []
    run = isolated(node, {'window': window, 'windows': SimpleNamespace(foreground=fg, raise_normal_window=lambda hwnd: True),
                          'DIAG': SimpleNamespace(info=Mock()),
                          'QTimer': SimpleNamespace(singleShot=lambda ms, fn: tasks.append((ms, fn)))})
    return run, tasks


def test_desktop_summon_allows_pre_and_post_raise_foregrounds():
    before_after = iter([101, 202, 202, 202])  # Chrome => Explorer desktop while showing.
    window = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
        dismiss_on_outside_click=False, summon=Mock(), raise_=Mock(),
        activateWindow=Mock(), restore_keyboard_focus=Mock(), isActiveWindow=lambda: False,
        winId=lambda: 303)
    run, tasks = desktop_callback(window, lambda: next(before_after))
    run()
    for delay, fn in tasks:
        if delay in (0, 120): fn()
    assert [v.args[0] for v in window.restore_keyboard_focus.call_args_list] == [(101, 202)] * 2
    assert all(v.kwargs == {'restore_current': False} for v in window.restore_keyboard_focus.call_args_list)
    window.summon.assert_not_called()


def test_desktop_callback_preserves_same_source_foreground_compatibility():
    window = SimpleNamespace(isVisible=lambda: False, isMinimized=lambda: False,
        dismiss_on_outside_click=True, summon=Mock(), raise_=Mock(), activateWindow=Mock(),
        restore_keyboard_focus=Mock(), isActiveWindow=lambda: False)
    run, tasks = desktop_callback(window, lambda: 101)
    run()
    for ms, fn in tasks:
        if ms in (0, 120): fn()
    assert window.restore_keyboard_focus.call_args_list[0].args[0] == 101
    assert window.restore_keyboard_focus.call_args_list[0].kwargs == {'restore_current': True}


def test_desktop_shell_foreground_is_only_allowed_for_explicit_desktop_request():
    records = []
    windows = SimpleNamespace(foreground=lambda: 202, desktop_shell_foreground=lambda: 202,
        activate_keyboard_window=lambda hwnd, expected_foreground: records.append(expected_foreground) or True)
    window = SimpleNamespace(isVisible=lambda: True, menu=None, winId=lambda: 303,
        activateWindow=Mock(), restore_last_current=Mock(), _last_focus_area='files')
    fn = isolated(method('Launcher', 'restore_keyboard_focus'),
                  {'windows': windows, 'DIAG': SimpleNamespace(info=Mock())})
    fn(window, expected_foreground=101, reason='desktop_retry', restore_current=False)
    assert records == [(101, 202)]
    fn(window, expected_foreground=101, reason='normal_window_click', restore_current=False)
    assert records[-1] == 101
    window.restore_last_current.assert_not_called()


def test_desktop_does_not_accept_unrelated_app_as_foreground():
    records = []
    windows = SimpleNamespace(foreground=lambda: 404, desktop_shell_foreground=lambda: 0,
        activate_keyboard_window=lambda hwnd, expected_foreground: records.append(expected_foreground) or False)
    window = SimpleNamespace(isVisible=lambda: True, menu=None, winId=lambda: 303,
        activateWindow=Mock(), restore_last_current=Mock(), _last_focus_area='files')
    fn = isolated(method('Launcher', 'restore_keyboard_focus'),
                  {'windows': windows, 'DIAG': SimpleNamespace(info=Mock())})
    fn(window, expected_foreground=(101, 202), reason='desktop_retry', restore_current=False)
    assert records == [(101, 202)]  # Win32 helper rejects 404.
    window.activateWindow.assert_not_called()


def test_click_any_launcher_child_does_not_eat_original_mouse_event():
    # A global QApplication filter catches blank parts of the embedded Files
    # widget too, not just Launcher.mousePressEvent().
    class Widget:
        def __init__(self, owner): self.owner = owner
        def window(self): return self.owner
    class Other: pass
    qt = SimpleNamespace(Type=SimpleNamespace(MouseButtonPress='press'))
    queue = []
    focus = Mock()
    launcher = SimpleNamespace(dismiss_on_outside_click=False,
        isVisible=lambda: True, isMinimized=lambda: False, winId=lambda: 303,
        restore_keyboard_focus=focus)
    scope = {'QEvent': qt, 'QWidget': Widget,
        'windows': SimpleNamespace(foreground=lambda: 101, raise_normal_window=lambda hwnd: True),
        'DIAG': SimpleNamespace(info=Mock()),
        'QTimer': SimpleNamespace(singleShot=lambda d, f: queue.append((d,f)))}
    click = isolated(method('NormalWindowClickActivationFilter', 'eventFilter'), scope)
    filt = SimpleNamespace(launcher=launcher)
    event = SimpleNamespace(type=lambda: 'press')
    assert click(filt, Widget(launcher), event) is False
    assert queue[0][0] == 0
    queue.pop(0)[1]()
    focus.assert_called_once_with(101, reason='normal_window_click', restore_current=False)
    focus.reset_mock()
    assert click(filt, Widget(Other()), event) is False
    assert queue == []
    launcher.dismiss_on_outside_click = True
    assert click(filt, Widget(launcher), event) is False
    assert queue == []


def test_native_foreground_activation_accepts_safe_samples_not_new_program():
    import sys
    import types
    sys.path.insert(0, str(ROOT / 'src'))
    import windows
    class FakeUser:
        def __init__(self, current): self.current=current; self.calls=[]
        def IsWindow(self, hwnd): return True
        def GetForegroundWindow(self): return self.current
        def SetForegroundWindow(self, hwnd): self.calls.append(hwnd);return False
        def GetWindowThreadProcessId(self, hwnd, unused): return 123
        def AttachThreadInput(self, *args): return False
    for current, accepted in ((101, True), (202, True), (404, False)):
        fake = FakeUser(current)
        with (patch.object(windows,'IS_WINDOWS',True), patch.object(windows,'user',fake,create=True),
              patch.object(windows,'kernel',SimpleNamespace(GetCurrentThreadId=lambda:234),create=True)):
            assert windows.activate_keyboard_window(303, expected_foreground=(101,202)) is False
            assert bool(fake.calls) is accepted


def test_desktop_shell_eligibility_rejects_normal_browser_window():
    import sys
    import ctypes
    sys.path.insert(0, str(ROOT / 'src'))
    import windows
    class FakeUser:
        def __init__(self, name): self.name=name
        def GetForegroundWindow(self): return 202
        def GetClassNameW(self, hwnd, buffer, length):
            buffer.value = self.name
            return len(self.name)
    for name, expected in (('Progman',202), ('WorkerW',202),
                           ('Chrome_WidgetWin_1',0), ('CabinetWClass',0)):
        with patch.object(windows,'IS_WINDOWS',True), patch.object(windows,'user',FakeUser(name),create=True):
            assert windows.desktop_shell_foreground() == expected
