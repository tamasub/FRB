"""Debounced Exp-wheel breadcrumb/List preview, with Exp still the controller.

These execute the actual production class methods via AST, without PySide6.
Windows Qt painting/scroll geometry is an additional manual verification.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP = (ROOT / 'src' / 'remote_files_explorer.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def actual(text, class_name, name, scope=None):
    klass = next(n for n in ast.parse(text).body
                 if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(scope or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 '<actual-source>', 'exec'), env)
    return env[name]


class PendingTimer:
    def __init__(self):
        self.pending = False
        self.starts = 0
        self.stops = 0
        self.callback = None
    def start(self):
        self.starts += 1
        self.pending = True
    def stop(self):
        self.stops += 1
        self.pending = False
    def fire(self):
        if not self.pending:
            return False
        self.pending = False
        self.callback()
        return True


class Index:
    def __init__(self, number):
        self.number = number
    def isValid(self):
        return self.number >= 0
    def __eq__(self, rhs):
        return isinstance(rhs, Index) and rhs.number == self.number


class FakeTree:
    def __init__(self, panel):
        self.panel = panel
        self.idx = Index(0)
    def currentIndex(self):
        return self.idx
    def setCurrentIndex(self, idx):
        old = self.idx
        self.idx = idx
        if idx != old:
            self.panel._selection_changed(idx, old)
    def indexBelow(self, idx):
        return Index(min(idx.number + 1, len(self.panel.paths) - 1))
    def indexAbove(self, idx):
        return Index(max(idx.number - 1, 0))
    def scrollTo(self, idx, hint):
        pass


class Rig:
    def __init__(self, tmp_path, floating=False):
        self.paths = [tmp_path / name for name in ('one', 'two', 'three', 'empty')]
        for directory in self.paths:
            directory.mkdir()
        for name, path in (('1.txt', self.paths[0]), ('2.txt', self.paths[1]),
                           ('3.txt', self.paths[2])):
            (path / name).write_text(name, encoding='utf-8')
        self.breadcrumb = str(self.paths[0])
        self.rows = ['1.txt']
        self.refreshes = []
        self.operating_target = 'directory'
        self.remote = NS(isVisible=lambda: True)
        self.app = NS(remote_window=self.remote, _files_operating_target='directory',
                      remote_15_mode=floating, files_exp_embedded_mode=floating)
        self.view = NS(_workspace_mode='files', isVisible=lambda: True, path=[],
                       launcher=self.app, middle=NS(),
                       current_directory=lambda: self.breadcrumb,
                       focus_panel=lambda _: None)
        self.app.expanded_view = self.view
        def refresh():
            self.breadcrumb = self.view.path[-1]['directory']
            self.rows = sorted(os.listdir(self.breadcrumb))
            self.refreshes.append(self.breadcrumb)
        self.view.refresh_middle = refresh
        go_to_directory = actual(VIEW, 'ExpandedLauncherView', 'go_to_directory',
                {'os': os, 'normalized_directory': lambda s: str(s),
                 'directory_row': lambda s: {'directory': s}})
        self.view.go_to_directory = lambda path, **kw: go_to_directory(self.view, path, **kw)
        nav = actual(APP, 'Launcher', 'navigate_files_exp_folder', {'Path': Path})
        self.app.navigate_files_exp_folder = lambda path: nav(self.app, path)
        self.panel = NS(_embedded=floating, _syncing_directory=False,
                        _restoring_tree=False, _launcher=self.app,
                        _schedule_tree_state_save=lambda: None,
                        paths=self.paths)
        self.panel._selection_timer = PendingTimer()
        self.panel.tree = FakeTree(self.panel)
        self.panel.model = NS(index=lambda row, _: Index(row))
        self.panel._index_path = lambda idx: str(self.paths[idx.number]) if idx.isValid() else None
        self.panel._is_pc_index = lambda idx: False
        self.panel.folder_selected = NS(emit=self.app.navigate_files_exp_folder)
        self.panel.pc_selected = NS(emit=Mock())
        selection_changed = actual(EXP,'RemoteFilesExplorer','_selection_changed')
        commit = actual(EXP,'RemoteFilesExplorer','_commit_current_selection',{'os':os})
        step = actual(EXP, 'RemoteFilesExplorer','remote_step',
                      {'QAbstractItemView':NS(ScrollHint=NS(EnsureVisible=0))})
        self.panel._selection_changed = lambda idx,prev: selection_changed(self.panel,idx,prev)
        self.panel._selection_timer.callback = lambda: commit(self.panel)
        self.panel.remote_step = lambda direction: step(self.panel,direction)
        setter = actual(APP,'Launcher','set_files_operating_target')
        # The real target setter updates several Qt visual widgets; on this
        # fixture only the *one canonical target* and pending timer matter.
        def set_target(target):
            if target != 'files_exp':
                self.panel._selection_timer.stop()
            self.app._files_operating_target = target
            self.operating_target = target
        self.app.set_files_operating_target = set_target
        self.view.launcher = self.app


@pytest.mark.parametrize('floating', [False, True])
def test_exp_direct_scroll_updates_breadcrumb_and_list_but_not_target(tmp_path, floating):
    rig = Rig(tmp_path, floating)
    rig.app.set_files_operating_target('files_exp')  # native Exp wheel claims this
    rig.panel.tree.setCurrentIndex(Index(1))  # QTreeView currentChanged from wheel
    assert rig.panel._selection_timer.pending
    assert rig.breadcrumb == str(rig.paths[0])
    assert rig.rows == ['1.txt']
    rig.panel._selection_timer.fire()
    assert rig.breadcrumb == str(rig.paths[1])
    assert rig.rows == ['2.txt']
    assert rig.operating_target == 'files_exp'
    assert rig.refreshes == [str(rig.paths[1])]


@pytest.mark.parametrize('floating', [False, True])
def test_remote_exp_wheel_updates_list_using_same_debounced_navigation(tmp_path, floating):
    rig = Rig(tmp_path, floating)
    rig.app.set_files_operating_target('files_exp')
    assert rig.panel.remote_step(+1)
    assert rig.panel._selection_timer.pending
    assert rig.breadcrumb == str(rig.paths[0])
    rig.panel._selection_timer.fire()
    assert rig.breadcrumb == str(rig.paths[1])
    assert rig.rows == ['2.txt']
    assert rig.operating_target == 'files_exp'


def test_fast_wheel_only_commits_final_folder_after_quiet_interval(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    rig.panel.remote_step(1)
    assert rig.panel._selection_timer.starts == 2
    assert rig.panel._selection_timer.stops >= 2
    assert rig.refreshes == []
    rig.panel._selection_timer.fire()
    assert rig.refreshes == [str(rig.paths[2])]
    assert rig.rows == ['3.txt']


def test_empty_folder_is_a_valid_preview_and_exp_keeps_control(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.tree.setCurrentIndex(Index(3))
    rig.panel._selection_timer.fire()
    assert rig.breadcrumb == str(rig.paths[3])
    assert rig.rows == []
    assert rig.operating_target == 'files_exp'


def test_switching_to_list_cancels_wheel_navigation(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    rig.app.set_files_operating_target('directory')
    assert not rig.panel._selection_timer.fire()
    assert rig.breadcrumb == str(rig.paths[0])
    assert rig.operating_target == 'directory'


def test_browser_switch_after_scroll_does_not_navigate_even_on_late_timeout(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    rig.view._workspace_mode = 'browser'
    # Even if an already queued Qt timeout fires, the handler re-checks state.
    assert rig.panel._selection_timer.fire()
    assert rig.breadcrumb == str(rig.paths[0])
    assert rig.refreshes == []


def test_programmatic_tree_sync_does_not_schedule_delayed_navigation(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel._syncing_directory = True
    rig.panel.tree.setCurrentIndex(Index(1))
    rig.panel._syncing_directory = False
    assert not rig.panel._selection_timer.pending
    rig.panel._restoring_tree = True
    rig.panel.tree.setCurrentIndex(Index(2))
    rig.panel._restoring_tree = False
    assert not rig.panel._selection_timer.pending
    assert rig.refreshes == []


def test_explicit_right_handoff_cancels_pending_wheel_preview(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    rig.app._current_remote_files_exp = lambda: rig.panel
    rig.panel.remote_current_folder_path = lambda: str(rig.paths[1])
    rig.app.remote_focus_area = lambda target: rig.app.set_files_operating_target(target)
    method = actual(APP, 'Launcher', 'remote_exp_right_to_list')
    assert method(rig.app)
    assert rig.breadcrumb == str(rig.paths[1])
    assert rig.operating_target == 'directory'
    assert rig.refreshes == [str(rig.paths[1])]
    assert not rig.panel._selection_timer.fire()  # No second reload.


def test_same_folder_preview_does_not_refresh_again(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.tree.setCurrentIndex(Index(1))
    assert rig.panel._selection_timer.fire()
    rig.panel.tree.setCurrentIndex(Index(0))
    assert rig.panel._selection_timer.fire()
    rig.panel.tree.setCurrentIndex(Index(1))
    assert rig.panel._selection_timer.fire()
    assert rig.refreshes == list(map(str, (rig.paths[1],rig.paths[0],rig.paths[1])))
    # A repeated debounce on the *same current folder* is a no-op.
    rig.panel._selection_changed(Index(1),Index(0))
    assert rig.panel._selection_timer.fire()
    assert len(rig.refreshes) == 3


def test_remote_dispatch_does_not_cancel_timer_after_wheel_step():
    # Inspect the ACTUAL remote_command branch rather than replaying all its
    # non-related menus, QR actions and Windows application state.
    fn = next(n for n in ast.walk(ast.parse(APP))
              if isinstance(n, ast.FunctionDef) and n.name == 'remote_command')
    body = ast.get_source_segment(APP, fn)
    branch_start = body.index("if (expanded and not browser_mode and area == 'files_exp'):")
    branch_end = body.index("if (self.files_root_hidden_mode and expanded", branch_start)
    branch = body[branch_start:branch_end]
    assert branch.index("self.remote_focus_area('files_exp')") < branch.index('panel.remote_step(')
    assert "self.remote_exp_right_to_list()" in branch


def test_active_column_cancellation_is_in_canonical_setter():
    fn = next(n for n in ast.walk(ast.parse(APP))
              if isinstance(n, ast.FunctionDef) and n.name == 'set_files_operating_target')
    body = ast.get_source_segment(APP, fn)
    assert "if target != 'files_exp':" in body
    assert 'exp_panel._selection_timer.stop()' in body


def test_exp_click_beats_pending_wheel_debounce(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    activate = actual(EXP, 'RemoteFilesExplorer', '_activate_index')
    assert rig.panel._selection_timer.pending
    activate(rig.panel, Index(1))
    assert rig.breadcrumb == str(rig.paths[1])
    assert rig.refreshes == [str(rig.paths[1])]
    assert not rig.panel._selection_timer.fire()
    assert rig.operating_target == 'files_exp'


def test_canonical_launcher_target_setter_stops_pending_preview_when_list_claims_control():
    class PaneTree:
        def __init__(self):
            self.values = {}
        def property(self, k): return self.values.get(k)
        def setProperty(self, k, value): self.values[k] = value
        def style(self): return self
        def unpolish(self, w): pass
        def polish(self, w): pass
        def viewport(self): return self
        def update(self): pass
    timer = PendingTimer()
    timer.start()
    exp = NS(_selection_timer=timer, set_operating_active=lambda _v: None)
    view = NS(_workspace_mode='files', left=NS(tree=PaneTree()),
              middle=NS(tree=PaneTree()), set_files_operating_area=lambda target: None)
    remote = NS(files_exp_panel=exp, set_operating_target=lambda target: None,
                set_area=lambda target: None)
    launcher = NS(files_exp_embedded_mode=True, expanded_view=view,
                  remote_window=remote, _files_operating_target='files_exp',
                  files_exp_panels=lambda: (exp,))
    setter = actual(APP, 'Launcher', 'set_files_operating_target')
    assert setter(launcher, 'directory')
    assert timer.pending is False
    assert launcher._files_operating_target == 'directory'
    assert view.middle.tree.values['remoteInactive'] is False


def test_right_after_live_preview_transfers_to_list_without_second_refresh(tmp_path):
    rig = Rig(tmp_path)
    rig.app.set_files_operating_target('files_exp')
    rig.panel.remote_step(1)
    assert rig.panel._selection_timer.fire()
    assert rig.refreshes == [str(rig.paths[1])]
    rig.app._current_remote_files_exp = lambda: rig.panel
    rig.panel.remote_current_folder_path = lambda: str(rig.paths[1])
    rig.app.remote_focus_area = lambda target: rig.app.set_files_operating_target(target)
    handoff = actual(APP, 'Launcher', 'remote_exp_right_to_list')
    assert handoff(rig.app)
    assert rig.operating_target == 'directory'
    assert rig.refreshes == [str(rig.paths[1])]
