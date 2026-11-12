"""FRB menu ownership contract — no GUI runtime required.

A Files context-menu is the grigri-enabled UI *object*. Neither Exp nor List
may opt in to the Runner separately, or gate it on Remote visibility.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
LAUNCHER = next(c for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
MENU = next(c for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'FRBContextMenu')


def method(name, namespace):
    node = next(n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(namespace)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<extracted method>', 'exec'), ns)
    return ns[name]


class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self):
        for callback in list(self.callbacks):
            callback()


class FakeMenuBase:
    def __init__(self, parent=None, launcher=None):
        self.parent = parent
        self.launcher = launcher
        self.aboutToShow = Signal()
        self.aboutToHide = Signal()
        self.visible = False
        self.actions = []

    def isVisible(self):
        return self.visible

    def popup(self, pos=None):
        self.aboutToShow.emit()
        self.visible = True

    def close(self):
        if self.visible:
            self.visible = False
            self.aboutToHide.emit()


class FakeRunner:
    instances = []

    def __init__(self, launcher, root):
        self.launcher = launcher
        self.root = root
        self.active = True
        self.stops = 0
        self.__class__.instances.append(self)

    def stop(self):
        if self.active:
            self.active = False
            self.stops += 1
            if getattr(self.launcher, '_remote_context_wheel', None) is self:
                self.launcher._remote_context_wheel = None


def harness():
    FakeRunner.instances.clear()
    pending = []
    namespace = {
        'RemoteFolderActionsMenu': FakeMenuBase,
        'RemoteContextWheel': FakeRunner,
        'style_context_menu': lambda menu, theme: None,
        'QTimer': SimpleNamespace(singleShot=lambda milliseconds, callback: pending.append(callback)),
    }
    exec(compile(ast.fix_missing_locations(ast.Module(body=[MENU], type_ignores=[])), '<FRBContextMenu>', 'exec'), namespace)
    menu_class = namespace['FRBContextMenu']
    factory = method('_create_files_context_menu', {'FRBContextMenu': menu_class})
    enable = method('_enable_remote_context_wheel_for_menu', {
        'FRBContextMenu': menu_class, 'RemoteContextWheel': FakeRunner,
    })
    owner = SimpleNamespace(_remote_context_wheel=None, color_theme='light')
    owner._create_files_context_menu = lambda parent=None: factory(owner, parent)
    return SimpleNamespace(cls=menu_class, launcher=owner, pending=pending, factory=factory, enable=enable)


def tick(pending):
    while pending:
        pending.pop(0)()


def test_exp_and_list_are_the_same_menu_class_and_auto_activate_even_without_remote():
    env = harness()
    exp = env.factory(env.launcher)
    list_menu = env.factory(env.launcher)
    assert type(exp) is type(list_menu) is env.cls
    assert exp._frb_files_context_menu and list_menu._frb_files_context_menu
    assert exp.remote_context_root and list_menu.remote_context_root
    assert not hasattr(env.launcher, 'remote_window')  # Never display-gate the Runner.
    exp.popup()
    tick(env.pending)
    first = exp._frb_grigri_runner
    assert first.active and first.root is exp
    assert env.launcher._remote_context_wheel is first
    list_menu.popup()
    tick(env.pending)
    second = list_menu._frb_grigri_runner
    assert not first.active and first.stops == 1
    assert second.active and second.root is list_menu
    assert env.launcher._remote_context_wheel is second
    list_menu.close()
    assert not second.active and second.stops == 1
    assert list_menu._frb_grigri_runner is None
    assert env.launcher._remote_context_wheel is None


def test_menu_owns_single_runner_per_presentation_no_duplicate_hooks_or_leaks():
    env = harness()
    menu = env.factory(env.launcher)
    # Runner hook is installed in the class constructor, before any caller wiring.
    assert len(menu.aboutToShow.callbacks) == 1
    assert len(menu.aboutToHide.callbacks) == 1
    menu.popup()
    tick(env.pending)
    controller = menu._frb_grigri_runner
    assert env.enable(env.launcher, menu) is True
    assert menu._frb_grigri_runner is controller
    assert len(FakeRunner.instances) == 1
    menu.close()
    assert controller.stops == 1
    assert env.enable(env.launcher, menu) is False
    menu.popup()
    tick(env.pending)
    assert len(FakeRunner.instances) == 2
    assert menu._frb_grigri_runner is not controller
    menu.close()
    assert not any(item.active for item in FakeRunner.instances)


def test_popup_closed_before_scheduled_runner_installation_does_not_install_anything():
    env = harness()
    menu = env.factory(env.launcher)
    menu.popup()
    menu.close()
    tick(env.pending)
    assert FakeRunner.instances == []
    assert menu._frb_grigri_runner is None


def test_no_files_context_menu_uses_plain_qmenu_and_runner_is_not_injected_by_callers():
    assert 'menu = FRBContextMenu(parent=parent or self, launcher=self)' in SOURCE
    for name in ('show_files_column_navigation_menu', 'show_launch_root_registration_menu',
                 'show_virtual_launch_context', 'show_expanded_background_paste_menu',
                 'show_launch_context_menu', 'remote_context_menu'):
        node = next(n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef) and n.name == name)
        snippet = ast.get_source_segment(SOURCE, node)
        assert 'menu = QMenu(' not in snippet, name
        assert 'RemoteFolderActionsMenu(' not in snippet, name
    assert 'if not isinstance(menu, FRBContextMenu):' in SOURCE
    assert 'return menu._activate_grigri_runner()' in SOURCE


def test_real_runner_qobject_parent_is_popup_not_launcher():
    source = (Path(__file__).resolve().parents[1] / 'src' / 'remote_context_wheel.py').read_text(encoding='utf-8')
    assert 'super().__init__(menu)' in source
    assert 'super().__init__(launcher)' not in source
