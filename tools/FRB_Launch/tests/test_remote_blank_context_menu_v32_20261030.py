"""v32: Remote lower blank strip shares Files column 2 background menu.

No PySide6 required: exercise Qt event routing and Launcher command via small
fakes, and assert the production blank-area menu builder is reused directly.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
REMOTE = (ROOT / 'src' / 'launch_remote.py').read_text(encoding='utf-8')
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
VIEW = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')


def get_method(source, cls, name):
    tree = ast.parse(source)
    klass = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    env = {'QCursor': SimpleNamespace(pos=lambda: 'remote-mouse-pos')}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<method>', 'exec'), env)
    return env[name]


def test_right_click_on_blank_band_emits_only_background_command():
    command = Mock()
    band = SimpleNamespace(command=SimpleNamespace(emit=command))
    event = SimpleNamespace(accept=Mock())
    get_method(REMOTE, 'UpDoubleClickBand', 'contextMenuEvent')(band, event)
    command.assert_called_once_with('BACKGROUND_CONTEXT_MENU')
    event.accept.assert_called_once_with()


def test_remote_reuses_explorer_blank_menu_on_actual_mouse_position():
    window = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
        expanded_view=SimpleNamespace(isVisible=lambda: True,
                                     current_directory=lambda: 'F:/FRB'),
        show_expanded_background_paste_menu=Mock())
    get_method(APP, 'Launcher', 'remote_command')(window, 'BACKGROUND_CONTEXT_MENU')
    window.show_expanded_background_paste_menu.assert_called_once_with('remote-mouse-pos')


def test_remote_blank_menu_not_available_when_files_view_hidden_or_path_missing():
    for expanded, path in [(False, 'F:/FRB'), (True, '')]:
        window = SimpleNamespace(isVisible=lambda: True, isMinimized=lambda: False,
            expanded_view=SimpleNamespace(isVisible=lambda: expanded,
                                         current_directory=lambda: path),
            show_expanded_background_paste_menu=Mock())
        get_method(APP, 'Launcher', 'remote_command')(window, 'BACKGROUND_CONTEXT_MENU')
        window.show_expanded_background_paste_menu.assert_not_called()


def test_double_click_and_existing_blank_menu_remain_unchanged():
    assert "self.command.emit('FOLDER_UP')" in REMOTE
    assert 'root.addWidget(self.up_band)' in REMOTE
    assert 'self.up_band.command.connect(self.command.emit)' in REMOTE
    # The same authoritative menu builder is invoked from Files column 2.
    assert 'self.launcher.show_expanded_background_paste_menu(' in VIEW
    assert "menu.addSeparator()\n        self.expanded_view.add_lane_new_submenu(menu)" in APP
    assert 'self.show_expanded_background_paste_menu(QCursor.pos())' in APP
