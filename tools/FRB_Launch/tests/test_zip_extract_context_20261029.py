"""ZIP-only Extract All behavior, existing menu routing and extraction safety."""
import ast
import json
import os
import stat
import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from zipfile import ZipFile, ZipInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_config import load_context_menus, visible_context_entries
from zip_extract_action import (
    default_extract_destination, invoke_windows_extract_all,
    is_extractable_zip, safe_extract_zip,
)


def _launcher_methods():
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    launcher = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    return {n.name: n for n in launcher.body if isinstance(n, ast.FunctionDef)}


def test_only_file_menu_has_extract_all_action():
    config = load_context_menus(ROOT / 'config/context_menu_options.json')
    action = next(e for e in config['file'] if e.get('action_id') == 'extract_all')
    assert action['title'] == 'すべて展開...'
    assert all(e.get('action_id') != 'extract_all' for e in config['folder'])
    # Existence/file suffix are guarded by both the menu and the handler.
    menu_src = ast.get_source_segment((ROOT / 'src/app.py').read_text(encoding='utf-8'),
                                      _launcher_methods()['show_launch_context_menu'])
    assert "d['action_id'] == 'extract_all' and Path(path).suffix.casefold() != '.zip'" in menu_src
    dispatch_src = ast.get_source_segment((ROOT / 'src/app.py').read_text(encoding='utf-8'),
                                          _launcher_methods()['perform_filesystem_context_action'])
    assert "action_id == 'extract_all' and kind == 'file'" in dispatch_src
    assert 'self.extract_all_zip(path)' in dispatch_src
    assert "'extract_all'" not in (ROOT / 'src/context_menu_config.py').read_text(encoding='utf-8').split("'folder': frozenset(", 1)[1].split(')),', 1)[0]


def test_existing_menu_routes_zip_only():
    from test_context_menu_filesystem import ActualLauncherRoutingTests
    routing, context = ActualLauncherRoutingTests.setup()
    assert routing(context, (1, 1), {'_indexed_file': 'C:/work/test .ZIP'})
    names = [n for n, _ in context._launch_context_menu.actions]
    assert 'すべて展開...' in names
    callback = next(cb for title, cb in context._launch_context_menu.actions
                    if title == 'すべて展開...')
    callback(True)
    context.perform_filesystem_context_action.assert_called_once_with(
        'extract_all', 'C:/work/test .ZIP', 'file')
    context.perform_filesystem_context_action.reset_mock()
    assert routing(context, (1, 1), {'_indexed_file': 'C:/work/readme.txt'})
    assert 'すべて展開...' not in [n for n, _ in context._launch_context_menu.actions]


def test_file_kind_and_default_folder():
    with TemporaryDirectory() as root:
        path = Path(root) / '資料 & (test).ZIP'
        with ZipFile(path, 'w') as archive:
            archive.writestr('doc.txt', 'hello')
        assert is_extractable_zip(path)
        assert default_extract_destination(path) == Path(root) / '資料 & (test)'
        assert not is_extractable_zip(Path(root))
        assert not is_extractable_zip(Path(root) / 'not-here.zip')
        assert not is_extractable_zip(Path(root) / 'file.7z')


def test_safe_zip_extract_and_never_overwrite_existing():
    with TemporaryDirectory() as root:
        path = Path(root) / '日本語 & space.zip'
        with ZipFile(path, 'w') as archive:
            archive.writestr('foo/日本語.txt', 'data')
        destination = Path(root) / 'extracted'
        assert safe_extract_zip(path, destination) == destination
        assert (destination / 'foo/日本語.txt').read_text() == 'data'
        with pytest.raises(FileExistsError):
            safe_extract_zip(path, destination)
        assert path.exists()


@pytest.mark.parametrize('bad_name', [
    '../outside.txt', '/absolute.txt', 'D:/drive.txt',
    'foo\\..\\out.txt', 'CON.txt', 'folder/secret?.txt',
])
def test_traversal_or_invalid_windows_paths_rejected(bad_name):
    with TemporaryDirectory() as root:
        path = Path(root) / 'unsafe.zip'
        with ZipFile(path, 'w') as archive:
            archive.writestr(bad_name, 'data')
        with pytest.raises(ValueError):
            safe_extract_zip(path, Path(root) / 'dest')
        assert not (Path(root) / 'outside.txt').exists()


def test_reject_duplicate_case_and_symlink_and_file_parent_collision():
    with TemporaryDirectory() as root:
        root = Path(root)
        for index, names in enumerate((('A.txt','a.TXT'), ('foo/bar.txt','foo'))):
            path = root / f'collision-{index}.zip'
            with ZipFile(path, 'w') as archive:
                for name in names: archive.writestr(name, name)
            with pytest.raises(ValueError):
                safe_extract_zip(path, root / f'collision-{index}')
        path = root / 'symlink.zip'
        with ZipFile(path, 'w') as archive:
            link = ZipInfo('link')
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link, 'outside')
        with pytest.raises(ValueError):
            safe_extract_zip(path, root / 'link_dest')


def test_native_is_only_for_windows_and_does_not_change_files():
    with TemporaryDirectory() as root:
        path = Path(root) / 'demo.zip'
        with ZipFile(path, 'w') as archive:
            archive.writestr('name.txt', 'hello')
        if os.name != 'nt':
            assert invoke_windows_extract_all(path) is False
        assert path.exists()


def test_fallback_dialog_is_explicit_and_never_auto_extracts_on_menu_open():
    ui_src = ast.get_source_segment((ROOT / 'src/app.py').read_text(encoding='utf-8'),
                                    _launcher_methods()['extract_all_zip'])
    assert 'if dialog.exec() != QDialog.DialogCode.Accepted:' in ui_src
    assert 'safe_extract_zip(path, dest_text)' in ui_src
    assert 'QFileDialog.getExistingDirectory' in ui_src
    assert 'invoke_windows_extract_all(path)' in ui_src
