"""Regression contract for the reversible, floating column-1.5 experiment.

Pure behavioral tests: this CI environment has no PySide6/Windows compositor.
Extract the actual implementation so test doubles exercise its branches.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)


def actual_method(source, name):
    module = ast.parse(source)
    launcher = next(node for node in module.body if isinstance(node, ast.ClassDef)
                    and node.name == ('Launcher' if source is APP else
                                      'ExpandedLauncherView'))
    method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == name)
    bare = ast.FunctionDef(name=method.name, args=method.args, body=method.body,
                           decorator_list=[], returns=None, type_comment=None)
    namespace = {'QPoint': Point}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[bare], type_ignores=[])),
                 '<actual-method>', 'exec'), namespace)
    return namespace[name]


class Remote:
    def __init__(self, visible=False):
        self.visible = visible
        self.position = Point(-1, -1)
        self.raised = 0
        self._remote_15_placement = False
        self.area = None
    def isVisible(self): return self.visible
    def sync_window_mode(self): pass
    def set_pages(self, pages): self.pages = pages
    def apply_theme(self, theme): self.theme = theme
    def set_workspace(self, mode): self.workspace = mode
    def set_area(self, area): self.area = area
    def pos(self): return self.position
    def width(self): return 184
    def move(self, pos): self.position = pos
    def show(self): self.visible = True
    def raise_(self): self.raised += 1


class Lane:
    def __init__(self, visible=True): self.visible = visible
    def isVisible(self): return self.visible
    def width(self): return 196
    def mapToGlobal(self, local): return Point(300 + local.x, 100 + local.y)


def build(*, visible=False, anchor_visible=True, needs_show=True, with_remote=True):
    remote = Remote(visible) if with_remote else None
    lane = Lane(anchor_visible)
    view = SimpleNamespace(_workspace_mode='files',
                           remote_15_lane=lane,
                           isVisible=lambda: anchor_visible)
    app = SimpleNamespace(remote_15_mode=True, expanded_view=view,
                          isVisible=lambda: True, isMinimized=lambda: False,
                          remote_window=remote, pages=['work'], color_theme='light',
                          _remote_area='directory', _remote_15_needs_show=needs_show,
                          _remote_15_alignment_pending=True,
                          pos=lambda: Point(100, 70))
    if not with_remote:
        def create():
            app.remote_window = Remote()
            return app.remote_window
        app.ensure_remote_window = create
    return app


def test_floating_remote_is_visible_over_files_and_does_not_reparent():
    app = build(with_remote=False)
    actual_method(APP, '_align_remote_15_now')(app)
    assert app.remote_window.visible
    assert app.remote_window.position == Point(306, 104)
    assert app.remote_window.raised == 1
    assert app.remote_window.area == 'directory'
    assert app.remote_window._remote_15_placement


def test_user_closed_remote_stays_closed_during_geometry_changes():
    app = build(visible=False, needs_show=False)
    actual_method(APP, '_align_remote_15_now')(app)
    assert not app.remote_window.visible
    assert app.remote_window.raised == 0


def test_hidden_files_canvas_global_search_preserves_remote_and_anchor():
    app = build(visible=True, anchor_visible=False, needs_show=False)
    app._remote_15_offset = Point(206, 34)
    actual_method(APP, '_align_remote_15_now')(app)
    assert app.remote_window.position == Point(306, 104)
    assert app.remote_window.visible
    assert app.remote_window.raised == 1


def test_background_browser_mode_does_not_reposition_or_create_remote():
    app = build(visible=True, needs_show=False)
    app.expanded_view._workspace_mode = 'browser'
    actual_method(APP, '_align_remote_15_now')(app)
    assert app.remote_window.position == Point(-1, -1)


def test_existing_search_result_execution_is_not_replaced():
    assert "if command == 'SEARCH_RESULT_DOUBLE_CLICK':" in APP
    assert 'self.remote_search_result_double_click()' in APP
    assert "if command == 'SEARCH_HISTORY':" in APP or "'SEARCH_HISTORY'" in APP
    assert 'self.activate(row)' in APP


def test_native_tool_is_not_embedded_into_reserved_splitter():
    assert "self.remote_15_lane = QFrame(self.files_first_host)" in VIEW
    assert 'first_host_row.addWidget(self.remote_15_lane, 0)' in VIEW
    assert 'self.files_splitter.addWidget(self.files_first_host)' in VIEW
    assert 'self.files_splitter.addWidget(self.middle)' in VIEW
    assert 'self.files_splitter.addWidget(remote)' not in VIEW
    assert 'super().__init__(launcher, flags)' in REMOTE
    assert 'Qt.WindowType.Tool' in REMOTE


def test_cross_mode_state_and_saved_manual_position_are_protected():
    assert "'experiment_remote_15_column'" in APP
    assert "'workspace_files_remote_15_splitter_sizes'" in VIEW
    assert 'not self._remote_15_placement' in REMOTE
    assert 'if self.remote_15_mode:' in APP


def test_remote_close_and_reopen_are_explicit_actions():
    assert "if command == 'CLOSE':\n            self.hide_remote()" in APP
    assert 'self.queue_remote_15_alignment(show=True)' in APP
    assert 'if not show and (remote is None or not remote.isVisible()):' in APP

class Widget:
    def __init__(self, visible=False): self.visible=visible
    def show(self): self.visible=True
    def hide(self): self.visible=False
    def setVisible(self, value): self.visible=bool(value)

class Splitter:
    def __init__(self, sizes): self.widths=sizes[:]
    def sizes(self): return self.widths[:]
    def setSizes(self, widths):
        assert len(widths)==2, 'legacy splitter must remain two panels'
        self.widths=widths[:]

class Settings:
    def __init__(self, record=None): self.record=record or {}
    def value(self, key, default=''): return self.record.get(key, default)


def test_column_15_toggle_preserves_original_two_splitter_sizes():
    launcher = SimpleNamespace(remote_15_mode=True, files_root_hidden_mode=False,
                               files_exp_embedded_mode=True, settings=Settings(),
                               queue_remote_15_alignment=lambda: None)
    splitter = Splitter([300, 700])
    view = SimpleNamespace(launcher=launcher, remote_15_lane=Widget(),
                           files_first_host=Widget(True), files_splitter=splitter)
    actual_method(VIEW,'apply_remote_15_lane_mode')(view)
    assert view.remote_15_lane.visible
    assert splitter.sizes()==[496, 504]
    launcher.remote_15_mode=False
    actual_method(VIEW,'apply_remote_15_lane_mode')(view)
    assert splitter.sizes()==[300,700]
    assert not view.remote_15_lane.visible


def test_mode_restore_uses_separate_1_5_column_state():
    settings=Settings({'workspace_files_remote_15_splitter_sizes':'515|485',
                       'workspace_files_exp_embedded_splitter_sizes':'300|700'})
    launcher=SimpleNamespace(remote_15_mode=True, files_root_hidden_mode=False,
                             files_exp_embedded_mode=True, settings=settings,
                             queue_remote_15_alignment=lambda: None)
    view=SimpleNamespace(launcher=launcher, remote_15_lane=Widget(),
                         files_first_host=Widget(True), files_splitter=Splitter([300,700]))
    actual_method(VIEW,'apply_remote_15_lane_mode')(view)
    assert view.files_splitter.sizes()==[515,485]
    assert settings.record['workspace_files_exp_embedded_splitter_sizes']=='300|700'


def test_close_rollback_keeps_legacy_hidden_first_column_hidden():
    launcher=SimpleNamespace(remote_15_mode=True, files_root_hidden_mode=True,
                             files_exp_embedded_mode=False, settings=Settings(),
                             queue_remote_15_alignment=lambda: None)
    view=SimpleNamespace(launcher=launcher, remote_15_lane=Widget(),
                         files_first_host=Widget(), files_splitter=Splitter([0,1000]))
    actual_method(VIEW,'apply_remote_15_lane_mode')(view)
    assert view.files_first_host.visible
    launcher.remote_15_mode=False
    actual_method(VIEW,'apply_remote_15_lane_mode')(view)
    assert not view.files_first_host.visible
