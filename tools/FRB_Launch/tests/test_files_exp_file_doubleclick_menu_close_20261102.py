"""Files Exp > Filesリスト: opening a file closes its entire context cascade.

Qt-free tests exercise the real source methods. Windows/Qt GUI still needs a
manual double-click check because PySide6 is not installed in this runner.
"""

import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

APP = Path(__file__).resolve().parents[1] / 'src' / 'app.py'


def source_method(owner, name, scope):
    module = ast.parse(APP.read_text(encoding='utf-8'))
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == owner)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    fake = ast.Module(body=[method], type_ignores=[])
    exec(compile(ast.fix_missing_locations(fake), str(APP), 'exec'), scope)
    return scope[name]


def setup_activate():
    deferred = []
    scope = {
        'Path': Path,
        'QTimer': NS(singleShot=lambda interval, callback: deferred.append((interval, callback))),
    }
    return source_method('RemoteFolderCascade', '_remote_activate_file', scope), deferred


def test_file_launch_dismisses_all_menus_after_mouse_event(tmp_path):
    launch, deferred = setup_activate()
    filename = tmp_path / 'example.txt'
    filename.write_text('ok', encoding='utf-8')
    events = []
    launcher = NS(
        activate=lambda row: events.append(('activate', row['_browse_file'])),
        close_finished_file_context_menus=lambda: events.append(('close-all', None)),
    )
    launch(NS(launcher=launcher), {'_browse_file': str(filename)})
    assert events == [('activate', str(filename))]
    assert len(deferred) == 1
    assert deferred[0][0] == 0
    deferred.pop()[1]()
    assert events == [('activate', str(filename)), ('close-all', None)]


def test_nonexistent_file_never_closes_folder_navigation(tmp_path):
    launch, deferred = setup_activate()
    owner = NS(launcher=NS(activate=Mock(), close_finished_file_context_menus=Mock()))
    launch(owner, {'_browse_file': str(tmp_path / 'does_not_exist.txt')})
    assert not deferred
    owner.launcher.activate.assert_not_called()
    owner.launcher.close_finished_file_context_menus.assert_not_called()


def test_failed_launch_still_dismisses_finished_command(tmp_path):
    launch, deferred = setup_activate()
    filename = tmp_path / 'bad.txt'
    filename.write_text('ok', encoding='utf-8')
    def fail(row):
        raise OSError('cannot start')
    owner = NS(launcher=NS(activate=fail, close_finished_file_context_menus=Mock()))
    try:
        launch(owner, {'_browse_file': str(filename)})
    except OSError:
        pass
    else:
        assert False, 'launch error must propagate normally'
    assert len(deferred) == 1
    deferred[0][1]()
    owner.launcher.close_finished_file_context_menus.assert_called_once_with()


def test_non_scroll_and_scroll_double_click_share_single_launch_method():
    text = APP.read_text(encoding='utf-8')
    module = ast.parse(text)
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
               and n.name == 'RemoteFolderCascade')
    methods = {n.name: ast.get_source_segment(text, n) for n in cls.body
               if isinstance(n, ast.FunctionDef)}
    assert "lambda r=dbl: self._remote_activate_file(r)" in methods['mouseReleaseEvent']
    assert "lambda r=row: self._remote_activate_file(r)" in methods['_scroll_double_clicked']
    assert 'close_finished_file_context_menus' in methods['_remote_activate_file']


def test_closer_dismisses_both_right_click_opener_and_folder_columns():
    scope = {}
    close = source_method('Launcher', 'close_finished_file_context_menus', scope)
    seen = []
    context = NS(close=lambda: seen.append('context'))
    cascade = NS(isVisible=lambda:True, close=lambda: seen.append('other-cascade'))
    launcher = NS(_launch_context_menu=context, _remote_page_menu=None,
                  menu=cascade, close_remote_folder_menu=lambda: seen.append('folder-root'))
    close(launcher)
    assert seen == ['context', 'folder-root', 'other-cascade']
    assert launcher._launch_context_menu is None
