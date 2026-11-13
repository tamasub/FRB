"""Remote folder-list click refreshes from LIVE breadcrumb, without Qt runtime."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(SOURCE)


def method(cls_name, method_name, globals_=None):
    clazz = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == cls_name)
    function = next(x for x in clazz.body if isinstance(x, ast.FunctionDef) and x.name == method_name)
    env = dict(globals_ or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                 '<extracted>', 'exec'), env)
    return env[method_name]


class FakeRemoteFolderCascade:
    def __init__(self, parent, launcher):
        self.parent, self.launcher = parent, launcher
        self.owner_action = None
        self.open_mode = None
        self.remote_folder_root = None
        self.close = Mock()
        self.deleteLater = Mock()
        self.popup = Mock()
        self.setFocus = Mock()
        self.isVisible = Mock(return_value=True)


def setup(tmp_path, current):
    previous = FakeRemoteFolderCascade('previous', None)
    previous.owner_action = 'folder-action'
    opener = NS(child=previous, actionGeometry=lambda a: NS(top=lambda: 10),
                mapToGlobal=lambda x: x, width=lambda: 260)
    current_ref = {'path': current}
    launcher = NS(expanded_view=NS(current_directory=lambda: current_ref['path']),
                  _remote_folder_root_menu=previous, _remote_folder_source_path=None,
                  _remote_folder_context=Mock(side_effect=lambda p: {'title': p}),
                  fill_cascade=Mock())
    fn = method('Launcher', '_open_remote_folder_cascade', {
        'Path': Path, 'os': os, 'RemoteFolderCascade': FakeRemoteFolderCascade,
        'QPoint': lambda x, y:(x, y)})
    return previous, opener, current_ref, launcher, fn


def test_live_breadcrumb_replaces_visible_column_after_folder_change(tmp_path):
    previous_dir, now = tmp_path / 'old', tmp_path / 'new'
    previous_dir.mkdir()
    now.mkdir()
    previous, opener, current_ref, launcher, fn = setup(tmp_path, previous_dir)
    current_ref['path'] = now
    fn(launcher, opener, 'folder-action', str(previous_dir), 'refresh')
    assert opener.child is not previous
    previous.close.assert_called_once()
    previous.deleteLater.assert_called_once()
    launcher.fill_cascade.assert_called_once_with(opener.child, {'title': str(now)})
    assert launcher._remote_folder_source_path == os.path.normcase(os.path.normpath(str(now)))
    assert launcher._remote_folder_root_menu is opener.child
    opener.child.popup.assert_called_once_with((259, 10))
    opener.child.setFocus.assert_called_once()


def test_same_path_also_recreates_for_changed_contents(tmp_path):
    folder = tmp_path / 'data'
    folder.mkdir()
    previous, opener, _, launcher, fn = setup(tmp_path, folder)
    fn(launcher, opener, 'folder-action', str(folder), 'refresh')
    assert opener.child is not previous
    launcher.fill_cascade.assert_called_once_with(opener.child, {'title': str(folder)})


def test_hover_does_not_replace_already_visible_column(tmp_path):
    folder = tmp_path / 'data'
    folder.mkdir()
    previous, opener, _, launcher, fn = setup(tmp_path, folder)
    fn(launcher, opener, 'folder-action', '/older/path', 'hover')
    assert opener.child is previous
    previous.close.assert_not_called()
    launcher.fill_cascade.assert_not_called()


def test_no_breadcrumb_means_no_stale_refresh(tmp_path):
    previous_dir = tmp_path / 'old'
    previous_dir.mkdir()
    previous, opener, ref, launcher, fn = setup(tmp_path, previous_dir)
    ref['path'] = None
    fn(launcher, opener, 'folder-action', str(previous_dir), 'refresh')
    assert opener.child is previous
    launcher.fill_cascade.assert_not_called()


def test_click_dispatch_is_distinct_from_page_navigation():
    fn = next(n for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'CascadeMenu'
              for n in c.body if isinstance(n, ast.FunctionDef) and n.name == 'mouseReleaseEvent')
    source = ast.get_source_segment(SOURCE, fn)
    assert "getattr(self, 'remote_context_root', False):" in source
    assert "self.openers[action]('refresh')" in source
    assert "self.openers[action]('keyboard')" in source


def test_opener_does_not_capture_stale_path():
    fn = next(n for c in TREE.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher'
              for n in c.body if isinstance(n, ast.FunctionDef) and n.name == 'show_expanded_background_paste_menu')
    source = ast.get_source_segment(SOURCE, fn)
    relevant = source.split('folder_list_action.triggered.connect')[0].split('folder_list_action = menu.addAction')[1]
    assert 'p=directory' not in relevant
    assert 'self._open_remote_folder_cascade(m, a, None, mode)' in source
    assert "menu.openers[a]('refresh')" in source
