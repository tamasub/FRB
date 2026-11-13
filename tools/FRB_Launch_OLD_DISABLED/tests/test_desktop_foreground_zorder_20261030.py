"""Desktop gesture and non-topmost foreground recovery; no Qt/Windows needed."""
import ast
import ctypes
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import windows
from desktop_double_click import Click, DesktopDoubleClick


def desktop_callback(window, winapi):
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    node = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'open_from_desktop')
    queue = []
    env = dict(window=window, windows=winapi, DIAG=SimpleNamespace(info=Mock()),
               QTimer=SimpleNamespace(singleShot=lambda ms, fn: queue.append((ms, fn))))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'app.py', 'exec'), env)
    return env['open_from_desktop'], queue


def make_window():
    return SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
        dismiss_on_outside_click=False, summon=Mock(), raise_=Mock(),
        activateWindow=Mock(), restore_keyboard_focus=Mock(),
        isActiveWindow=lambda: False, winId=lambda: 303)


def test_verified_desktop_gesture_retries_over_chrome_and_raises_normal_zorder():
    # The Chrome HWND remains foreground throughout the desktop gesture.
    calls = []
    winapi = SimpleNamespace(foreground=lambda: 101,
        desktop_click_still_last_input=lambda tick: calls.append(('guard', tick)) or True,
        raise_normal_window=lambda hwnd: calls.append(('raise', hwnd)) or True)
    window = make_window()
    run, queue = desktop_callback(window, winapi)
    run(Click(200, 200, 5000, 202))
    for delay, fn in queue:
        if delay in (0, 120): fn()
    assert window.restore_keyboard_focus.call_count == 2
    for event in window.restore_keyboard_focus.call_args_list:
        assert event.kwargs['desktop_input_hwnd'] == 202
        assert event.kwargs['restore_current'] is False
    assert calls.count(('guard', 5000)) == 2
    assert calls.count(('raise', 303)) == 2
    window.summon.assert_not_called()


def test_desktop_retry_aborts_on_new_user_input():
    calls = []
    guard = iter([True, False])
    winapi = SimpleNamespace(foreground=lambda: 101,
        desktop_click_still_last_input=lambda tick: next(guard),
        raise_normal_window=lambda hwnd: calls.append(hwnd) or True)
    window = make_window()
    run, queue = desktop_callback(window, winapi)
    run(Click(200, 200, 5000, 202))
    for delay, fn in queue:
        if delay in (0, 120): fn()
    assert window.restore_keyboard_focus.call_count == 1
    assert calls == [303]


def test_desktop_click_verification_passes_original_mouse_metadata():
    received = []
    api = DesktopDoubleClick.__new__(DesktopDoubleClick)
    api.logger = None
    api._empty_wallpaper = lambda x, y, view: True
    api.on_double_click = lambda click: received.append(click)
    click = Click(8, 9, 1024, 202)
    api._verify_and_open(click)
    assert received == [click]


def test_last_input_guard_rejects_new_click_and_preserves_wraparound():
    class FakeUser:
        def __init__(self, time): self.time = time
        def GetLastInputInfo(self, ptr):
            ptr._obj.dwTime = self.time
            return True
    for now, before, expected in ((1000, 1000, True),
                                  (1009, 1000, True),
                                  (1060, 1000, False),
                                  (5, 0xFFFFFFFE, True),
                                  (1000, None, False)):
        with patch.object(windows, 'IS_WINDOWS', True), patch.object(windows, 'user', FakeUser(now), create=True):
            assert windows.desktop_click_still_last_input(before) is expected


def test_zorder_uses_hwnd_top_not_topmost_and_does_not_activate():
    class FakeUser:
        def __init__(self): self.args = None
        def IsWindow(self, hwnd): return hwnd == 303
        def SetWindowPos(self, *args): self.args = args; return True
    u = FakeUser()
    with patch.object(windows, 'IS_WINDOWS', True), patch.object(windows, 'user', u, create=True):
        assert windows.raise_normal_window(303) is True
        assert u.args == (303, 0, 0, 0, 0, 0, 0x13)
        assert windows.raise_normal_window(999) is False


def test_chrome_foreground_can_try_verified_explorer_input_queue():
    class FakeUser:
        def __init__(self):
            self.current = 101
            self.source = None
            self.calls = []
        def IsWindow(self, hwnd): return hwnd in (303, 202)
        def GetForegroundWindow(self): return self.current
        def SetForegroundWindow(self, hwnd):
            self.calls.append(('activate', self.source))
            if self.source == 202:
                self.current = hwnd
                return True
            return False
        def GetWindowThreadProcessId(self, hwnd, out):
            return {101: 800, 202: 900}.get(hwnd, 700)
        def AttachThreadInput(self, own, other, attach):
            self.calls.append(('attach', other, bool(attach)))
            self.source = ({800: 101, 900: 202}.get(other) if attach else None)
            return True
        def BringWindowToTop(self, hwnd): return True
    u = FakeUser()
    with (patch.object(windows, 'IS_WINDOWS', True),
          patch.object(windows, 'user', u, create=True),
          patch.object(windows, 'kernel', SimpleNamespace(GetCurrentThreadId=lambda: 700), create=True)):
        assert windows.activate_keyboard_window(303, expected_foreground=101, input_window=202)
    assert ('attach', 800, True) in u.calls
    assert ('attach', 800, False) in u.calls
    assert ('attach', 900, True) in u.calls
    assert ('attach', 900, False) in u.calls
    assert u.current == 303


def test_foreground_switch_to_unrelated_app_blocks_desktop_attachment():
    class FakeUser:
        def __init__(self): self.calls = []
        def GetForegroundWindow(self): return 404
        def IsWindow(self, hwnd): return True
        def SetForegroundWindow(self, hwnd): self.calls.append(hwnd)
    u = FakeUser()
    with (patch.object(windows, 'IS_WINDOWS', True),
          patch.object(windows, 'user', u, create=True)):
        assert not windows.activate_keyboard_window(303, expected_foreground=101, input_window=202)
    assert not u.calls


def test_desktop_view_can_be_foreground_as_child_or_parent_of_verified_view():
    class FakeUser:
        def IsWindow(self, hwnd): return hwnd == 202
        def GetParent(self, hwnd): return {202: 203, 203: 204, 204: 0}.get(hwnd, 0)
    u = FakeUser()
    for current, expected in ((202, 202), (203, 203), (204, 204), (505, 0)):
        with (patch.object(windows, 'IS_WINDOWS', True),
              patch.object(windows, 'user', u, create=True),
              patch.object(windows, 'foreground', lambda: current)):
            assert windows.verified_desktop_view_foreground(202) == expected


def test_normal_window_blank_click_repairs_zorder_without_suppressing_click():
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == 'NormalWindowClickActivationFilter')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == 'eventFilter')
    class Widget:
        def __init__(self, owner): self.owner = owner
        def window(self): return self.owner
    queue = []
    events = []
    launcher = SimpleNamespace(
        dismiss_on_outside_click=False, isVisible=lambda: True,
        isMinimized=lambda: False, winId=lambda: 303,
        restore_keyboard_focus=lambda *a, **kw: events.append(('focus', a, kw)))
    env = dict(QEvent=SimpleNamespace(Type=SimpleNamespace(MouseButtonPress='press')),
               QWidget=Widget,
               windows=SimpleNamespace(foreground=lambda: 101,
                    raise_normal_window=lambda hwnd: events.append(('zorder', hwnd)) or True),
               DIAG=SimpleNamespace(info=Mock()),
               QTimer=SimpleNamespace(singleShot=lambda delay, fn: queue.append(fn)))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), 'app.py', 'exec'), env)
    filt = SimpleNamespace(launcher=launcher)
    assert env['eventFilter'](filt, Widget(launcher), SimpleNamespace(type=lambda: 'press')) is False
    for fn in queue: fn()
    assert events[0][0] == 'focus'
    assert events[1] == ('zorder', 303)


def test_verified_desktop_parent_forground_is_accepted_without_browser_steal():
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'restore_keyboard_focus')
    allowed = []
    winapi = SimpleNamespace(
        foreground=lambda: 203, desktop_shell_foreground=lambda: 0,
        verified_desktop_view_foreground=lambda view: 203 if view == 202 else 0,
        activate_keyboard_window=lambda hwnd, **kw: allowed.append(kw) or True)
    env = dict(windows=winapi, DIAG=SimpleNamespace(info=Mock()))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), 'app.py', 'exec'), env)
    window = SimpleNamespace(isVisible=lambda: True, menu=None, winId=lambda: 303,
        activateWindow=Mock(), restore_last_current=Mock(), _last_focus_area='files')
    env['restore_keyboard_focus'](window, 101, reason='desktop_retry',
                                  restore_current=False, desktop_input_hwnd=202)
    assert allowed == [{'expected_foreground': (101, 203), 'input_window': 202}]
