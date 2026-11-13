"""Four small Files Exp / Remote regressions; no PySide6 needed.

Windows GUI drawing still requires manual verification.  The pure logic tests
execute the real AST-extracted methods with small Qt doubles.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src' / 'app.py'
TEXT = SRC.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)


def source(cls, method):
    klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == method)
    return ast.get_source_segment(TEXT, node)


def extract(cls, name, env=None):
    klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<ast>', 'exec'), namespace)
    return namespace[name]


def test_page_popup_uses_click_coordinates_not_remote_button_top():
    method = source('Launcher', 'open_remote_page')
    assert 'pointer = QCursor.pos()' in method
    assert 'button.mapFromGlobal(pointer)' in method
    assert 'menu.popup(QPoint(pointer.x() + 8, pointer.y() + 4))' in method
    assert 'remote.width() - button.x()' not in method


def test_files_exp_popup_is_not_forced_under_remote_files_button():
    method = source('Launcher', 'show_expanded_background_paste_menu')
    assert 'if explicit_target is None:' in method
    assert 'menu = self._apply_remote_popup_bounds(menu)' in method
    assert 'menu.popup(global_pos)' in method
    assert 'menu.remote_target_directory = explicit_target' in method


def test_nested_folder_click_keeps_its_column_and_opens_right(tmp_path):
    target = tmp_path / 'FRB' / 'articles'
    target.mkdir(parents=True)
    clicked_action = object()
    open_child = Mock()
    context = NS(remote_context_root=True, remote_target_directory=str(tmp_path))
    menu = NS(activeAction=lambda: None, openers={clicked_action: open_child},
              child=None)
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              go_to_directory=Mock(return_value=True),
              current_directory=lambda: str(target))
    launcher = NS(expanded_view=view, _remote_folder_root_menu=menu,
                  _remote_folder_opener=context, _remote_folder_navigation=False,
                  _remote_folder_commit_pending=False)
    menu.launcher = launcher
    menu.remote_folder_root = menu
    commit = extract('RemoteFolderCascade', '_remote_commit_folder',
                     {'Path': Path, 'os': os})
    commit(menu, {'item_kind': 'directory', 'launch_browse_target': str(target)},
           clicked_action)
    view.go_to_directory.assert_called_once_with(str(target), preserve_remote_popup=True)
    open_child.assert_called_once_with('keyboard')
    assert context.remote_target_directory == str(target)
    assert launcher._remote_folder_source_path == os.path.normcase(os.path.normpath(str(target)))
    assert not launcher._remote_folder_commit_pending
    assert not launcher._remote_folder_navigation


def test_existing_right_child_is_not_destroyed_by_navigation(tmp_path):
    folder = tmp_path / 'docs'
    folder.mkdir()
    action = object()
    opener = Mock()
    child = NS(owner_action=action, isVisible=lambda: True, close=Mock())
    context = NS(remote_context_root=True, remote_target_directory=str(tmp_path))
    menu = NS(activeAction=lambda: action, openers={action: opener}, child=child)
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              go_to_directory=Mock(return_value=True), current_directory=lambda: str(folder))
    launcher = NS(expanded_view=view, _remote_folder_root_menu=menu,
                  _remote_folder_opener=context, _remote_folder_navigation=False,
                  _remote_folder_commit_pending=False)
    menu.launcher = launcher
    menu.remote_folder_root = menu
    extract('RemoteFolderCascade', '_remote_commit_folder', {'Path': Path, 'os': os})(
        menu, {'item_kind': 'directory', 'launch_browse_target': str(folder)}, action)
    child.close.assert_not_called()
    opener.assert_not_called()  # visible right-hand child stays open


def test_progress_detail_is_single_line_and_elides_without_losing_counts():
    cls = source('FilesOperationProgress', '__init__')
    assert 'self.detail.setWordWrap(False)' in cls
    assert 'QSizePolicy.Policy.Ignored' in cls
    assert 'self._detail_values' in cls
    method = extract('FilesOperationProgress', '_update_detail_text',
                     {'Qt': NS(TextElideMode=NS(ElideRight=1))})
    fm = NS(horizontalAdvance=lambda text: len(text) * 7,
            elidedText=lambda s, mode, width: (s if len(s) * 7 <= width else s[:max(0,width//7-1)] + '…'))
    label = NS(fontMetrics=lambda: fm, width=lambda: 144, setText=Mock())
    obj = NS(_detail_values=(2, 10, 'FRB超長いファイル名' * 20 + '.json'), detail=label)
    method(obj)
    text = label.setText.call_args.args[0]
    assert text.startswith('2 / 10 件 — ')
    assert text.endswith('…')
    assert '\n' not in text
    assert len(text) * 7 <= 144
    assert 'self._update_detail_text()' in source('FilesOperationProgress', 'advance')
