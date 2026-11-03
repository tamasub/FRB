"""第1.5列・左右二つの操作対象と Browser自動非表示。

PySide6を起動できない環境でも、実ソースのメソッドを抽出して
Qt依存の少ない責務を直接テストする。
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT/'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT/'src/launch_remote.py').read_text(encoding='utf-8')
EXP = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')
VIEW = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')


def actual(source, klass, name, extras=None):
    root = ast.parse(source)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == klass)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    # Keep the actual function body, only remove annotations/decorators.
    bare = ast.FunctionDef(name=node.name, args=node.args, body=node.body,
                           decorator_list=[], returns=None, type_comment=None)
    env = dict(extras or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[bare], type_ignores=[])),
                 '<actual-source>', 'exec'), env)
    return env[name]


def test_remote_buttons_split_and_browser_full_width():
    assert "'REMOTE_TARGET_EXP', width=85, height=27" in REMOTE
    assert "'REMOTE_TARGET_LIST', width=85, height=27" in REMOTE
    assert "'WORKSPACE_BROWSER', width=172, height=27" in REMOTE
    assert 'row_workspaces.addWidget(self.files_exp_button)' in REMOTE
    assert 'row_workspaces.addWidget(self.files_list_button)' in REMOTE
    assert 'root.addWidget(self.browser_button)' in REMOTE
    assert "'files_exp': 'Files Exp'" in REMOTE
    assert "'directory': 'Files List'" in REMOTE


def test_exp_and_list_switch_only_operating_target_not_breadcrumb():
    fn = actual(APP, 'Launcher', 'remote_command')
    called = []
    view = NS(isVisible=lambda: True, _workspace_mode='files')
    app = NS(isVisible=lambda: True, isMinimized=lambda: False,
             expanded_view=view, remote_focus_area=lambda target: called.append(target))
    fn(app, 'REMOTE_TARGET_EXP')
    fn(app, 'REMOTE_TARGET_LIST')
    assert called == ['files_exp', 'directory']


def test_exp_wheel_changes_selection_without_committing_folder():
    class Index:
        def __init__(self, i): self.i=i
        def isValid(self): return self.i >= 0
    class Tree:
        def __init__(self): self.index=Index(0); self.selected=[]
        def currentIndex(self): return self.index
        def indexBelow(self, index): return Index(index.i+1)
        def indexAbove(self, index): return Index(index.i-1)
        def setCurrentIndex(self, index): self.index=index; self.selected.append(index.i)
        def scrollTo(self,*args): pass
    tree=Tree()
    panel=NS(tree=tree, model=NS(index=lambda row,col:Index(row)),
             _selection_timer=NS(stop=Mock()), _schedule_tree_state_save=Mock())
    fn=actual(EXP, 'RemoteFilesExplorer', 'remote_step',
              {'QAbstractItemView':NS(ScrollHint=NS(EnsureVisible=0))})
    assert fn(panel,1)
    assert tree.selected == [1]
    panel._selection_timer.stop.assert_called_once()
    assert not hasattr(panel, 'folder_selected')  # Can't navigate the filesystem.


def test_exp_central_button_expands_and_navigates_only_on_activation():
    class Index:
        def isValid(self): return True
    index = Index()
    triggered=[]
    class Tree:
        def currentIndex(self): return index
        def isExpanded(self,_): return bool(triggered)
        def expand(self,_): triggered.append('expanded_and_existing_disclosure_event')
    panel=NS(tree=Tree(), _selection_timer=NS(stop=Mock()),
             _activate_index=Mock())
    fn=actual(EXP,'RemoteFilesExplorer','remote_activate_current')
    assert fn(panel)
    assert triggered
    panel._activate_index.assert_not_called()  # Disclosure signal owns navigation.
    assert fn(panel)
    panel._activate_index.assert_called_once_with(index)


def test_remote_exp_click_calls_real_folder_tree():
    fn=actual(APP,'Launcher','remote_mouse_click')
    panel=NS(remote_activate_current=Mock())
    view=NS(isVisible=lambda: True, web_view_active=lambda: False,
            commit_remote_inline_rename=lambda: False,
            embedded_files_exp=panel)
    app=NS(expanded_view=view, _remote_page_menu=None, _remote_area='files_exp',
           _last_focus_area='directory', _remote_popup_area=None,
           remote_cascade_command=lambda command: False,
           _current_remote_files_exp=lambda: panel,
           remote_focus_area=Mock())
    fn(app, double=False)
    panel.remote_activate_current.assert_called_once()
    app.remote_focus_area.assert_called_once_with('files_exp')


def test_browser_switch_hides_floating_remote_and_files_reopens():
    fn=actual(APP,'Launcher','workspace_changed')
    called=[]
    remote=NS(set_workspace=lambda mode: called.append(('set',mode)),
              isVisible=lambda: False)
    app=NS(remote_15_mode=True, _remote_15_needs_show=True,
           _remote_popup_area=None, expanded_view=NS(),
           remote_window=remote, _remote_area='files_exp',
           hide_remote=lambda: called.append(('hide',)),
           close_remote_folder_menu=lambda: called.append(('close_menu',)),
           queue_remote_15_alignment=lambda **kw: called.append(('align',kw)))
    fn(app,'browser')
    assert ('hide',) in called
    assert app._remote_15_needs_show is False
    called.clear()
    fn(app,'files')
    assert ('align', {'show': True}) in called
    assert ('hide',) not in called


def test_files_list_title_and_exp_title_share_width_and_style():
    fn=actual(VIEW,'ExpandedLauncherView','_align_files_list_title_width')
    title=NS(width=lambda:110, setFixedWidth=Mock())
    view=NS(files_list_title_box=title, embedded_files_exp=NS(width=lambda:238))
    fn(view)
    title.setFixedWidth.assert_called_once_with(238)
    assert "QFrame#filesListTitleBox" in VIEW
    assert "QLabel#filesListTitle" in VIEW
    assert "self.files_list_title_label = QLabel('Files List'" in VIEW
    assert 'header_row.setContentsMargins(8 if self._embedded else 2' in EXP


def test_browser_remote_command_and_search_result_paths_preserved():
    assert "if command == 'SEARCH_RESULT_DOUBLE_CLICK':" in APP
    assert 'self.remote_search_result_double_click()' in APP
    assert "if command == 'WORKSPACE_FILES'" in APP
    assert 'self.show_expanded_background_paste_menu' in APP
    assert "if not expanded and getattr(self, 'remote_15_mode', False)" in APP
    assert "view._workspace_mode == 'browser':" in APP
    assert "self._remote_15_needs_show = False" in APP
