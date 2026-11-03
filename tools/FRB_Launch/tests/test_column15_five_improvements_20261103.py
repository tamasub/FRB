"""2026-11-03: Remote 1.5-column history/pane polish without PySide6."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1] / 'src'
APP = (ROOT / 'app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'expanded_view.py').read_text(encoding='utf-8')
EXP = (ROOT / 'remote_files_explorer.py').read_text(encoding='utf-8')


def method(src, cls, name, env=None):
    tree = ast.parse(src)
    found = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == cls)
    node = next(n for n in found.body if isinstance(n, ast.FunctionDef) and n.name == name)
    executable = ast.FunctionDef(name=node.name, args=node.args, body=node.body,
                                 decorator_list=[], returns=None, type_comment=None)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[executable], type_ignores=[])),
                 '<actual-source>', 'exec'), scope)
    return scope[name]


def fake_panel():
    events = []
    child_index = NS(isValid=lambda: True)
    parent_index = NS(isValid=lambda: True)
    child = NS(index=lambda: child_index)
    parent_item = NS(rowCount=lambda: 1, child=lambda row: child)
    def collapse(index):
        assert panel._syncing_directory is True, 'collapsing must not trigger navigation'
        events.append(index)
    panel = NS(_syncing_directory=False,
               tree=NS(currentIndex=lambda: parent_index,
                       isExpanded=lambda index: index is child_index,
                       collapse=collapse),
               model=NS(itemFromIndex=lambda index: parent_item),
               _index_path=lambda index: ('F:/FRB' if index is parent_index else 'F:/FRB/assets'),
               _schedule_tree_state_save=Mock())
    return panel, events


def test_go_up_collapses_only_departed_child_with_navigation_suppressed():
    f = method(EXP, 'RemoteFilesExplorer', 'collapse_departed_child')
    panel, events = fake_panel()
    assert f(panel, 'F:/FRB/assets', 'F:/FRB') is True
    assert len(events) == 1
    assert panel._syncing_directory is False
    panel._schedule_tree_state_save.assert_called_once()


def test_go_up_does_not_close_unrelated_branches():
    f = method(EXP, 'RemoteFilesExplorer', 'collapse_departed_child')
    panel, events = fake_panel()
    assert f(panel, 'F:/FRB/assets/subfolder', 'F:/FRB') is False
    assert events == []
    panel._schedule_tree_state_save.assert_not_called()


def test_launcher_syncs_to_parent_before_collapsing_departed_folder():
    f = method(APP, 'Launcher', 'on_files_directory_changed', {'os': __import__('os')})
    calls = []
    def sync(path):
        calls.append(('sync', path))
    def collapse(old, new):
        calls.append(('collapse', old, new))
    panel = NS(isVisible=lambda: True, sync_current_directory=sync,
               collapse_departed_child=collapse)
    launcher = NS(_last_files_breadcrumb_directory='F:/FRB/assets',
                  remote_window=None, expanded_view=NS(embedded_files_exp=panel),
                  refresh_main_files_cut_visuals=Mock(),
                  _remote_folder_opener=None, _remote_folder_root_menu=None)
    f(launcher, 'F:/FRB')
    assert calls == [('sync', 'F:/FRB'), ('collapse', 'F:/FRB/assets', 'F:/FRB')]
    assert launcher._last_files_breadcrumb_directory == 'F:/FRB'
    calls.clear()
    f(launcher, 'F:/Other')
    assert calls == [('sync', 'F:/Other')], 'non-parent navigation may not collapse Exp'


def test_empty_list_left_handoff_also_supports_pc_root():
    f = method(APP, 'Launcher', 'remote_list_left_to_exp')
    tree = NS(topLevelItemCount=lambda: 0, topLevelItem=lambda _: None,
              currentItem=lambda: None)
    panel = NS(sync_current_directory=Mock(return_value=True),
               remote_select_pc_root=Mock(return_value=True))
    view = NS(_workspace_mode='files', isVisible=lambda: True, embedded_files_exp=panel,
              middle=NS(tree=tree), row_data=lambda item: None,
              current_directory=lambda: None)
    launcher = NS(remote_15_mode=True, files_exp_embedded_mode=True,
                  expanded_view=view, _current_remote_files_exp=lambda: panel,
                  remote_focus_area=Mock())
    assert f(launcher) is True
    panel.remote_select_pc_root.assert_called_once()
    launcher.remote_focus_area.assert_called_once_with('files_exp')


def test_empty_files_list_label_is_centered_muted_and_mouse_transparent():
    assert "QLabel('このフォルダーは空です。', self.middle.tree.viewport())" in VIEW
    assert 'WA_TransparentForMouseEvents' in VIEW
    assert 'self.middle.tree.viewport().installEventFilter(self)' in VIEW
    assert 'self._update_middle_empty_label()' in VIEW
    assert '一致する項目はありません。' in VIEW
    assert '#8e918d' in VIEW
    assert 'def _position_middle_empty_label(self):' in VIEW


def test_empty_label_update_is_cleared_when_real_folder_has_items():
    f = method(VIEW, 'ExpandedLauncherView', '_update_middle_empty_label',
               {'os': NS(path=NS(isdir=lambda path: True))})
    label = NS(setText=Mock(), show=Mock(), hide=Mock(), raise_=Mock())
    tree = NS(topLevelItemCount=lambda: 0)
    view = NS(middle_empty_label=label, current_directory=lambda: 'F:/FRB/empty',
              middle=NS(tree=tree, ), middle_search=NS(text=lambda: ''),
              _position_middle_empty_label=Mock())
    f(view)
    label.setText.assert_called_once_with('このフォルダーは空です。')
    label.show.assert_called_once()
    tree.topLevelItemCount = lambda: 4
    f(view)
    label.hide.assert_called_once()


def test_history_positions_anchor_to_files_list_only_in_experiment():
    hist = method(APP, 'Launcher', 'position_history_popup')
    fav = method(VIEW, 'ExpandedLauncherView', 'position_directory_favorites')
    assert 'files_list_title_box' in ast.get_source_segment(APP, next(
        n for n in ast.walk(ast.parse(APP)) if isinstance(n, ast.FunctionDef)
        and n.name == 'position_history_popup'))
    assert 'list_title.mapTo(self, QPoint(0, 0)).x()' in APP
    assert 'title.mapTo(self.launcher, QPoint(0, 0)).x()' in VIEW
    assert 'self._workspace_mode == \'files\'' in VIEW
    assert callable(hist) and callable(fav)


def test_active_column_warm_background_keeps_green_row_selection():
    assert '#FFFEF9' in EXP and '#FFFEF9' in VIEW
    assert 'QTreeView#filesExpTree[operatingActive="true"]' in EXP
    assert 'QTreeWidget#expandedTree[detailsColumns="true"][remoteInactive="false"]' in VIEW
    assert 'QWidget#expandedBackLane[operatingActive="true"]' in VIEW
    assert 'QWidget#expandedMiddleTreeContainer[operatingActive="true"]' in VIEW
    assert 'QFrame#filesListTitleBox[operatingActive="true"]' in VIEW
    assert 'QFrame#filesExpHeader[operatingActive="true"]' in EXP
    assert "background:{colors['selection']}" in EXP
    assert 'background:{active};color:{text}' in VIEW
    assert 'QTreeView#filesExpTree::item:selected' in EXP
    assert 'QTreeWidget#expandedTree[remoteInactive="true"]::item:selected' in VIEW


def test_remote_15_controller_remains_standalone():
    assert 'queue_remote_15_alignment' in APP
    assert 'remote_15_lane.setFixedWidth(196)' in VIEW
    assert 'self.remote_list_left_to_exp()' in APP
