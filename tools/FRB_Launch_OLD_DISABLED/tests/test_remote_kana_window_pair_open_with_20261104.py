"""Regression checks for the 2026-11-04 Remote/Kana window pair and Open With.

The Linux CI runner cannot exercise the Windows z-order or native IME. These
Qt-free tests execute the source methods using small protocol-compatible doubles.
"""
import ast
from enum import IntFlag
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src/launch_remote.py').read_text('utf-8')
APP = (ROOT / 'src/app.py').read_text('utf-8')
KANA = (ROOT / 'experiments/frb_japanese_input/frb_japanese_input.py').read_text('utf-8')
CONNECTOR = (ROOT / 'src/remote_kana_integration.py').read_text('utf-8')
WHEEL = (ROOT / 'src/remote_context_wheel.py').read_text('utf-8')


def actual_method(source, class_name, method_name, scope):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<source method>', 'exec'), scope)
    return scope[method_name]


class F(IntFlag):
    Widget = 0
    FramelessWindowHint = 1
    WindowDoesNotAcceptFocus = 2
    Tool = 4
    WindowStaysOnTopHint = 8
    Window = 16


class P:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __sub__(self, other):
        return P(self.x - other.x, self.y - other.y)
    def __add__(self, other):
        return P(self.x + other.x, self.y + other.y)
    def isNull(self):
        return self.x == self.y == 0
    def __eq__(self, other):
        return isinstance(other, P) and (self.x, self.y) == (other.x, other.y)


def test_kana_header_has_exact_remote_header_height():
    assert 'title_frame.setFixedHeight(30)' in REMOTE
    assert 'title_frame.setFixedHeight(30)' in KANA
    assert 'self.header_keyboard_icon.setFixedSize(25, 24)' in KANA


def test_kana_owned_by_remote_and_front_order_is_remote_then_keyboard():
    assert 'MiniJapaneseInputWindow(parent=self.launcher.remote_window)' in CONNECTOR
    marker = CONNECTOR.index('window.send_button.setToolTip(')
    segment = CONNECTOR[marker: CONNECTOR.index('self.reposition()', marker)]
    assert segment.index('self.launcher.remote_window.set_kana_visible(True)') < segment.index('window.show()') < segment.index('window.raise_()')


def test_kana_visibility_never_promotes_remote_to_topmost_in_normal_mode():
    scope = {'Qt': NS(WindowType=F)}
    sync = actual_method(REMOTE, 'LaunchRemote', 'sync_window_mode', scope)
    class Remote:
        def __init__(self):
            self.parent_obj = NS(dismiss_on_outside_click=False)
            self.flags = F.Window | F.WindowDoesNotAcceptFocus | F.FramelessWindowHint
            self.position = P(100, 120)
            self.visible = True
            self.shows, self.raises = 0, 0
            self._kana_stacking_active = False
            self._window_mode_transition = False
        def parent(self): return self.parent_obj
        def windowFlags(self): return self.flags
        def isVisible(self): return self.visible
        def pos(self): return self.position
        def setWindowFlags(self, flags):
            assert self._window_mode_transition
            self.flags = flags
            self.visible = False  # Qt actually hides on flag changes.
        def move(self, p): self.position = p
        def show(self): self.shows += 1; self.visible = True
        def raise_(self): self.raises += 1
    remote = Remote()
    sync(remote)
    assert not remote.flags & F.WindowStaysOnTopHint
    # When the keyboard opens, its owner's flags must be unchanged.
    set_visible = actual_method(REMOTE, 'LaunchRemote', 'set_kana_visible', scope)
    remote.kana_button = NS(setProperty=lambda *args: None,
                            style=lambda: NS(unpolish=lambda *_: None,
                                             polish=lambda *_: None))
    set_visible(remote, True)
    sync(remote)
    assert not remote.flags & F.WindowStaysOnTopHint
    assert remote.isVisible() and remote.raises == 0
    assert remote._window_mode_transition is False
    assert remote.shows == 0


def test_keyboard_has_no_unconditional_topmost_flag():
    tree = ast.parse(KANA)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MiniJapaneseInputWindow')
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    body_text = ast.get_source_segment(KANA, init)
    assert 'Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)' in body_text
    assert 'Qt.WindowType.WindowStaysOnTopHint' not in body_text


def test_main_launch_drag_moves_remote_only_while_kana_visible():
    scope = {}
    move = actual_method(APP, 'Launcher', 'moveEvent', scope)
    class Base:
        def moveEvent(self, e): self.base_called = True
    # The method uses zero-argument super(); make it callable in real class
    # by compiling a tiny subclass with this exact code, preserving __class__.
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'moveEvent')
    clone = ast.ClassDef(name='TestLauncher', bases=[ast.Name(id='Base', ctx=ast.Load())],
                         keywords=[], body=[method], decorator_list=[])
    namespace = {'Base': Base}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[clone], type_ignores=[])),
                 '<Launcher.moveEvent>', 'exec'), namespace)
    o = namespace['TestLauncher']()
    class Remote:
        def __init__(self): self.position = P(200, 210); self.visible = True
        def isVisible(self): return self.visible
        def pos(self): return self.position
        def move(self, point): self.position = point
    o.remote_window = Remote()
    o._remote_kana_companion = NS(window=NS(isVisible=lambda: True))
    o.remote_15_mode = False
    o.isVisible = lambda: True
    event = NS(pos=lambda: P(120, 115), oldPos=lambda: P(100, 100))
    o.moveEvent(event)
    assert o.remote_window.pos() == P(220, 225)
    assert o.base_called
    o._remote_kana_companion.window.isVisible = lambda: False
    o.moveEvent(event)
    assert o.remote_window.pos() == P(220, 225)  # Free remote unchanged.


def test_remote_open_with_registered_action_payload_contract():
    assert "action.setData(('open_with_app', str(path), application.executable))" in APP
    assert "other.setData(('open_with_dialog', str(path)))" in APP
    assert "self.launcher.open_file_with_selected_app(*args)" in WHEEL
    assert 'self.root.close()' in WHEEL
    assert 'self.launcher.perform_filesystem_context_action(' in WHEEL
