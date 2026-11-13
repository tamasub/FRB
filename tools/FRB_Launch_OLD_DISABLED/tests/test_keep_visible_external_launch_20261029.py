"""Regression: normal-window mode never hides Launch when opening external files.

AST-isolated tests execute the actual Launcher methods without requiring Qt or Windows.
Run: PYTHONPATH=src python -m pytest -q tests/test_keep_visible_external_launch_20261029.py
"""
import ast
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from process_runner import should_start_before_dismiss

ROOT = Path(__file__).resolve().parents[1]


def method(name, scope=None):
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    klass = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == 'Launcher')
    node = next(node for node in klass.body if isinstance(node, ast.FunctionDef)
                and node.name == name)
    ns = dict(scope or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 'src/app.py', 'exec'), ns)
    return ns[name]


@pytest.mark.parametrize('mode', [False, True])
@pytest.mark.parametrize('action', [
    {'launch_action_type': 'Run', 'launch_program': 'FRBStudio.NativeShell.exe'},
    {'launch_action_type': 'Run', 'launch_program': 'build.bat', 'launch_show_console': True},
    {'launch_action_type': 'Run', 'launch_program': 'build.cmd', 'launch_wait_for_exit': True},
    {'launch_action_type': 'Open', 'launch_target': 'C:/work/日本語.txt'},
    {'launch_action_type': 'Open', 'launch_target': 'https://example.org'},
])
def test_launch_paths_respect_display_mode(mode, action):
    events = []
    callbacks = []
    scope = {
        'DIAG': logging.getLogger('keep-visible-test'),
        'should_start_before_dismiss': should_start_before_dismiss,
        'QTimer': SimpleNamespace(singleShot=lambda ms, cb: callbacks.append((ms, cb))),
        'file_index': SimpleNamespace(route_registered_open_step=lambda step, studio: [step]),
    }
    execute = method('execute', scope)
    launcher = SimpleNamespace(
        busy=False, data={}, dismiss_on_outside_click=mode,
        expander=lambda values: SimpleNamespace(values={}, expand=lambda value: value),
        next_step=lambda: events.append('run'),
        dismiss=lambda: events.append('hide'),
        error=Mock(),
    )
    execute(launcher, {'item_id': 'x', 'title': 'open', 'launch_actions': [action]})
    if action['launch_action_type'] == 'Run' and should_start_before_dismiss([action]):
        assert events == (['run', 'hide'] if mode else ['run'])
        assert callbacks == []
        assert launcher._foreground_handoff_pending is True
    else:
        assert events == (['hide'] if mode else [])
        assert len(callbacks) == 1
        assert callbacks[0][0] == (180 if mode else 0)
        callbacks[0][1]()
        assert events == (['hide', 'run'] if mode else ['run'])
    launcher.error.assert_not_called()


@pytest.mark.parametrize('mode', [False, True])
def test_selected_open_with_app_retains_normal_window(tmp_path, mode):
    filename = tmp_path / '設定.json'
    executable = tmp_path / 'editor.exe'
    filename.write_text('{}', encoding='utf-8')
    executable.write_bytes(b'fake exe')
    events = []
    fn = method('open_file_with_selected_app', {
        'Path': Path,
        'open_file_with_app': lambda path, exe: events.append(('open', path, exe)),
    })
    launcher = SimpleNamespace(
        dismiss_on_outside_click=mode,
        dismiss=lambda: events.append('hide'), error=Mock())
    fn(launcher, str(filename), str(executable))
    assert events == (["hide"] if mode else []) + [('open', str(filename), str(executable))]
    launcher.error.assert_not_called()


@pytest.mark.parametrize('mode', [False, True])
def test_native_open_with_dialog_retains_normal_window(tmp_path, mode):
    filename = tmp_path / '記録.md'
    filename.write_text('data', encoding='utf-8')
    events = []
    fn = method('perform_filesystem_context_action', {
        'Path': Path, 'DIAG': logging.getLogger('keep-visible-test'),
        'open_with_windows_dialog': lambda path: events.append(('chooser', path)),
    })
    launcher = SimpleNamespace(
        dismiss_on_outside_click=mode,
        dismiss=lambda: events.append('hide'), error=Mock(),
    )
    fn(launcher, 'open_with', str(filename), 'file')
    assert events == (['hide'] if mode else []) + [('chooser', filename)]
    launcher.error.assert_not_called()


def test_run_with_pause_is_already_keep_visible(tmp_path):
    filename = tmp_path / 'コンパイル.ps1'
    filename.write_text('echo test', encoding='utf-8')
    launched = []
    fn = method('perform_filesystem_context_action', {
        'Path': Path, 'DIAG': logging.getLogger('keep-visible-test'),
        'run_script_with_pause': lambda path: launched.append(path),
    })
    launcher = SimpleNamespace(dismiss_on_outside_click=False,
                               dismiss=Mock(), error=Mock())
    fn(launcher, 'run_with_pause', str(filename), 'file')
    assert launched == [filename]
    launcher.dismiss.assert_not_called()
    launcher.error.assert_not_called()
