"""Regression: authored-JSON Qt.Tool QMenus must not survive action completion.

This unit test models QAction/QMenu signals without requiring Windows/PySide6;
real Win11 right-click, wheel and outside click still need device acceptance.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def _method(name):
    tree = ast.parse(APP)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                    and n.name == 'Launcher')
    fn = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
              and n.name == name)
    namespace = {'QTimer': FakeTimer}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 'Launcher.' + name, 'exec'), namespace)
    return namespace[name]


class FakeTimer:
    pending = []

    @classmethod
    def singleShot(cls, delay, callback):
        cls.pending.append((delay, callback))

    @classmethod
    def flush(cls):
        scheduled, cls.pending = sorted(cls.pending, key=lambda entry: entry[0]), []
        for _, callback in scheduled:
            callback()


class Signal:
    def __init__(self):
        self.handlers = []

    def connect(self, callback):
        self.handlers.append(callback)

    def emit(self, *args):
        for handler in tuple(self.handlers):
            handler(*args)


class FakeMenu:
    def __init__(self):
        self.aboutToHide = Signal()
        self.triggered = Signal()
        self.visible = False
        self.deleted = False
        self.popup_calls = []
        self.close_calls = 0

    def popup(self, point):
        self.popup_calls.append(point)
        self.visible = True

    def exec(self, *_):
        raise AssertionError('Qt.Tool menu must not call QMenu.exec()')

    def close(self):
        self.close_calls += 1
        if self.visible:
            self.visible = False
            self.aboutToHide.emit()

    def deleteLater(self):
        self.deleted = True


class FakeAction:
    def __init__(self, submenu=None):
        self.submenu = submenu

    def menu(self):
        return self.submenu


def make_launcher():
    launcher = SimpleNamespace(_launch_context_menu=None, wired=[], remote_added=[])
    launcher._forget_launch_context_menu = lambda menu: (
        setattr(launcher, '_launch_context_menu', None)
        if launcher._launch_context_menu is menu else None)
    launcher._wire_hybrid_context_menu = launcher.wired.append
    launcher._prepend_remote_pad_navigation = launcher.remote_added.append
    launcher._show_launch_json_context_popup = lambda menu, point, remote_pad=False: (
        _method('_show_launch_json_context_popup')(
            launcher, menu, point, remote_pad=remote_pad))
    return launcher


def test_native_action_closes_and_releases_json_context_menu():
    launcher = make_launcher()
    menu = FakeMenu()
    launcher._show_launch_json_context_popup(menu, 'point')
    assert menu.popup_calls == ['point']
    assert launcher._launch_context_menu is menu
    assert launcher.wired == [menu]
    assert not menu.deleted
    menu.triggered.emit(FakeAction())
    assert not menu.visible
    assert not menu.deleted  # wheel QAction.trigger() may still be pending
    assert launcher._launch_context_menu is None
    FakeTimer.flush()
    assert menu.deleted


def test_submenu_preview_does_not_close_parent_but_leaf_does():
    launcher = make_launcher()
    menu = FakeMenu()
    launcher._show_launch_json_context_popup(menu, 'position', remote_pad=True)
    assert launcher.remote_added == [menu]
    menu.triggered.emit(FakeAction(submenu=object()))
    assert menu.visible
    menu.triggered.emit(FakeAction())
    assert not menu.visible


def test_next_rightclick_closes_previous_menu_only():
    launcher = make_launcher()
    first, second = FakeMenu(), FakeMenu()
    launcher._show_launch_json_context_popup(first, 'first')
    launcher._show_launch_json_context_popup(second, 'second')
    assert first.close_calls == 1
    assert not first.deleted
    assert launcher._launch_context_menu is second
    FakeTimer.flush()
    assert first.deleted
    assert second.visible


def test_both_json_context_entrypoints_use_nonblocking_popup():
    launcher_tree = ast.parse(APP)
    launcher = next(n for n in launcher_tree.body if isinstance(n, ast.ClassDef)
                    and n.name == 'Launcher')
    for name in ('show_virtual_launch_context', 'show_launch_root_registration_menu'):
        fn = next(n for n in launcher.body if isinstance(n, ast.FunctionDef)
                  and n.name == name)
        calls = [node for node in ast.walk(fn) if isinstance(node, ast.Call)]
        assert any(isinstance(call.func, ast.Attribute)
                   and call.func.attr == '_show_launch_json_context_popup'
                   for call in calls), name
        assert not any(isinstance(call.func, ast.Attribute)
                       and call.func.attr == 'exec'
                       for call in calls), name


def test_deferred_wheel_action_fires_before_menu_disposal():
    launcher = make_launcher()
    menu = FakeMenu()
    launcher._show_launch_json_context_popup(menu, 'point')
    triggered = []
    # The real wheel controller closes the popup then queues QAction.trigger.
    menu.close()
    FakeTimer.singleShot(0, lambda: triggered.append('activated'))
    assert triggered == [] and not menu.deleted
    FakeTimer.flush()
    assert triggered == ['activated'] and menu.deleted
