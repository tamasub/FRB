"""Portability and mouse-menu polish regression coverage; no PySide6 required."""
import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text('utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text('utf-8')
SHURIKEN = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
ADAPTER = ROOT / 'src/remote_context_wheel.py'


def isolated_method(method, helpers=None):
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)
    env = dict(helpers or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'isolated', 'exec'), env)
    return env[method]


def test_theme_from_launch_not_reparented_rod():
    assert 'self.pad.launcher = launcher' in REMOTE
    assert "getattr(launcher, 'color_theme', None)" in SHURIKEN
    assert "self._target_preview.present(self, self._target_entries" in REMOTE


def test_hotkey_rebinds_on_native_hwnd_change():
    calls = []
    win = NS(unhotkey=lambda hwnd, key_id=1: calls.append(('remove', hwnd, key_id)),
             hotkey=lambda hwnd, key: calls.append(('register', hwnd, key)))
    method = isolated_method('register_key', {'windows': win, 'DIAG': NS(info=lambda *args: None),
                                               'MENU_HOTKEY_ID_START': 100,
                                               'menu_shortcuts': lambda config: []})
    class Window:
        registered_key = 'Ctrl+Shift+;'
        _registered_hotkey_hwnd = 17
        registered_menu_hotkeys = {}
        data = {'launch_hotkey': 'Ctrl+Shift+;'}
        authored_items = []
        error = Mock()
        winId = lambda self: 25
    window = Window()
    method(window)
    assert ('remove', 17, 1) in calls
    assert ('register', 25, 'Ctrl+Shift+;') in calls
    assert window._registered_hotkey_hwnd == 25
    calls.clear()
    method(window)
    assert not any(cmd == 'register' for cmd, *_ in calls)
    assert 'QTimer.singleShot(0, self._ensure_launcher_hotkey)' in APP


def test_selection_has_send_button_same_confirm_f12():
    assert "QPushButton('送信 (F12)', self.selection_tools)" in APP
    assert 'self.selection_send_button.clicked.connect(self.confirm_selection)' in APP
    assert 'self.selection_send_button.setEnabled(bool(self.selection and self.checked))' in APP
    assert 'self.selection_send_button.setEnabled(bool(self.checked))' in APP
    assert 'if k==Qt.Key.Key_F12:self.confirm_selection();return True' in APP


def test_native_wheel_filter_only_captures_actual_pad():
    pyqt = ModuleType('PySide6')
    core = ModuleType('PySide6.QtCore')
    gui = ModuleType('PySide6.QtGui')
    widgets = ModuleType('PySide6.QtWidgets')
    class Base:
        def __init__(self, *args): pass
    core.QObject = Base
    core.QAbstractNativeEventFilter = Base
    core.QEvent = NS(Type=NS(Wheel=1,MouseButtonPress=2,MouseButtonRelease=3,MouseButtonDblClick=4))
    core.QTimer = NS(singleShot=lambda _, cb: None)
    core.Qt = NS(MouseButton=NS(LeftButton=1))
    gui.QCursor = NS(pos=lambda: 'pad')
    widgets.QApplication = NS(instance=lambda: None)
    old = {name: sys.modules.get(name) for name in
           ('PySide6','PySide6.QtCore','PySide6.QtGui','PySide6.QtWidgets')}
    try:
        for name, mod in (('PySide6',pyqt),('PySide6.QtCore',core),
                          ('PySide6.QtGui',gui),('PySide6.QtWidgets',widgets)):
            sys.modules[name] = mod
        spec=importlib.util.spec_from_file_location('release_wheel_test',ADAPTER)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        menu=NS(isVisible=lambda: True)
        commands=[]
        ctrl=NS(active=True,root=menu,_hit=lambda pos: 'CLICK' if pos=='pad' else None,
                command=lambda cmd: commands.append(cmd))
        handler=m._NativePopupWheel(ctrl)
        m.os=NS(name='nt')
        m.wintypes.MSG=NS(from_address=lambda ptr: NS(message=0x020A,wParam=(120 << 16)))
        assert handler.nativeEventFilter('windows_generic_MSG',77)==(True,0)
        assert commands==['UP']
        m.wintypes.MSG=NS(from_address=lambda ptr: NS(message=0x020B,wParam=(120 << 16)))
        assert handler.nativeEventFilter('windows_generic_MSG',77)==(False,0)
        ctrl._hit=lambda pos: None
        assert handler.nativeEventFilter('windows_generic_MSG',77)==(False,0)
    finally:
        for name, mod in old.items():
            if mod is None: sys.modules.pop(name,None)
            else: sys.modules[name]=mod


def test_native_filter_is_transient_and_no_global_hook():
    text=ADAPTER.read_text('utf-8')
    assert 'installNativeEventFilter(self._native_wheel)' in text
    assert 'removeNativeEventFilter(self._native_wheel)' in text
    assert 'WM_MOUSEWHEEL = 0x020A' in text
    assert 'SetWindowsHookEx' not in text
    assert "point = QCursor.pos()" in text


def test_hotkey_raises_background_launcher_instead_of_dismissing():
    method = isolated_method('summon', {
        'foreground_owned_by_process': lambda: False,
        'windows': NS(foreground=lambda: 33),
    })
    calls = []
    win = NS(busy=False, isMinimized=lambda: False, isVisible=lambda: True,
             show_launcher_normal_or_saved=lambda: calls.append('show'),
             raise_=lambda: calls.append('raise'),
             activateWindow=lambda: calls.append('activate'),
             restore_keyboard_focus=lambda **kwargs: calls.append('focus'),
             dismiss=lambda: calls.append('dismiss'))
    method(win)
    assert calls == ['show','raise','activate','focus']


def test_hotkey_still_toggles_when_launcher_is_foreground():
    method = isolated_method('summon', {
        'foreground_owned_by_process': lambda: True,
    })
    calls=[]
    win=NS(busy=False,isMinimized=lambda:False,isVisible=lambda:True,
           dismiss=lambda:calls.append('dismiss'))
    method(win)
    assert calls==['dismiss']
