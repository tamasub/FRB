"""Windows-native Open With chooser, without duplicating Explorer app discovery."""
import ast
import ctypes
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from context_menu_actions import open_with_windows_dialog
from context_menu_config import load_context_menus

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/context_menu_options.json'


def test_file_only_new_action_is_declared_in_json_and_allowlist():
    menus = load_context_menus(CONFIG)
    files = [v.get('action_id') for v in menus['file'] if v.get('action_id')]
    folders = [v.get('action_id') for v in menus['folder'] if v.get('action_id')]
    assert files.count('open_with') == 1
    assert 'open_with' not in folders
    assert next(e['title'] for e in menus['file'] if e.get('action_id') == 'open_with') == 'プログラムから開く…'
    assert files.index('open_with') < files.index('open_parent_folder')


def test_native_dialog_uses_windows_app_selection_once_without_file_association_change(tmp_path):
    filename = tmp_path / 'my test (1) 日本語 & space.json'
    filename.write_text('{}', encoding='utf-8')
    fake_choose = Mock(return_value=0)
    fake_dll = SimpleNamespace(SHOpenWithDialog=fake_choose)
    with patch('context_menu_actions._windows_only'), patch('context_menu_actions.ctypes.WinDLL',
                                                             return_value=fake_dll, create=True):
        result = open_with_windows_dialog(filename)
    assert result is True
    (hwnd, pointer), = [call.args for call in fake_choose.call_args_list]
    assert hwnd is None
    info = pointer._obj
    assert info.pcszFile == str(filename.resolve())
    assert info.pcszClass is None
    assert info.oaifInFlags & 0x4  # OAIF_EXEC: selected app opens this file
    assert not info.oaifInFlags & 0x2  # OAIF_REGISTER_EXT: DO NOT change default app


def test_native_dialog_handles_cancel_without_error(tmp_path):
    filename = tmp_path / 'data.json'
    filename.write_text('{}', encoding='utf-8')
    fake_choose = Mock(return_value=ctypes.c_long(0x800704c7).value)
    with patch('context_menu_actions._windows_only'), patch('context_menu_actions.ctypes.WinDLL',
                                                             return_value=SimpleNamespace(SHOpenWithDialog=fake_choose), create=True):
        assert open_with_windows_dialog(filename) is False


def test_native_dialog_rejects_missing_file_and_folder(tmp_path):
    with patch('context_menu_actions._windows_only'):
        with pytest.raises(FileNotFoundError):
            open_with_windows_dialog(tmp_path / 'absent.json')
        with pytest.raises(FileNotFoundError):
            open_with_windows_dialog(tmp_path)


def test_launcher_dispatch_invokes_native_helper_only_for_file(tmp_path):
    src = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    parsed = ast.parse(src)
    cls = next(item for item in parsed.body if isinstance(item, ast.ClassDef) and item.name == 'Launcher')
    fn = next(item for item in cls.body if isinstance(item, ast.FunctionDef)
              and item.name == 'perform_filesystem_context_action')
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    scope = {'Path': Path, 'open_with_windows_dialog': Mock(), 'DIAG': Mock()}
    exec(compile(module, '<isolated launcher action>', 'exec'), scope)
    filename = tmp_path / '設定 & data.json'
    filename.write_text('{}', encoding='utf-8')
    owner = SimpleNamespace(_clear_previous_paste_feedback=Mock(), dismiss=Mock(), error=Mock())
    scope['perform_filesystem_context_action'](owner, 'open_with', str(filename), 'file')
    owner.dismiss.assert_called_once_with()
    scope['open_with_windows_dialog'].assert_called_once_with(filename)
    owner.error.assert_not_called()
