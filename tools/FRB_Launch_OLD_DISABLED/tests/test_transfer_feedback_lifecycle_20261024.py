"""New filesystem operation resets only previous paste feedback.

The GUI is verified by executing its actual methods as AST-extracted units;
no PySide6 is required for these behavioral checks.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
CODE = SOURCE.read_text(encoding='utf-8')
MODULE = ast.parse(CODE)
LAUNCHER = next(n for n in MODULE.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')


def function(name, globals_=None):
    fn = next(n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = dict(globals_ or {})
    exec(compile(ast.fix_missing_locations(ast.Module([fn], type_ignores=[])), str(SOURCE), 'exec'), namespace)
    return namespace[name]


def popup(paths, child=None):
    return SimpleNamespace(_pasted_feedback_paths=list(paths),
                           _refresh_transfer_visuals=Mock(), child=child)


def test_clears_all_open_cascade_levels_and_noop_if_empty():
    child = popup(['c:/new/child.txt'])
    root = popup(['c:/new/root.txt'], child=child)
    launcher = SimpleNamespace(menu=root)
    clear = function('_clear_previous_paste_feedback')
    clear(launcher)
    assert root._pasted_feedback_paths == ()
    assert child._pasted_feedback_paths == ()
    root._refresh_transfer_visuals.assert_called_once()
    child._refresh_transfer_visuals.assert_called_once()
    clear(launcher)
    root._refresh_transfer_visuals.assert_called_once()
    child._refresh_transfer_visuals.assert_called_once()


def test_file_copy_or_cut_resets_previous_paste_before_setting_new_clipboard(tmp_path):
    path = tmp_path / 'new.txt'
    path.write_text('x')
    for operation in ('copy', 'cut'):
        popup_ = popup([str(path)])
        clear = function('_clear_previous_paste_feedback')
        clipboard = SimpleNamespace(setMimeData=Mock())
        def set_data(mime):
            assert popup_._pasted_feedback_paths == (), 'old feedback must disappear before new copy/cut'
            clipboard.called = True
        clipboard.setMimeData.side_effect = set_data
        class Mime:
            def setUrls(self, urls): pass
            def setData(self, name, value): pass
        fn = function('perform_filesystem_context_action', {
            'Path': Path, 'QMimeData': Mime, 'QUrl': SimpleNamespace(fromLocalFile=lambda p: p),
            'QApplication': SimpleNamespace(clipboard=lambda: clipboard),
            'DIAG': Mock()
        })
        launcher = SimpleNamespace(menu=popup_, footer=Mock(), error=Mock())
        launcher._clear_previous_paste_feedback = lambda: clear(launcher)
        fn(launcher, operation, str(path), 'file')
        assert clipboard.called
        assert popup_._refresh_transfer_visuals.call_count == 1
        launcher.error.assert_not_called()


def test_new_paste_clears_old_feedback_then_only_marks_new_results(tmp_path):
    source_dir, destination = tmp_path/'source', tmp_path/'destination'
    source_dir.mkdir(); destination.mkdir()
    source = source_dir/'new.txt'
    source.write_text('content')
    popup_ = popup([str(destination/'old.txt')])
    popup_._folder_container_row = lambda: {'launch_browse_target': str(destination)}
    clear = function('_clear_previous_paste_feedback')
    refresh = Mock()
    clipboard = SimpleNamespace(mimeData=lambda: object())
    def paste_items(plan, **kw):
        assert popup_._pasted_feedback_paths == (), 'old paste feedback must clear before new paste'
        return 1
    fn = function('paste_into_directory', {
        'Path': Path, 'QApplication': SimpleNamespace(clipboard=lambda: clipboard),
        'clipboard_sources': lambda mime: [source],
        'is_cut_clipboard': lambda mime: False,
        'is_virtual_file_clipboard': lambda mime: False,
        'make_paste_plan': lambda d, src, allow_existing: [SimpleNamespace(target=d/source.name)],
        'paste_conflicts': lambda plan: [], 'paste_items': paste_items,
        'pasted_paths_for': lambda dest, names: [str(dest/name) for name in names],
        'QTimer': SimpleNamespace(singleShot=lambda _, fn: fn()), 'DIAG': Mock()
    })
    launcher = SimpleNamespace(menu=popup_, expander=lambda: SimpleNamespace(expand=lambda v:v),
                               footer=Mock(), refresh_pasted_directory=refresh, error=Mock())
    launcher._clear_previous_paste_feedback = lambda: clear(launcher)
    fn(launcher, popup_)
    assert popup_._pasted_feedback_paths == [str(destination/'new.txt')]
    refresh.assert_called_once_with(popup_, reopen=True, focus_pasted=True)
    launcher.error.assert_not_called()


def test_clipboard_clearing_is_not_used_to_reset_visual_feedback():
    func = next(n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef)
                and n.name == '_clear_previous_paste_feedback')
    snippet = ast.get_source_segment(CODE, func)
    assert 'QApplication.clipboard()' not in snippet
    assert '.clear()' not in snippet
    assert 'menu._refresh_transfer_visuals()' in snippet
    for method_name in ('perform_filesystem_context_action', 'paste_into_directory'):
        fn = next(n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
        assert "'_clear_previous_paste_feedback'" in ast.get_source_segment(CODE, fn)


def test_new_clipboard_contents_clear_the_previous_paste_color():
    node = next(n for n in MODULE.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == '_on_clipboard_change')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module([fn], type_ignores=[])), str(SOURCE), 'exec'), scope)
    popup_ = popup(['c:/old/pasted.txt'])
    popup_._update_paste_button = Mock()
    scope['_on_clipboard_change'](popup_)
    assert popup_._pasted_feedback_paths == ()
    popup_._update_paste_button.assert_called_once()
    popup_._refresh_transfer_visuals.assert_called_once()
