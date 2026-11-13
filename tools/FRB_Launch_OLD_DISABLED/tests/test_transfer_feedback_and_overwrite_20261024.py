"""Regression for explicit overwrite, folder merge and cut/paste UI state."""
from pathlib import Path
import ast

import pytest

from sys import path as _sys_path
_sys_path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from clipboard_paste import make_paste_plan, paste_items, paste_conflicts
from file_transfer_visual import transfer_state, pasted_paths_for
from virtual_clipboard_paste import preflight_virtual_destination


def test_replace_only_after_explicit_opt_in(tmp_path):
    source, destination = tmp_path/'src', tmp_path/'dst'
    source.mkdir(); destination.mkdir()
    (source/'a.txt').write_text('new')
    (destination/'a.txt').write_text('old')
    with pytest.raises(FileExistsError):
        make_paste_plan(destination, [source/'a.txt'])
    plan = make_paste_plan(destination, [source/'a.txt'], allow_existing=True)
    assert [p.name for p in paste_conflicts(plan)] == ['a.txt']
    with pytest.raises(FileExistsError):
        paste_items(plan)
    assert (destination/'a.txt').read_text() == 'old'
    assert paste_items(plan, overwrite=True) == 1
    assert (destination/'a.txt').read_text() == 'new'
    assert (source/'a.txt').read_text() == 'new'


def test_merge_directory_retains_unrelated_files(tmp_path):
    source, destination = tmp_path/'src', tmp_path/'dst'
    (source/'folder').mkdir(parents=True)
    (destination/'folder').mkdir(parents=True)
    (source/'folder'/'replace.txt').write_text('new')
    (destination/'folder'/'replace.txt').write_text('old')
    (destination/'folder'/'other.txt').write_text('keep')
    assert paste_items(make_paste_plan(destination, [source/'folder'], allow_existing=True), overwrite=True) == 1
    assert (destination/'folder'/'replace.txt').read_text() == 'new'
    assert (destination/'folder'/'other.txt').read_text() == 'keep'


def test_confirmed_move_overwrites_file_and_removes_cut_source(tmp_path):
    source, destination = tmp_path/'src', tmp_path/'dst'
    source.mkdir();destination.mkdir()
    (source/'a.txt').write_text('new')
    (destination/'a.txt').write_text('old')
    plan = make_paste_plan(destination, [source/'a.txt'], allow_existing=True)
    assert paste_items(plan, overwrite=True, move=True) == 1
    assert not (source/'a.txt').exists()
    assert (destination/'a.txt').read_text() == 'new'


def test_folders_versus_files_cannot_replace(tmp_path):
    source, destination = tmp_path/'src', tmp_path/'dst'
    source.mkdir();destination.mkdir()
    (source/'a').write_text('contents')
    (destination/'a').mkdir()
    with pytest.raises(ValueError, match='種類'):
        make_paste_plan(destination, [source/'a'], allow_existing=True)


def test_virtual_clipboard_collisions_need_confirmation(tmp_path):
    (tmp_path/'a').mkdir()
    with pytest.raises(FileExistsError):
        preflight_virtual_destination(tmp_path, ['a'])
    preflight_virtual_destination(tmp_path, ['a'], allow_existing=True)


def test_cut_and_pasted_visual_states_have_separate_semantics(tmp_path):
    cut = tmp_path/'cut.txt'
    pasted = pasted_paths_for(tmp_path, ['new.txt', 'folder'])
    assert transfer_state(cut, cut_paths=[cut]) == 'cut'
    assert transfer_state(tmp_path/'new.txt', pasted_paths=pasted) == 'pasted'
    assert transfer_state(tmp_path/'folder', pasted_paths=pasted) == 'pasted'
    assert transfer_state(tmp_path/'else.txt', pasted_paths=pasted, cut_paths=[cut]) == ''


def test_ui_routes_modal_delete_back_to_same_column():
    src = (Path(__file__).resolve().parents[1] / 'src'/'app.py').read_text(encoding='utf-8')
    assert "self._filesystem_dialog_depth" in src
    assert "self.refresh_deleted_directory(m)" in src
    assert "menu._pasted_feedback_paths = pasted_paths_for(destination, names_done)" in src
    assert "self._refresh_transfer_visuals()" in src
    assert "state == 'cut'" in src and "state == 'pasted'" in src
    ast.parse(src)


def test_delete_refreshes_open_folder_instead_of_closing(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import Mock
    path = tmp_path / 'gone.txt'
    path.write_text('hello')
    src = (Path(__file__).resolve().parents[1] / 'src'/'app.py').read_text(encoding='utf-8')
    launcher = next(c for c in ast.parse(src).body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
    fn = next(f for f in launcher.body if isinstance(f, ast.FunctionDef)
              and f.name == 'perform_filesystem_context_action')
    class QMessageBox:
        class StandardButton:
            Yes = 1
            No = 2
        @staticmethod
        def question(*args):
            return 1
    class QTimer:
        @staticmethod
        def singleShot(_, callback):
            callback()
    recycle = Mock(side_effect=lambda p: p.unlink())
    namespace = {'Path': Path, 'QMessageBox': QMessageBox, 'QTimer': QTimer,
                 'move_to_recycle_bin': recycle, 'path_key': lambda p: str(p),
                 'DIAG': Mock()}
    exec(compile(ast.fix_missing_locations(ast.Module([fn], [])), 'app.py', 'exec'), namespace)
    cascade = object()
    launcher_proxy = SimpleNamespace(_directory_menu_for_path=lambda folder: cascade,
                    hover_timer=Mock(), file_index_busy=False,
                    file_index_settings={'enabled':False}, footer=Mock(),
                    render=Mock(), close_cascade_for_main_interaction=Mock(),
                    refresh_pasted_directory=Mock(), refresh_deleted_directory=Mock(), error=Mock())
    namespace['perform_filesystem_context_action'](launcher_proxy, 'delete', str(path), 'file')
    recycle.assert_called_once()
    assert not path.exists()
    launcher_proxy.refresh_deleted_directory.assert_called_once_with(cascade)
    launcher_proxy.close_cascade_for_main_interaction.assert_not_called()
    launcher_proxy.render.assert_not_called()
    launcher_proxy.error.assert_not_called()
