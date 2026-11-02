"""Promoted Files Exp / Page context menu contracts; Qt-free regression tests."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text('utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
EXPLORER = (ROOT / 'src' / 'remote_files_explorer.py').read_text('utf-8')


def method(text, cls_name, method_name):
    root = ast.parse(text)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)


def bound(text, class_name, name, global_names):
    body = method(text, class_name, name)
    ns = dict(global_names)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body], type_ignores=[])),
                 'extracted.py', 'exec'), ns)
    return ns[name]


def test_files_exp_above_files_and_both_mouse_buttons():
    exp = REMOTE.index('root.addWidget(self.files_exp_button)')
    files = REMOTE.index('row_workspaces.addWidget(self.files_button)')
    assert exp < files
    assert "'FILES_EXP_PREVIEW', width=172, height=27" in REMOTE
    assert 'self.files_exp_button.clicked.connect(self.toggle_files_exp)' in REMOTE
    assert 'self.files_exp_button.customContextMenuRequested.connect(' in REMOTE


def test_folder_navigation_updates_breadcrumb_via_existing_api(tmp_path):
    go_calls = []
    view = NS(isVisible=lambda: True, _workspace_mode='browser',
              show_files_view=lambda: go_calls.append('show_files'),
              go_to_directory=lambda path, **kwargs: go_calls.append((path, kwargs)) or True)
    navigate = bound(APP, 'Launcher', 'navigate_files_exp_folder', {'Path': Path})
    launcher = NS(expanded_view=view)
    assert navigate(launcher, str(tmp_path))
    assert go_calls == ['show_files',
                        (str(tmp_path), {'preserve_remote_popup': True})]
    go_calls.clear()
    assert not navigate(launcher, str(tmp_path / 'missing'))
    assert not go_calls


def test_right_click_routes_into_existing_full_remote_context_menu(tmp_path):
    events = []
    show = bound(APP, 'Launcher', 'show_files_exp_folder_menu', {})
    launcher = NS(navigate_files_exp_folder=lambda p: events.append(('navigate', p)) or True,
                  close_remote_folder_menu=lambda: events.append('close-old'),
                  show_expanded_background_paste_menu=lambda pos, **kw: events.append(('menu', pos, kw)) or True)
    assert show(launcher, str(tmp_path), 'here')
    assert events == [('navigate', str(tmp_path)), 'close-old',
                      ('menu', 'here', {'remote_folder_list': True,
                                       'files_exp_rename_target': str(tmp_path)})]
    assert "folder_list_action = menu.addAction('Filesリスト')" in APP
    assert "self.expanded_view.add_lane_new_submenu(menu)" in APP
    assert "folder_actions.add('rename')" in APP


def test_tree_context_uses_clicked_folder_not_previous_selection():
    block = ast.get_source_segment(EXPLORER, method(EXPLORER, 'RemoteFilesExplorer', '_show_folder_context'))
    assert 'self.tree.indexAt(local_pos)' in block
    assert 'self.tree.setCurrentIndex(index)' in block
    assert 'self.folder_context_requested.emit(path' in block
    assert 'self.tree.viewport().mapToGlobal(local_pos)' in block


def test_wheel_honors_pointer_follow_vdi_and_moves_visible_tree_rows():
    block = ast.get_source_segment(EXPLORER, method(EXPLORER, 'FilesExpWheelTree', 'wheelEvent'))
    follower = ast.get_source_segment(EXPLORER, method(EXPLORER, 'FilesExpWheelTree', '_follow_wheel_pointer'))
    assert 'wheel_steps(' in block
    assert 'super().wheelEvent(event)' in block
    assert block.index('super().wheelEvent(event)') < block.index('wheel_steps(')
    assert 'if before != after:' in block
    assert 'self._select_flow_row' in block
    assert 'can_follow_at_edge(' in block
    assert 'self.indexBelow(new_index)' in block
    assert 'self.indexAbove(new_index)' in block
    assert 'self.setCurrentIndex(new_index)' in block
    assert 'self.pointer_follow_enabled()' in block
    assert 'cursor_target(' in follower
    assert 'QCursor.setPos(dest)' in follower
    assert "'pointer_warp_enabled'" in EXPLORER


def test_page_right_click_uses_same_page_clicked_signal_as_left():
    block = ast.get_source_segment(REMOTE, method(REMOTE, 'LaunchRemote', 'set_pages'))
    assert 'button.clicked.connect(lambda checked=False, pid=page_id:' in block
    assert 'button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)' in block
    assert 'button.customContextMenuRequested.connect(' in block
    assert 'self.page_clicked.emit(pid)' in block
    assert 'self.remote_window.page_clicked.connect(self.open_remote_page)' in APP


def test_current_files_window_behaviors_and_no_filesystem_writes_in_tree():
    assert "self.remote_window.files_exp_folder_selected.connect(self.navigate_files_exp_folder)" in APP
    assert "self.remote_window.files_exp_folder_context.connect(self.show_files_exp_folder_menu)" in APP
    assert 'self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)' in EXPLORER
    for forbidden in ('os.remove(', 'shutil.rmtree(', 'subprocess.', 'os.rename('):
        assert forbidden not in EXPLORER
