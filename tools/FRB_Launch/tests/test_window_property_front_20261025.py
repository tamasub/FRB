"""Native property sheets must appear after the topmost launcher is dismissed."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method(name, scope):
    root = ast.parse(TEXT)
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    code = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    namespace = dict(scope)
    exec(compile(code, '<app.py>', 'exec'), namespace)
    return namespace[name]


def test_file_properties_dismisses_topmost_launcher_before_native_sheet(tmp_path):
    candidate = tmp_path / 'sample.txt'
    candidate.write_text('sample', encoding='utf-8')
    calls = []
    launcher = SimpleNamespace(
        dismiss=lambda: calls.append('hide-launcher'),
        error=Mock(),
        _clear_previous_paste_feedback=lambda: calls.append('clear-highlight'),
    )
    fn = method('perform_filesystem_context_action', {
        'Path': Path,
        'show_windows_properties': lambda path: calls.append(('native-properties', path)),
        'DIAG': Mock(),
    })
    fn(launcher, 'properties', str(candidate), 'file')
    assert calls == ['clear-highlight', 'hide-launcher', ('native-properties', candidate)]
    launcher.error.assert_not_called()


def test_folder_properties_dismisses_topmost_launcher_too(tmp_path):
    calls = []
    launcher = SimpleNamespace(dismiss=lambda: calls.append('hide'), error=Mock())
    fn = method('perform_filesystem_context_action', {
        'Path': Path, 'show_windows_properties': lambda path: calls.append('properties'),
        'DIAG': Mock()})
    fn(launcher, 'properties', str(tmp_path), 'folder')
    assert calls == ['hide', 'properties']
