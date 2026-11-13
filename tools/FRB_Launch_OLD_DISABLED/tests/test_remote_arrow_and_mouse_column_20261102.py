"""Regression for remote menu arrow size and mouse-selected Files column."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1] / 'src'


def _method(filename, klass, method, globs):
    module = ast.parse((ROOT / filename).read_text(encoding='utf-8'))
    parent = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == klass)
    source = next(n for n in parent.body if isinstance(n, ast.FunctionDef) and n.name == method)
    code = compile(ast.Module(body=[source], type_ignores=[]), str(ROOT / filename), 'exec')
    scope = dict(globs)
    exec(code, scope)
    return scope[method]


class Queue:
    def __init__(self):
        self.pending = []

    def singleShot(self, delay, callback):
        assert delay == 0
        self.pending.append(callback)


def test_first_middle_mouse_press_moves_remote_area_without_synthetic_click():
    queue = Queue()
    fn = _method('expanded_view.py', 'ExpandedLauncherView',
                 '_sync_remote_area_after_mouse_press', {'QTimer': queue})
    seen = []
    remote = NS(isVisible=lambda: True)
    launcher = NS(remote_window=remote, _remote_area='files',
                  remote_focus_area=lambda area: seen.append(area))
    view = NS(launcher=launcher, isVisible=lambda: True, _workspace_mode='files')
    fn(view, 'directory')
    assert seen == []  # Qt must finish mouse/selection handling first.
    assert len(queue.pending) == 1
    queue.pending.pop()()
    assert seen == ['directory']


def test_mouse_column_sync_does_not_override_newer_remote_navigation():
    queue = Queue()
    fn = _method('expanded_view.py', 'ExpandedLauncherView',
                 '_sync_remote_area_after_mouse_press', {'QTimer': queue})
    seen = []
    remote = NS(isVisible=lambda: True)
    launcher = NS(remote_window=remote, _remote_area='files',
                  remote_focus_area=lambda area: seen.append(area))
    view = NS(launcher=launcher, isVisible=lambda: True, _workspace_mode='files')
    fn(view, 'directory')
    launcher._remote_area = 'directory'  # Already changed by another handler.
    queue.pending.pop()()
    assert seen == []
    fn(view, 'files')
    remote.isVisible = lambda: False
    queue.pending.pop()()
    assert seen == []


def test_mouse_pane_hooks_are_on_press_not_double_click():
    source = (ROOT / 'expanded_view.py').read_text(encoding='utf-8')
    assert "self.middle.tree.itemPressed.connect(" in source
    assert "self._sync_remote_area_after_mouse_press('directory')" in source
    assert "self.left.tree.itemPressed.connect(" in source
    assert "self._sync_remote_area_after_mouse_press('files')" in source


def test_new_and_folder_list_share_arrow_geometry_and_paint_path():
    code = (ROOT / 'app.py').read_text(encoding='utf-8')
    cls = code.split('class RemoteFolderActionsMenu(CascadeMenu):', 1)[1].split(
        'class RemoteFolderCascade(CascadeMenu):', 1)[0]
    assert "getattr(self, 'folder_list_action', None)" in cls
    assert "getattr(self, 'new_submenu_action', None)" in cls
    assert cls.count('arrow.moveTo(') == 1
    assert cls.count('arrow.lineTo(') == 2
    assert 'painter.fillRect(QRect(' in cls  # Covers the larger native Qt arrow.
    assert 'painter.fillPath(arrow, color)' in cls
    assert 'menu.new_submenu_action = new_submenu.menuAction()' in code
    assert 'new_submenu = self.expanded_view.add_lane_new_submenu(' in code
