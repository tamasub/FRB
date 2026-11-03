"""1.5列のExp→List→Exp往復、通常モード互換とRemoteキャプション。"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
EXP = (ROOT / 'src/remote_files_explorer.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')


def method(source, cls_name, name, extras=None):
    top = ast.parse(source)
    cls = next(c for c in top.body if isinstance(c, ast.ClassDef) and c.name == cls_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    bare = ast.FunctionDef(name=node.name, args=node.args, body=node.body,
                           decorator_list=[], returns=None, type_comment=None)
    env = dict(extras or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[bare], type_ignores=[])),
                 '<actual-source>', 'exec'), env)
    return env[name]


def test_exp_right_commits_folder_and_moves_to_list():
    fn = method(APP, 'Launcher', 'remote_exp_right_to_list')
    panel = NS(remote_current_folder_path=Mock(return_value='F:/FRB'),
               tree=NS(currentIndex=Mock()))
    view = NS(_workspace_mode='files', isVisible=lambda: True, embedded_files_exp=panel)
    launcher = NS(remote_15_mode=True, files_exp_embedded_mode=True,
                  expanded_view=view, _current_remote_files_exp=lambda: panel,
                  navigate_files_exp_folder=Mock(return_value=True),
                  navigate_files_exp_pc=Mock(), remote_focus_area=Mock())
    assert fn(launcher) is True
    launcher.navigate_files_exp_folder.assert_called_once_with('F:/FRB')
    launcher.remote_focus_area.assert_called_once_with('directory')
    launcher.navigate_files_exp_pc.assert_not_called()


def test_exp_right_pc_uses_pc_navigation_not_fake_filesystem_path():
    fn = method(APP, 'Launcher', 'remote_exp_right_to_list')
    panel = NS(remote_current_folder_path=Mock(return_value=None),
               tree=NS(currentIndex=lambda: 'pc-index'),
               _is_pc_index=Mock(return_value=True))
    launcher = NS(remote_15_mode=True, files_exp_embedded_mode=True,
                  expanded_view=NS(_workspace_mode='files', isVisible=lambda: True, embedded_files_exp=panel),
                  _current_remote_files_exp=lambda: panel, navigate_files_exp_folder=Mock(), navigate_files_exp_pc=Mock(return_value=True),
                  remote_focus_area=Mock())
    assert fn(launcher) is True
    panel._is_pc_index.assert_called_once_with('pc-index')
    launcher.navigate_files_exp_folder.assert_not_called()
    launcher.navigate_files_exp_pc.assert_called_once()
    launcher.remote_focus_area.assert_called_once_with('directory')


def test_exp_right_bad_folder_keeps_exp_target():
    fn = method(APP, 'Launcher', 'remote_exp_right_to_list')
    panel = NS(remote_current_folder_path=lambda:'not-a-folder')
    launcher = NS(remote_15_mode=True, files_exp_embedded_mode=True,
                  expanded_view=NS(_workspace_mode='files',isVisible=lambda: True,embedded_files_exp=panel),
                  _current_remote_files_exp=lambda: panel, navigate_files_exp_folder=Mock(return_value=False),
                  remote_focus_area=Mock())
    assert fn(launcher) is False
    launcher.remote_focus_area.assert_not_called()


def make_list_launcher(*, at_first=True, path='F:/FRB', rows=2):
    items=[object() for _ in range(rows)]
    selected=items[0] if at_first and items else (items[-1] if items else None)
    tree=NS(topLevelItemCount=lambda:len(items), topLevelItem=lambda i:items[i],
            currentItem=lambda:selected)
    panel=NS(sync_current_directory=Mock(return_value=True),
             remote_select_pc_root=Mock(return_value=True))
    view=NS(_workspace_mode='files', isVisible=lambda: True, embedded_files_exp=panel,
            middle=NS(tree=tree), row_data=lambda item: {'kind':'folder'},
            current_directory=lambda:path)
    launcher=NS(remote_15_mode=True, files_exp_embedded_mode=True,
                expanded_view=view, _current_remote_files_exp=lambda: panel, remote_focus_area=Mock())
    return launcher,panel


def test_list_left_on_first_row_returns_to_same_breadcrumb_exp_folder():
    fn = method(APP, 'Launcher', 'remote_list_left_to_exp')
    launcher,panel=make_list_launcher()
    assert fn(launcher) is True
    panel.sync_current_directory.assert_called_once_with('F:/FRB')
    launcher.remote_focus_area.assert_called_once_with('files_exp')
    panel.remote_select_pc_root.assert_not_called()


def test_list_left_not_first_does_not_switch_or_sync():
    fn = method(APP, 'Launcher', 'remote_list_left_to_exp')
    launcher,panel=make_list_launcher(at_first=False)
    assert fn(launcher) is False
    panel.sync_current_directory.assert_not_called()
    launcher.remote_focus_area.assert_not_called()


def test_list_left_pc_uses_virtual_pc_root_and_does_not_collapse():
    fn = method(APP, 'Launcher', 'remote_list_left_to_exp')
    launcher,panel=make_list_launcher(path=None)
    assert fn(launcher) is True
    panel.remote_select_pc_root.assert_called_once()
    panel.sync_current_directory.assert_not_called()
    launcher.remote_focus_area.assert_called_once_with('files_exp')


def test_list_left_empty_returns_to_exp_at_breadcrumb():
    fn = method(APP, 'Launcher', 'remote_list_left_to_exp')
    launcher,panel=make_list_launcher(rows=0)
    assert fn(launcher) is True
    panel.sync_current_directory.assert_called_once_with('F:/FRB')
    launcher.remote_focus_area.assert_called_once_with('files_exp')


def test_arrow_routing_works_in_both_remote_placements():
    fn = method(APP, 'Launcher', 'remote_command')
    panel=NS(remote_step=Mock(),remote_branch=Mock(),remote_activate_current=Mock())
    view=NS(isVisible=lambda:True,web_view_active=lambda:False,
            _workspace_mode='files', embedded_files_exp=panel)
    launcher=NS(expanded_view=view,isVisible=lambda:True,isMinimized=lambda:False,
                _remote_popup_area=None,_remote_area='files_exp',
                _remote_page_menu=None,remote_cascade_command=lambda c:False,
                remote_focus_area=Mock(),remote_exp_right_to_list=Mock(return_value=True),
                _current_remote_files_exp=lambda: panel, remote_15_mode=True)
    fn(launcher,'RIGHT')
    launcher.remote_exp_right_to_list.assert_called_once()
    panel.remote_branch.assert_not_called()
    launcher.remote_focus_area.assert_not_called()
    launcher.remote_15_mode=False
    fn(launcher,'RIGHT')
    panel.remote_branch.assert_not_called()
    assert launcher.remote_exp_right_to_list.call_count == 2
    launcher.remote_focus_area.assert_not_called()


def test_remote_pc_root_selection_suppresses_automatic_breadcrumb_changes():
    fn=method(EXP,'RemoteFilesExplorer','remote_select_pc_root',
              {'QAbstractItemView': NS(ScrollHint=NS(EnsureVisible=1))})
    class Index:
        def __init__(self, i): self.i=i
    class Tree:
        def __init__(self):self.selected=None
        def setCurrentIndex(self,i): self.selected=i
        def scrollTo(self,*_): pass
    tree=Tree()
    panel=NS(model=NS(rowCount=lambda:2,index=lambda i,j:Index(i)),tree=tree,
             _is_pc_index=lambda idx:idx.i==1,
             _selection_timer=NS(stop=Mock()),_syncing_directory=False,
             _schedule_tree_state_save=Mock())
    assert fn(panel) is True
    assert tree.selected.i==1
    assert panel._syncing_directory is False
    panel._selection_timer.stop.assert_called_once()
    panel._schedule_tree_state_save.assert_called_once()


def test_remote_caption_says_list_current_folder():
    assert "QLabel('（List カレントフォルダー操作）'" in REMOTE
    assert "QLabel('（カレントフォルダー操作）'" not in REMOTE


def test_actual_list_left_routing_hands_off_only_at_first_row():
    fn=method(APP, 'Launcher', 'remote_command')
    a=object();b=object()
    class Tree:
        def __init__(self): self.current=a
        def currentItem(self): return self.current
        def topLevelItem(self,i):return (a,b)[i]
        def topLevelItemCount(self):return 2
    tree=Tree()
    view=NS(isVisible=lambda:True, web_view_active=lambda:False,
            _workspace_mode='files', middle=NS(tree=tree),
            left=NS(tree=NS()),right=NS(tree=NS()),
            navigate_left_from_middle=Mock(return_value='directory'),
            ensure_middle_current_selection=Mock(),
            row_data=lambda item: {'path':'dummy'})
    app=NS(isVisible=lambda:True,isMinimized=lambda:False,
           expanded_view=view,_remote_area='directory',_remote_popup_area=None,
           _remote_page_menu=None,remote_cascade_command=lambda c:False,
           files_root_hidden_mode=True,remote_15_mode=True,
           remote_list_left_to_exp=Mock(return_value=True),remote_focus_area=Mock())
    fn(app,'LEFT')
    app.remote_list_left_to_exp.assert_called_once()
    view.navigate_left_from_middle.assert_not_called()
    app.remote_list_left_to_exp.reset_mock(return_value=True)
    app.remote_list_left_to_exp.return_value=False  # helper: current is not first
    tree.current=b
    fn(app,'LEFT')
    view.navigate_left_from_middle.assert_called_once()


def test_arrow_helpers_run_in_normal_mode_but_not_browser_mode():
    exp_fn=method(APP,'Launcher','remote_exp_right_to_list')
    list_fn=method(APP,'Launcher','remote_list_left_to_exp')
    app,panel=make_list_launcher()
    app.remote_15_mode=False
    app.navigate_files_exp_folder=Mock(return_value=True)
    app.remote_focus_area=Mock()
    # Both helpers operate even with no 1.5-column placement.
    panel.remote_current_folder_path=Mock(return_value='F:/FRB')
    assert exp_fn(app) is True
    assert list_fn(app) is True
    panel.sync_current_directory.reset_mock()
    app.remote_15_mode=True
    app.expanded_view._workspace_mode='browser'
    assert exp_fn(app) is False
    assert list_fn(app) is False
    panel.sync_current_directory.assert_not_called()
