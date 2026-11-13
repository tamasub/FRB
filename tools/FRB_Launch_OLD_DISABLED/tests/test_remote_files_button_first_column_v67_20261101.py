"""v67/v68: Files-button right click opens Files column 1 roots.

Keep this Qt-free: assert source contracts and simple extracted methods only.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')


def method(source, class_name, name, env=None):
    tree = ast.parse(source)
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == class_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<method>', 'exec'), scope)
    return scope[name]


def test_files_button_has_dedicated_right_click_entrypoint():
    init = ast.get_source_segment(REMOTE, next(n for n in next(c for c in ast.parse(REMOTE).body
        if isinstance(c, ast.ClassDef) and c.name == 'LaunchRemote').body
        if isinstance(n, ast.FunctionDef) and n.name == '__init__'))
    assert "Files画面へ切り替え / 右クリック：第1列から開く" in init
    assert "self.files_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)" in init
    assert "self.command.emit('REMOTE_FILES_FIRST_COLUMN_MENU')" in init


def test_remote_command_dispatches_new_files_button_menu():
    source = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'remote_command'))
    assert "if command == 'REMOTE_FILES_FIRST_COLUMN_MENU':" in source
    assert 'self.show_remote_files_first_column_menu()' in source


def test_show_remote_files_first_column_menu_builds_direct_remote_folder_cascade():
    source = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'show_remote_files_first_column_menu'))
    assert 'RemoteFolderCascade(parent=self, launcher=self)' in source
    assert 'menu.remote_folder_navigation = True' in source
    assert 'menu.remote_folder_root = menu' in source
    assert "'launch_source': 'remote_files_roots'" in source
    assert 'menu.remote_files_roots = True' in source


def test_shared_remote_popup_bounds_are_applied_to_root_and_children():
    popup = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'CascadeMenu').body
        if isinstance(n, ast.FunctionDef) and n.name == 'popup'))
    assert "popup_bounds = getattr(self, 'remote_popup_bounds', None)" in popup
    assert 'bound_top = popup_bounds[0]' in popup
    assert 'bound_bottom = popup_bounds[1]' in popup
    fill = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'fill_cascade'))
    assert "if hasattr(m, 'remote_popup_bounds'):" in fill
    assert 'm.child.remote_popup_bounds = m.remote_popup_bounds' in fill
    blank = ast.get_source_segment(APP, next(n for n in next(c for c in ast.parse(APP).body
        if isinstance(c, ast.ClassDef) and c.name == 'Launcher').body
        if isinstance(n, ast.FunctionDef) and n.name == 'show_expanded_background_paste_menu'))
    assert 'menu = self._apply_remote_popup_bounds(menu)' in blank


def test_remote_popup_vertical_bounds_use_files_row_to_remote_bottom_band():
    fn = method(APP, 'Launcher', '_remote_popup_vertical_bounds', {'QPoint': lambda x, y: (x, y)})

    class Widget:
        def __init__(self, y):
            self._y = y
        def mapToGlobal(self, point):
            return NS(y=lambda: self._y + point[1])
        def height(self):
            return 210
        def isVisible(self):
            return True

    remote = NS(isVisible=lambda: True, files_button=Widget(100), mapToGlobal=lambda point: NS(y=lambda: 50 + point[1]), height=lambda: 210)
    launcher = NS(remote_window=remote)
    assert fn(launcher) == (99, 564)  # 3x the previous vertical reach


def test_show_remote_files_first_column_menu_ignores_hidden_remote_or_view():
    fn = method(APP, 'Launcher', 'show_remote_files_first_column_menu')
    for remote_visible, view_visible in ((False, True), (True, False)):
        view = NS(isVisible=lambda: view_visible, show_files_view=Mock())
        launcher = NS(
            remote_window=NS(isVisible=lambda: remote_visible),
            expanded_view=view,
            close_remote_folder_menu=Mock(),
            close_remote_page_menu=Mock(),
        )
        fn(launcher)
        view.show_files_view.assert_not_called()
        launcher.close_remote_folder_menu.assert_not_called()
        launcher.close_remote_page_menu.assert_not_called()
