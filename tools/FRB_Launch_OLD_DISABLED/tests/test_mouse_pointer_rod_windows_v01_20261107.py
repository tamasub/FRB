"""Native mouse experiment contracts; Qt/Windows GUI execution is smoke-only."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import mouse_pointer_rod_windows as native


def extract_method(method_name, env):
    tree = ast.parse((ROOT/'src/mouse_pointer_rod.py').read_text('utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == 'MousePointerRodPad')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
              and n.name == method_name)
    scope = dict(env)
    exec(compile(ast.Module(body=[fn],type_ignores=[]), 'mouse_rod_windows', 'exec'), scope)
    return scope[method_name]


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __sub__(self, other):
        return NS(manhattanLength=lambda: abs(self.x-other.x)+abs(self.y-other.y))


class MockCursor:
    position = Point(19, 27)
    travel = []

    @classmethod
    def pos(cls):
        return cls.position

    @classmethod
    def setPos(cls, p):
        cls.travel.append((p.x, p.y))
        cls.position = p


def setup_dispatch(monkeypatch, *, inside_remote=False, screen=True):
    from types import ModuleType
    module = ModuleType('mouse_pointer_rod_windows')
    monkeypatch.setattr(native, "send_left_click", Mock(return_value=True))
    module.click_at = Mock(side_effect=lambda target, *, cursor, double=False: native.click_at(target, cursor=cursor, double=double))
    monkeypatch.setitem(sys.modules, 'mouse_pointer_rod_windows', module)
    MockCursor.position = Point(19,27)
    MockCursor.travel = []
    method = extract_method('_dispatch_windows_click', {
        'QPoint': Point,
        'QCursor': MockCursor,
        'QTimer': NS(singleShot=lambda ms, action: None),
        'QApplication': NS(screenAt=lambda target: object() if screen else None)
    })
    pad = NS(_cursor_on_blue=lambda: True,
             tip_global=lambda: (340.2, 190.8),
             _finish_native_warp=Mock())
    remote = NS(frameGeometry=lambda: NS(contains=lambda target: inside_remote))
    launcher = NS(footer=NS(setText=Mock()))
    return method, pad, remote, launcher, native.send_left_click


def test_single_click_moves_to_tip_sends_one_press_release_and_restores(monkeypatch):
    method,pad,remote,launcher,send = setup_dispatch(monkeypatch)
    assert method(pad, 'select', remote, launcher)
    assert send.call_count == 1
    assert MockCursor.travel == [(340, 191), (19, 27)]
    assert MockCursor.pos().x == 19 and MockCursor.pos().y == 27
    launcher.footer.setText.assert_not_called()


def test_native_double_dispatch_stays_at_tip_for_both_clicks(monkeypatch):
    method,pad,remote,launcher,send = setup_dispatch(monkeypatch)
    monkeypatch.setattr(native.time, 'sleep', Mock())
    assert method(pad, 'double', remote, launcher)
    assert send.call_count == 2
    # Unlike v0.1, a double click moves the cursor exactly once.
    assert MockCursor.travel == [(340,191),(19,27)]
    native.time.sleep.assert_called_once()


def test_when_windows_injection_fails_cursor_is_restored(monkeypatch):
    method,pad,remote,launcher,send = setup_dispatch(monkeypatch)
    send.side_effect = OSError('blocked')
    assert method(pad,'select',remote,launcher) is False
    assert MockCursor.travel == [(340, 191), (19, 27)]
    launcher.footer.setText.assert_called_once()
    assert 'blocked' in launcher.footer.setText.call_args.args[0]


def test_outside_desktop_or_own_remote_is_never_clicked(monkeypatch):
    for kwargs in ({'screen':False}, {'inside_remote':True}):
        method,pad,remote,launcher,send = setup_dispatch(monkeypatch,**kwargs)
        assert not method(pad,'select',remote,launcher)
        assert not send.called
        assert MockCursor.travel == []
    method,pad,remote,launcher,send = setup_dispatch(monkeypatch)
    assert not method(pad,'context',remote,launcher)
    assert not send.called


def test_default_direct_adapter_and_switch_is_explicit(monkeypatch):
    native_adapter = Mock(return_value=True)
    from types import ModuleType
    module=ModuleType('mouse_pointer_rod_direct')
    module.direct_files_action=native_adapter
    monkeypatch.setitem(sys.modules,'mouse_pointer_rod_direct',module)
    dispatch = extract_method('_dispatch_tip_action',{})
    parent = NS(parent=lambda: 'launch')
    obj = NS(_enabled=True,_windows_click_mode=False,
             parentWidget=lambda:parent,
             tip_global=lambda:(11,12),
             _dispatch_windows_click=Mock(return_value=True))
    assert dispatch(obj,'select')
    native_adapter.assert_called_once_with('launch',(11,12),'select')
    obj._windows_click_mode=True
    assert dispatch(obj,'select')
    obj._dispatch_windows_click.assert_called_once_with('select', parent, 'launch')
    assert native_adapter.call_count == 1


def test_windows_native_adapter_rejects_non_windows(monkeypatch):
    monkeypatch.setattr(native.sys,'platform','linux')
    try:
        native.send_left_click()
    except OSError as exc:
        assert 'Windows以外' in str(exc)
    else:
        assert False, 'must never inject outside Windows'


def test_win32_sendinput_is_exactly_one_down_and_up(monkeypatch):
    monkeypatch.setattr(native.sys,'platform','win32')
    class FakeSendInput:
        def __init__(self):
            self.count = 0
            self.flags = ()
        def __call__(self, count, events, structure_size):
            self.count += 1
            self.flags = tuple(events[i].data.mi.dwFlags for i in range(count))
            assert structure_size == native.ctypes.sizeof(native._INPUT)
            return count
    fake=FakeSendInput()
    monkeypatch.setattr(native.ctypes,'WinDLL',lambda *a,**kw:NS(SendInput=fake), raising=False)
    assert native.send_left_click()
    assert fake.count == 1
    assert fake.flags == (native.MOUSEEVENTF_LEFTDOWN,native.MOUSEEVENTF_LEFTUP)


def test_menu_and_remote_contain_independent_switches():
    app=(ROOT/'src/app.py').read_text('utf-8')
    remote=(ROOT/'src/launch_remote.py').read_text('utf-8')
    assert "experiment_mouse_pointer_rod_windows" in app
    # The click adapters are independent in persistence/engine, but a
    # mutually exclusive public submenu now chooses the active adapter.
    assert "self.mouse_pointer_rod_choice_group.setExclusive(True)" in app
    assert "self.mouse_pointer_rod_windows_action = self.mouse_pointer_rod_choice_actions['windows']" in app
    assert 'self.mouse_pointer_rod_smart_action = None' in app
    assert 'def set_mouse_pointer_rod_windows_mode(self, enabled):' in remote
    assert 'self.pointer_rod.set_windows_click_mode(enabled)' in remote
    assert 'if self._windows_click_mode:' in (ROOT/'src/mouse_pointer_rod.py').read_text('utf-8')
