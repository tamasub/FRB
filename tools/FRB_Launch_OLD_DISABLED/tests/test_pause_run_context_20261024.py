"""Pause-run: no Qt required; inspect actual wiring and decode command."""
import ast
import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from context_menu_actions import paused_script_command, run_script_with_pause
from context_menu_config import load_context_menus

ROOT = Path(__file__).resolve().parents[1]


def test_context_config_contains_pause_action_for_file_not_folder():
    menus = load_context_menus(ROOT / 'config/context_menu_options.json')
    action = [x for x in menus['file'] if x['action_id'] == 'run_with_pause']
    assert action == [{'action_id': 'run_with_pause', 'title': 'Pause付きで実行'}]
    assert not any(x['action_id'] == 'run_with_pause' for x in menus['folder'])


def test_ui_only_offers_pause_for_ps1_and_py_and_dispatches():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    menu = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'show_launch_context_menu')
    action = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'perform_filesystem_context_action')
    menu_source = ast.get_source_segment(source, menu)
    action_source = ast.get_source_segment(source, action)
    assert "definition['action_id'] == 'run_with_pause'" in menu_source
    assert "Path(path).suffix.casefold() not in ('.ps1', '.py')" in menu_source
    assert "action_id == 'run_with_pause' and kind == 'file'" in action_source
    assert 'run_script_with_pause(path)' in action_source
    icons = (ROOT / 'src/context_menu_icons.py').read_text(encoding='utf-8')
    assert "action_id == 'run_with_pause'" in icons


@pytest.mark.parametrize('extension,runner', [('.ps1', 'powershell.exe -NoProfile -File'),
                                               ('.py', 'py.exe -3'),
                                               ('.PS1', 'powershell.exe -NoProfile -File'),
                                               ('.PY', 'py.exe -3')])
def test_paused_command_is_encoded_unicode_safe_and_finally_waits(extension, runner):
    with TemporaryDirectory(prefix='Pause 実験 ') as folder:
        path = Path(folder) / ("O'Brian & 変な文字 (1)" + extension)
        path.write_text('echo hello', encoding='utf-8')
        argv = paused_script_command(path)
        assert argv[:4] == ['powershell.exe', '-NoProfile', '-NoLogo', '-EncodedCommand']
        text = base64.b64decode(argv[-1]).decode('utf-16-le')
        assert runner in text
        assert str(path.resolve()).replace("'", "''") in text
        assert 'finally {' in text
        assert 'Read-Host' in text
        assert '$LASTEXITCODE' in text
        assert '[終了コード]' in text
        assert 'try {' in text and 'catch {' in text
        expected_dir = "'" + str(path.resolve().parent).replace("'", "''") + "'"
        set_location = 'Set-Location -LiteralPath ' + expected_dir
        assert set_location in text
        assert '[System.Environment]::CurrentDirectory = (Get-Location).ProviderPath' in text
        assert text.index(set_location) < text.index(runner)
        assert text.index('[System.Environment]::CurrentDirectory') < text.index(runner)
        # Display the actual PowerShell working directory after changing it
        # and before running either .py or .ps1. The path printed is data,
        # not a value inferred from the Windows Terminal tab title.
        assert "Write-Host '[実行ファイル]'" in text
        assert "Write-Host '[作業フォルダー]'" in text
        assert 'Write-Host ((Get-Location).ProviderPath)' in text
        assert "Write-Host '-------- 実行開始 --------'" in text
        assert text.index(set_location) < text.index("Write-Host '[実行ファイル]'")
        assert text.index("Write-Host '[実行ファイル]'") < text.index("Write-Host '[作業フォルダー]'")
        assert text.index("Write-Host '[作業フォルダー]'") < text.index(runner)
        assert 'cmd /c' not in text


def test_rejects_non_script_and_missing_script():
    with TemporaryDirectory() as folder:
        txt = Path(folder) / 'oops.txt'
        txt.touch()
        with pytest.raises(ValueError):
            paused_script_command(txt)
        with pytest.raises(FileNotFoundError):
            paused_script_command(Path(folder) / 'missing.ps1')


def test_process_starts_visible_in_script_directory():
    with TemporaryDirectory(prefix='pause root ') as folder:
        target = Path(folder) / 'Hi & テスト.py'
        target.write_text('print("hello")', encoding='utf-8')
        with patch('context_menu_actions._windows_only'), \
             patch('context_menu_actions.subprocess.Popen') as popen, \
             patch('context_menu_actions.subprocess.CREATE_NEW_CONSOLE', 16, create=True):
            run_script_with_pause(target)
        args, kwargs = popen.call_args
        assert args[0][0] == 'powershell.exe'
        assert kwargs['cwd'] == str(target.resolve().parent)
        assert kwargs['creationflags'] == 16
        assert not any(k in kwargs for k in ('stdin', 'stdout', 'stderr'))


def test_real_menu_routes_py_ps1_only_and_file_action_is_not_run_on_open():
    """Extract the real Launcher menu function and exercise it without Qt."""
    from context_menu_resolver import resolve_context_target
    from context_menu_actions import is_downloads_zip
    from types import SimpleNamespace
    from unittest.mock import Mock

    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'show_launch_context_menu')
    code = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(code)

    class Menu:
        def __init__(self, parent):
            self.actions = []
        def addAction(self, title, callback):
            self.actions.append((title, callback))
            return None  # Qt icon methods are tested structurally elsewhere.
        def isEmpty(self):
            return not self.actions
        def popup(self, pos):
            pass

    scope = {'QMenu': Menu, 'Path': Path,
             'resolve_context_target': resolve_context_target,
             'load_context_menus': load_context_menus,
             'CONTEXT_MENU_OPTIONS': ROOT / 'config/context_menu_options.json',
             'is_downloads_zip': is_downloads_zip}
    exec(compile(code, str(ROOT / 'src/app.py'), 'exec'), scope)

    for suffix in ('.py', '.ps1', '.txt', '.bat', '.PY'):
        holder = SimpleNamespace(data={'items': []}, selection=None,
                                 authored_items=[], stack=[],
                                 hover_timer=Mock(), pending_menu_item=None,
                                 perform_filesystem_context_action=Mock())
        row = {'_browse_file': 'C:/test/demo' + suffix, 'item_kind': 'command'}
        assert scope['show_launch_context_menu'](holder, (0, 0), row)
        names = [title for title, _ in holder._launch_context_menu.actions]
        assert ('Pause付きで実行' in names) == (suffix.casefold() in ('.ps1', '.py'))
        if 'Pause付きで実行' in names:
            action = next(cb for name, cb in holder._launch_context_menu.actions
                          if name == 'Pause付きで実行')
            holder.perform_filesystem_context_action.assert_not_called()
            action(True)
            holder.perform_filesystem_context_action.assert_called_once_with(
                'run_with_pause', 'C:/test/demo' + suffix, 'file')
