"""Regression for icon chooser, real-file registration Drop, Files toolbar UX.

These contract checks run without PySide6; Windows/Qt input still needs real UI
acceptance.  They must not alter Launch config JSON or physical files.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text('utf-8')
EXP = (ROOT / 'src/expanded_view.py').read_text('utf-8')
FILES = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
GUARD = (ROOT / 'src/remote_confirmation.py').read_text('utf-8')


def _get_drop_resolver():
    """Execute only this pure method with mocked UI state; no Qt required."""
    module = ast.parse(EXP)
    owner = next(node for node in module.body if isinstance(node, ast.ClassDef)
                 and any(isinstance(body, ast.FunctionDef) and
                         body.name == '_middle_launch_drop_target' for body in node.body))
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
                  and node.name == '_middle_launch_drop_target')
    # Do not evaluate references to Qt or import GUI source at module import.
    module_ast = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module_ast)
    env = {
        'mime_sources': lambda m: m,
        'Path': Path,
        'virtual_item_identity': lambda node: (node['page_id'], node['item_id']),
    }
    exec(compile(module_ast, '<drop-resolver>', 'exec'), env)
    return env['_middle_launch_drop_target']


def _node(kind, item_id, item_kind, runtime=''):
    return {'kind': kind, 'item_id': item_id, 'page_id': 'work',
            'row': {'item_kind': item_kind}, 'runtime_catalog': runtime}


def _fake_self(current, hover):
    item = object() if hover else None
    return SimpleNamespace(
        _workspace_mode='files', _virtual_directory_node=current,
        middle=SimpleNamespace(tree=SimpleNamespace(itemAt=lambda point: item)),
        row_data=lambda _: {'_launch_virtual_node': hover},
    )


def test_external_file_drop_on_existing_json_leaf_adds_to_current_category():
    drop = _get_drop_resolver()
    parent = _node('folder', 'public_url', 'category')
    leaf = _node('file', 'blog', 'command')
    assert drop(_fake_self(parent, leaf), None, [{'value': 'C:/foo.txt'}]) == ('work', 'public_url')
    assert drop(_fake_self(parent, None), None, [{'value': 'C:/foo.txt'}]) == ('work', 'public_url')


def test_external_drop_on_json_folder_enters_that_folder_but_rejects_runtime():
    drop = _get_drop_resolver()
    parent = _node('folder', 'public_url', 'category')
    child = _node('folder', 'sub', 'category')
    runtime = _node('file', 'runtime', 'command', 'browser_bookmarks')
    assert drop(_fake_self(parent, child), None, [{'value': 'C:/foo.txt'}]) == ('work', 'sub')
    assert drop(_fake_self(parent, runtime), None, [{'value': 'C:/foo.txt'}]) is False
    assert drop(_fake_self(None, None), None, [{'value': 'C:/foo.txt'}]) is False


def test_icon_chooser_keeps_native_combobox_controls_and_popup_usable():
    assert "'QComboBox'" in GUARD
    assert "combo.view().isVisible()" in GUARD
    assert 'if kind == QEvent.Type.Wheel and self._native_dialog_control(obj):' in GUARD
    assert "'icon_key': icon_box.currentData()" in APP


def test_simple_edit_description_is_white_and_path_still_not_editable():
    assert 'QPlainTextEdit { background-color: #ffffff;' in APP
    assert 'パスは変更しません。' in APP


def test_files_search_icon_hidden_but_list_search_remains():
    assert 'self.files_history_button.hide()' in EXP
    assert "self.middle_search.setPlaceholderText('このフォルダーを検索" in EXP
    assert 'self.middle_search.textChanged.connect(self.apply_middle_filter)' in EXP


def test_files_exp_drop_hint_is_passive_and_only_shown_in_empty_space():
    assert '～ フォルダー Drop エリア ～' in FILES
    assert 'self.root_drop_hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)' in FILES
    assert 'if available < 45:' in FILES
    assert 'self.tree.viewport().installEventFilter(self)' in FILES
