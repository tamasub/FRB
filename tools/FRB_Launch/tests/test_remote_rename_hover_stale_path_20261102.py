"""Regression contracts for Remote nested inline rename (Qt-free tests).

Windows mouse interaction still requires an interactive on-device smoke test.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import textwrap

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')


def method_source(cls, name):
    cl = next(n for n in ast.parse(APP).body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in cl.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(APP, node)


def load_method(cls, name, scope):
    env = dict(scope)
    exec(textwrap.dedent(method_source(cls, name)), env)
    return env[name]


def test_native_new_arrow_reduced_to_same_small_size_as_folder_list():
    painter = method_source('RemoteFolderActionsMenu', 'paintEvent')
    builder = method_source('Launcher', 'show_expanded_background_paste_menu')
    assert 'arrow.moveTo(cx - 2, cy - 4)' in painter
    assert 'arrow.lineTo(cx + 2, cy)' in painter
    assert 'arrow.lineTo(cx - 2, cy + 4)' in painter
    assert 'QMenu::right-arrow { width: 5px; height: 8px; }' in builder
    assert 'if remote_folder_list else' in builder


def test_during_inline_rename_all_hover_navigation_guards_are_armed():
    for name in ('_scroll_hover', 'mouseMoveEvent', 'open_current'):
        body = method_source('CascadeMenu', name)
        assert "getattr(self, '_inline_rename_editor', None) is not None" in body, name
    for name in ('mousePressEvent', 'mouseReleaseEvent'):
        body = method_source('RemoteFolderCascade', name)
        assert "getattr(self, '_inline_rename_editor', None) is not None" in body, name
    begin = method_source('RemoteFolderCascade', 'begin_inline_rename')
    assert 'self.hover_timer.stop()' in begin
    assert 'self.folder_click_timer.stop()' in begin
    assert 'self.child.close()' in begin
    assert 'row_font.setPixelSize(13)' in begin
    assert 'font-size:13px;' in begin


def test_renamed_action_preserves_original_row_and_its_existing_openers(tmp_path):
    original = tmp_path / 'old_folder'; original.mkdir()
    replacement = tmp_path / 'new_folder'
    row = {
        'item_kind': 'directory', 'title': 'old_folder', 'description': str(original),
        'item_id': str(original), 'launch_browse_target': str(original),
        'launch_actions': [{'launch_target': str(original)}],
    }
    captured_opener_row = row  # fill_cascade() closure historically holds this object
    editor = NS(text=lambda: 'new_folder', deleteLater=Mock())
    action = NS(data=lambda: row, setData=Mock(), setText=Mock(), setToolTip=Mock())
    launcher = NS(commit_remote_inline_rename=Mock(return_value=str(replacement)), error=Mock())
    menu = NS(launcher=launcher, _inline_rename_editor=editor,
              _inline_rename_committing=False, _inline_rename_cancelled=False,
              child=None)
    fn = load_method('RemoteFolderCascade', '_finish_inline_rename', {'Path': Path})
    fn(menu, editor, action, None, str(original), 'folder')
    assert captured_opener_row['launch_browse_target'] == str(replacement)
    assert captured_opener_row['launch_actions'][0]['launch_target'] == str(replacement)
    action.setText.assert_called_once_with('new_folder')
    launcher.error.assert_not_called()


def test_new_nested_openers_read_qaction_current_data_not_captured_old_path():
    source = method_source('Launcher', 'fill_cascade')
    assert "if getattr(m, 'remote_folder_navigation', False):" in source
    assert 'latest = a.data()' in source
    assert 'r = latest' in source
    assert 'self.fill_cascade(m.child,r)' in source


def test_renaming_current_directory_does_not_destroy_menu_mid_commit():
    source = method_source('Launcher', 'commit_remote_inline_rename')
    assert "previous_navigation = getattr(self, '_remote_folder_navigation', False)" in source
    assert 'self._remote_folder_navigation = True' in source
    assert 'self.on_files_exp_folder_renamed(str(path), new_path)' in source
    assert 'self._remote_folder_navigation = previous_navigation' in source
