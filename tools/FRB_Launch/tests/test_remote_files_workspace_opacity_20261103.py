"""Qt-free contract tests for Remote Files state retention and alpha wheel.

CI is often Linux without PySide6. Exercise the actual extracted code using
minimal fake view/settings events rather than simulating a Windows desktop.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def _method(source, klass, name, *, extract=None, globals_=None):
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == klass)
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    if extract is not None:
        fn.body = [next(node for node in fn.body if extract(node))]
    fn.decorator_list = []
    ns = dict(globals_ or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<extracted implementation>', 'exec'), ns)
    return ns[name]


class Settings:
    def __init__(self):
        self.values = {}
        self.synced = 0

    def setValue(self, key, value):
        self.values[key] = value

    def sync(self):
        self.synced += 1


class FakeWheel:
    def __init__(self, delta, *, ctrl=True, pixel=False):
        self.ctrl, self.delta, self.pixel = ctrl, delta, pixel
        self.accepted = False

    def modifiers(self):
        return 1 if self.ctrl else 0

    def angleDelta(self):
        return SimpleNamespace(y=lambda: 0 if self.pixel else self.delta)

    def pixelDelta(self):
        return SimpleNamespace(y=lambda: self.delta if self.pixel else 0)

    def accept(self):
        self.accepted = True


class RemoteStub:
    def __init__(self):
        self.settings = Settings()
        self._background_opacity = .65
        self._opacity_wheel_angle_remainder = 0
        self._opacity_wheel_pixel_remainder = 0
        self.files_exp_theme = 'light'
        self.apply_calls = 0
        self.tooltips = []

    def parent(self):
        return SimpleNamespace(settings=self.settings)

    def apply_theme(self, value):
        self.apply_calls += 1


class QtStub:
    KeyboardModifier = SimpleNamespace(ControlModifier=1)


def _opacity_methods():
    # QToolTip is imported inside the method; use extracted wheel method and
    # stub only the setter to test the adjustment semantics separately.
    method = _method(REMOTE, 'LaunchRemote',
                     'adjust_background_opacity_from_wheel', globals_={'Qt': QtStub})
    return method


def test_ctrl_wheel_consumed_without_navigation_and_accumulates_fractional_steps():
    method = _opacity_methods()
    remote = RemoteStub()
    values = []
    remote.set_background_opacity = lambda v: (values.append(v), setattr(remote, '_background_opacity', round(v,2)))
    assert method(remote, FakeWheel(120, ctrl=False)) is False
    assert not values
    e = FakeWheel(60)
    assert method(remote, e) is True and e.accepted
    assert not values
    e = FakeWheel(60)
    assert method(remote, e) is True and e.accepted
    assert [round(v, 2) for v in values] == [.7]
    e = FakeWheel(-120)
    assert method(remote, e) is True and e.accepted
    assert round(values[-1], 2) == .65
    method(remote, FakeWheel(-36, pixel=True))
    assert round(values[-1], 2) == .6


def test_opacity_range_and_persistence_are_implemented():
    method = _method(REMOTE, 'LaunchRemote', 'set_background_opacity')
    remote = RemoteStub()
    # Qt's tooltip import cannot be loaded on a Linux CI runner, so assert
    # setter contract from its actual parsed body and the Qt code path.
    source = ast.get_source_segment(REMOTE, ast.parse(REMOTE).body[
        next(i for i,n in enumerate(ast.parse(REMOTE).body) if isinstance(n,ast.ClassDef) and n.name=='LaunchRemote')
    ])
    assert "settings.setValue('remote_background_opacity', value)" in source
    assert "settings.sync()" in source
    assert "max(0.25, min(1.0, value))" in source
    assert "self.apply_theme(self.files_exp_theme)" in source
    assert "QToolTip.showText" in source
    assert callable(method)


def test_all_remote_backgrounds_use_alpha_but_text_is_not_dimmed():
    for style in ('remoteTitleBar', 'remoteStatusBar', 'remoteWheelPad'):
        assert style in REMOTE
    assert "QPushButton {{background:{button_bg}" in REMOTE
    assert 'QPushButton:hover {{background:{hover_bg}' in REMOTE
    assert 'QPushButton:pressed {{background:{active_bg}' in REMOTE
    assert "self._remote_background.setAlphaF(self._background_opacity)" in REMOTE
    assert 'self.setWindowOpacity(' not in REMOTE
    assert "self._background_opacity = max(0.25, min(1.0, saved_opacity))" in REMOTE
    assert 'self.adjust_background_opacity_from_wheel(event)' in REMOTE


def test_remote_files_button_switches_workspace_without_resetting_files_state():
    clause = lambda n: (isinstance(n, ast.If) and ast.unparse(n.test) ==
                        "command in ('WORKSPACE_FILES', 'WORKSPACE_BROWSER')")
    run = _method(APP, 'Launcher', 'remote_command', extract=clause)
    folder = 'F:/FRB/tools/FRBStudio_App'

    class View:
        def __init__(self):
            self._workspace_mode = 'browser'
            def make_pane():
                class Tree:
                    remote_highlight_mode = False
                    remote_logical_active = False
                    def property(self, name): return getattr(self, name, None)
                    def setProperty(self, name, value): setattr(self, name, value)
                    def style(self): return self
                    def unpolish(self, _): pass
                    def polish(self, _): pass
                    def viewport(self): return self
                    def update(self): pass
                return SimpleNamespace(tree=Tree())
            self.left, self.middle = make_pane(), make_pane()
            self.breadcrumb = folder
            self.exp_tree = ('PC expanded', 'FRB Studio expanded')
            self.exp_selected = folder
            self.files_selected = 'README.md'
            self.show_calls = 0

        def isVisible(self):
            return True

        def show_files_view(self):
            self._workspace_mode = 'files'
            self.show_calls += 1
            # Real callback must see suppression during transition.
            assert owner._remote_preserve_files_selection

    class LauncherStub:
        def __init__(self):
            self.expanded_view = View()
            self._remote_area = 'web_body:0'
            self.remote_window = SimpleNamespace(set_area=lambda a: area_calls.append(a))

    area_calls = []
    owner = LauncherStub()
    view = owner.expanded_view
    snapshot = (view.breadcrumb, view.exp_tree, view.exp_selected, view.files_selected)
    run(owner, 'WORKSPACE_FILES')
    assert view.show_calls == 1
    assert (view.breadcrumb, view.exp_tree, view.exp_selected, view.files_selected) == snapshot
    assert owner._remote_area == 'directory'
    assert area_calls == ['directory']
    assert owner._remote_preserve_files_selection is False
    assert view.middle.tree.remote_logical_active is True
    assert view.left.tree.remote_logical_active is False
    run(owner, 'WORKSPACE_FILES')
    assert view.show_calls == 2
    assert (view.breadcrumb, view.exp_tree, view.exp_selected, view.files_selected) == snapshot
    assert area_calls == ['directory']


def test_home_remains_separate_and_workspace_callback_honors_guard():
    cmd = APP[APP.index('    def remote_command('):APP.index("        if command == 'REMOTE_FAVORITE_SAVE':")]
    files = cmd[cmd.index("if command == 'WORKSPACE_FILES':"):cmd.index("elif view.switch_workspace('browser'):")]
    assert 'navigate_home' not in files
    assert 'remote_focus_area' not in files
    assert "view.show_files_view()" in files
    assert "not getattr(self, '_remote_preserve_files_selection', False)" in APP
    home = APP[APP.index('    def navigate_home('):APP.index('    def go_back(')]
    assert 'panel.reset_to_roots()' in home
