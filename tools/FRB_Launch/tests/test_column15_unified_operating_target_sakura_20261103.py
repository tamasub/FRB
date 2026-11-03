"""One canonical Exp/List target, intentional gestures, Sakura tone, blank List guidance.

Runs without PySide6: these are the ACTUAL source methods extracted from AST,
not reimplemented logic. The Windows painting result is an explicit manual check.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
VIEW = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
EXP = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')


def method(text, cls, name):
    module = ast.parse(text)
    cls_node = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in cls_node.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<actual>', 'exec'), ns)
    return ns[name]


class PaneTree:
    def __init__(self):
        self.p = {}
        self.remote_highlight_mode = False
        self.remote_logical_active = False
        self.update_calls = 0
    def property(self, name): return self.p.get(name)
    def setProperty(self, name, value): self.p[name] = value
    def style(self): return self
    def polish(self, widget): pass
    def unpolish(self, widget): pass
    def viewport(self): return self
    def update(self): self.update_calls += 1


def launcher_stub():
    left, middle = PaneTree(), PaneTree()
    pane_modes = []
    remote = NS(set_operating_target=Mock(), set_area=Mock())
    view = NS(_workspace_mode='files', left=NS(tree=left), middle=NS(tree=middle),
              set_files_operating_area=lambda target: pane_modes.append(target))
    app = NS(expanded_view=view, files_exp_embedded_mode=True, remote_window=remote,
             _files_operating_target='directory', _remote_area='directory',
             _last_focus_area='directory', breadcrumb='F:/FRB/unchanged')
    return app, view, remote, pane_modes


def test_single_source_updates_remote_titles_rows_and_no_navigation():
    app, view, remote, modes = launcher_stub()
    setter = method(APP,'Launcher','set_files_operating_target')
    assert setter(app,'files_exp')
    assert (app._files_operating_target, app._remote_area) == ('files_exp','files_exp')
    assert modes == ['files_exp']
    assert view.left.tree.remote_logical_active is False
    assert view.middle.tree.remote_logical_active is False
    assert view.middle.tree.property('remoteInactive') is True
    remote.set_operating_target.assert_called_once_with('files_exp')
    remote.set_area.assert_called_once_with('files_exp')
    assert app.breadcrumb == 'F:/FRB/unchanged'
    assert setter(app,'directory')
    assert app._files_operating_target == 'directory'
    assert modes == ['files_exp','directory']
    assert view.middle.tree.remote_logical_active is True
    assert view.middle.tree.property('remoteInactive') is False
    assert app.breadcrumb == 'F:/FRB/unchanged'


def test_direct_mouse_press_changes_the_canonical_target_immediately():
    app, view, remote, modes = launcher_stub()
    setter = method(APP,'Launcher','set_files_operating_target')
    app.set_files_operating_target = lambda target: setter(app,target)
    controller = NS(launcher=app, _workspace_mode='files')
    clicked = method(VIEW,'ExpandedLauncherView','_sync_remote_area_after_mouse_press')
    clicked(controller, 'directory')
    clicked(controller, 'files_exp')
    assert app._remote_area == 'files_exp'
    assert modes == ['directory','files_exp']
    assert remote.set_area.call_args.args == ('files_exp',)


def test_mouse_wheel_exp_claims_target_but_no_delayed_breadcrumb_navigation():
    app, view, remote, modes = launcher_stub()
    app.remote_15_mode = True
    setter = method(APP,'Launcher','set_files_operating_target')
    app.set_files_operating_target = lambda target: setter(app,target)
    panel = NS(_embedded=True, _launcher=app, _selection_timer=NS(stop=Mock(), start=Mock()))
    tree = NS(parentWidget=lambda:panel)
    claim = method(EXP,'FilesExpWheelTree','_claim_operating_target')
    claim(tree)
    panel._selection_timer.stop.assert_called_once()
    assert app._files_operating_target == 'files_exp'
    assert modes == ['files_exp']
    assert app.breadcrumb == 'F:/FRB/unchanged'
    # Guard against user scroll generating the legacy delayed commit.
    selection = method(EXP,'RemoteFilesExplorer','_selection_changed')
    panel._syncing_directory = False
    panel._schedule_tree_state_save = Mock()
    selection(panel, 'row-b', 'row-a')
    assert panel._selection_timer.stop.call_count == 2
    panel._selection_timer.start.assert_not_called()
    assert app.breadcrumb == 'F:/FRB/unchanged'


def test_standalone_exp_wheel_does_not_silently_navigate():
    selection = method(EXP,'RemoteFilesExplorer','_selection_changed')
    panel = NS(_embedded=False, _launcher=NS(remote_15_mode=True),
               _syncing_directory=False,_schedule_tree_state_save=Mock(),
               _selection_timer=NS(stop=Mock(),start=Mock()),
               _index_path=lambda index:'F:/Folder',_is_pc_index=lambda index:False)
    selection(panel,'row-b','row-a')
    panel._selection_timer.stop.assert_called_once_with()
    panel._selection_timer.start.assert_not_called()


def test_direct_list_wheel_hook_and_exp_mouse_and_wheel_hooks_are_present():
    assert "self._sync_remote_area_after_mouse_press('directory')" in VIEW
    assert "obj in (self.middle.tree.viewport()," in VIEW
    assert "self._claim_operating_target()" in EXP
    assert 'def mousePressEvent(self, event):' in EXP
    assert 'def wheelEvent(self, event):' in EXP


def test_navigation_preserves_exp_target_until_exp_right_handoff():
    go_source = ast.get_source_segment(VIEW, next(n for n in ast.walk(ast.parse(VIEW))
                            if isinstance(n, ast.FunctionDef) and n.name == 'go_to_directory'))
    assert "if preserve_remote_popup:" in go_source
    assert 'self.launcher.set_files_operating_target(' in go_source
    assert "getattr(self.launcher, '_files_operating_target', 'directory')" in go_source
    assert "self.remote_focus_area('directory')" in APP  # Explicit right arrow.
    assert 'def remote_exp_right_to_list(self):' in APP


def test_browser_workspace_is_not_a_second_files_operating_target():
    app, view, remote, modes = launcher_stub()
    setter = method(APP,'Launcher','set_files_operating_target')
    setter(app, 'files_exp')
    view._workspace_mode='browser'
    count=remote.set_area.call_count
    setter(app,'directory')
    # State can be retained, but no Files UI must be painted while in Browser.
    assert remote.set_area.call_count == count
    assert modes == ['files_exp']


def test_sakura_editor_canvas_color_exact_and_titles_gently_warm():
    assert "operating_bg = '#FFFEF9' if light" in VIEW
    assert "operating_bg = '#FFFEF9' if theme_family(theme)" in EXP
    assert '#FFF9EF' in VIEW and '#FFF9EF' in EXP
    assert 'QTreeView#filesExpTree[operatingActive="true"]' in EXP
    assert 'QTreeWidget#expandedTree[detailsColumns="true"][remoteInactive="false"]' in VIEW
    assert 'QWidget#expandedMiddleTreeContainer[operatingActive="true"]' in VIEW


def test_empty_folder_message_appears_on_second_row_and_is_noninteractive():
    pos = method(VIEW,'ExpandedLauncherView','_position_middle_empty_label')
    positions=[]
    label=NS(setGeometry=lambda *args: positions.append(args))
    viewport=NS(height=lambda:800,width=lambda:540)
    pane=NS(middle_empty_label=label,middle=NS(tree=NS(viewport=lambda:viewport)))
    pos(pane)
    assert positions == [(0,28,540,28)]
    viewport.height=lambda:40
    pos(pane)
    assert positions[-1] == (0,12,540,28)
    assert 'WA_TransparentForMouseEvents' in VIEW
    assert "'このフォルダーは空です。'" in VIEW
