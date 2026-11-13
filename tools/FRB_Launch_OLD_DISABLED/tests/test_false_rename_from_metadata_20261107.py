"""Regression: QTreeWidget.itemChanged is not proof of a filename edit.

Qt can emit itemChanged for icon/size/flags updates.  PC drive labels
are deliberately not equal to their physical path basename, so treating
those updates as a rename attempts to use 'C:' in a Windows filename.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from context_menu_resolver import resolve_context_target


def isolated_finish():
    module = ast.parse((ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8'))
    owner = next(node for node in module.body if isinstance(node, ast.ClassDef)
                 and node.name == 'ExpandedLauncherView')
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'finish_inline_rename')
    def unexpected_rename(*args, **kwargs):
        raise AssertionError('Metadata change must not invoke a filesystem rename')
    namespace = dict(Path=Path, resolve_context_target=resolve_context_target,
                     rename_file_or_folder=unexpected_rename)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated>', 'exec'), namespace)
    return namespace['finish_inline_rename']


def make_view(row):
    messages = []
    launcher = NS(authored_items=(), error=messages.append,
                  footer=NS(setText=messages.append))
    return NS(row_data=lambda item: row, launcher=launcher), messages


def test_pc_drive_label_metadata_refresh_is_not_a_rename():
    row = {'_file': 'F:\\', 'title': 'ローカル ディスク (F:)',
           'item_kind': 'directory', '_system_drive': True}
    view, messages = make_view(row)
    item = NS(text=lambda _: 'ローカル ディスク (F:)')
    isolated_finish()(view, item, 0)  # Qt icon / size / flags notification
    assert messages == []


def test_non_file_display_label_metadata_refresh_is_not_a_rename(tmp_path):
    file = tmp_path / 'sample.txt'
    file.write_text('original', encoding='utf-8')
    row = {'_file': str(file), 'title': '表示用:sample.txt', 'item_kind': 'command'}
    view, messages = make_view(row)
    item = NS(text=lambda _: '表示用:sample.txt')
    isolated_finish()(view, item, 0)
    assert messages == []
    assert file.read_text(encoding='utf-8') == 'original'


def test_drive_rename_remains_prohibited_even_if_text_changes():
    row = {'_file': 'F:\\', 'title': 'ローカル ディスク (F:)',
           'item_kind': 'directory', '_system_drive': True}
    view, messages = make_view(row)
    item = NS(text=lambda _: 'other-name')
    isolated_finish()(view, item, 0)
    assert messages == []


def test_user_edited_filename_still_renames(tmp_path):
    from context_menu_actions import rename_file_or_folder
    source = tmp_path / 'before.txt'
    source.write_text('test', encoding='utf-8')
    updated = []
    row = {'_file': str(source), 'title': source.name, 'item_kind': 'command'}
    view, messages = make_view(row)
    view.refresh_middle = lambda: updated.append('refresh')
    view.select_created_middle_item = lambda path: updated.append(path)
    module = ast.parse((ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8'))
    owner = next(node for node in module.body if isinstance(node, ast.ClassDef)
                 and node.name == 'ExpandedLauncherView')
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'finish_inline_rename')
    namespace = dict(Path=Path, resolve_context_target=resolve_context_target,
                     rename_file_or_folder=rename_file_or_folder,
                     QTimer=NS(singleShot=lambda delay, fn: fn()))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated>', 'exec'), namespace)
    namespace['finish_inline_rename'](view, NS(text=lambda _: 'after.txt'), 0)
    assert not source.exists()
    assert (tmp_path / 'after.txt').read_text(encoding='utf-8') == 'test'
    assert updated == ['refresh', tmp_path / 'after.txt']
    assert messages == ['名前を変更しました: before.txt → after.txt']
