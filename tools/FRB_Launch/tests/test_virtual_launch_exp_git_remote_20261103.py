"""Launch JSON virtual Files Exp + Remote Git text-dialog regression contract."""
import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))

from launch_virtual_tree import virtual_launch_pages, virtual_item_identity


def _node(nodes, item_id):
    for node in nodes:
        if node.get('item_id') == item_id:
            return node
        result = _node(node['children'], item_id)
        if result is not None:
            return result
    return None


def test_page_order_is_explicit_and_pc_stays_separate():
    pages = [{'page_id': 'frb'}, {'page_id': 'windows'}, {'page_id': 'work'}]
    tree = virtual_launch_pages(pages, [])
    assert [p['title'] for p in tree] == ['My Work', 'Windows', 'FRB実験']
    assert [p['node_id'] for p in tree] == ['page:work', 'page:windows', 'page:frb']


def test_json_menu_folder_and_leaf_reflect_actual_parent_chain():
    pages = [{'page_id': 'work'}]
    items = [
        {'page_id': 'work', 'item_id': 'run', 'parent_item_id': 'folder',
         'title': '実行', 'item_kind': 'command', 'sort_order': 20, 'enabled': True,
         'launch_actions': [{'launch_action_type': 'Open', 'launch_target': 'https://example.org'}]},
        {'page_id': 'work', 'item_id': 'folder', 'parent_item_id': '',
         'title': '道具', 'item_kind': 'category', 'sort_order': 10, 'enabled': True},
        {'page_id': 'work', 'item_id': 'extra', 'parent_item_id': 'folder',
         'title': '別', 'item_kind': 'command', 'sort_order': 10, 'enabled': True},
    ]
    result = virtual_launch_pages(pages, items)
    folder = _node(result, 'folder')
    assert folder['kind'] == 'folder'
    assert [x['item_id'] for x in folder['children']] == ['extra', 'run']
    child = _node(result, 'run')
    assert child['kind'] == 'file'
    assert child['row'] is items[0]
    assert virtual_item_identity(child) == {
        'source': 'launch_json', 'page_id': 'work', 'item_id': 'run',
        'parent_item_id': 'folder', 'node_id': 'item:work:run'}


def test_only_authored_enabled_items_are_included():
    pages = [{'page_id': 'work'}, {'page_id': 'frb', 'enabled': False}]
    items = [
        {'page_id': 'work', 'item_id': 'enabled', 'title': 'OK', 'parent_item_id': ''},
        {'page_id': 'work', 'item_id': 'disabled', 'enabled': False, 'parent_item_id': ''},
        {'page_id': 'work', 'item_id': 'orphan', 'parent_item_id': 'missing'},
        {'page_id': 'frb', 'item_id': 'hidden', 'parent_item_id': ''},
    ]
    output = virtual_launch_pages(pages, items)
    assert [p['page_id'] for p in output] == ['work']
    assert [x['item_id'] for x in output[0]['children']] == ['enabled']


def test_reject_broken_cycles_without_running_items():
    pages = [{'page_id': 'work'}]
    items = [
        {'page_id': 'work', 'item_id': 'a', 'parent_item_id': 'b'},
        {'page_id': 'work', 'item_id': 'b', 'parent_item_id': 'a'},
    ]
    assert virtual_launch_pages(pages, items)[0]['children'] == []


def test_identity_does_not_include_mutable_source_row_or_physical_path():
    identity = virtual_item_identity({'source':'launch_json', 'page_id':'work',
        'item_id':'abc', 'parent_item_id':'xyz', 'node_id':'item:work:abc',
        'row':{'launch_actions':[{'launch_action_type':'Open'}]}, 'path':'C:/important'})
    assert 'row' not in identity and 'path' not in identity
    assert virtual_item_identity({'source':'filesystem', 'node_id':'f'}) is None


def test_exp_root_append_precedes_registered_pc_and_home_selects_pc():
    source = (SRC / 'remote_files_explorer.py').read_text(encoding='utf-8')
    roots = source.split('    def set_roots(', 1)[1].split('    def refresh_directory_branch(', 1)[0]
    assert roots.index('virtual_launch_pages(') < roots.index('for root in roots:')
    home = source.split('    def select_first_root_for_home(', 1)[1].split('    def _index_path(', 1)[0]
    assert '_is_pc_index' in home


def test_virtual_wheel_never_automatically_executes_or_navigates_list():
    source = (SRC / 'remote_files_explorer.py').read_text(encoding='utf-8')
    preview = source.split('    def _commit_current_selection(',1)[1].split('    def _activate_index(',1)[0]
    assert 'remote_current_virtual_node() is not None' in preview
    assert '_activate_virtual(' not in preview
    activation = source.split('    def _activate_virtual(',1)[1].split('    def _transfer_paths(',1)[0]
    assert "node['kind'] == 'file'" in activation
    assert 'virtual_item_activated.emit' in activation


def test_remote_right_keeps_virtual_folders_in_exp():
    source = (SRC / 'app.py').read_text(encoding='utf-8')
    method = source.split('    def remote_exp_right_to_list(',1)[1].split('    def remote_list_left_to_exp(',1)[0]
    assert "virtual.get('kind') != 'file'" in method
    assert 'panel.remote_branch(1)' in method
    assert method.index('panel.remote_branch(1)') < method.index("self.remote_focus_area('directory')")


def test_git_dialog_uses_remote_adapter_and_retains_editable_text():
    source = (SRC / 'app.py').read_text(encoding='utf-8')
    method = source.split('    def git_commit_using_filename(',1)[1].split('    def contextMenuEvent(',1)[0]
    assert 'RemoteTextDialog(self, dialog, message_editor, actions)' in method
    assert 'accepted = adapter.ask()' in method
    assert 'message_editor.text()' in method
    assert 'dialog.exec()' in method  # Native fallback if Remote is hidden.


def test_git_input_dispatch_before_background_navigation():
    source = (SRC / 'app.py').read_text(encoding='utf-8')
    method = source.split('    def remote_command(',1)[1].split('    def ',1)[0]
    assert method.index('text_dialog.remote_command(command)') < method.index('menu_wheel.command(command)')
    dialog = (SRC / 'remote_text_dialog.py').read_text(encoding='utf-8')
    assert 'self.editor.setFocus' in dialog
    assert 'button.setFocus(Qt.FocusReason.TabFocusReason)' in dialog
    assert "self.choose('Cancel')" in dialog
    assert "self.choose('OK')" in dialog
    assert 'button.click()' in dialog
    assert 'ConfirmationInputGuard(self.dialog, remote)' in dialog


def test_code_compiles_without_qt_dependency():
    for name in ('app.py', 'remote_files_explorer.py', 'remote_text_dialog.py',
                 'launch_virtual_tree.py', 'expanded_view.py', 'launch_remote.py'):
        ast.parse((SRC / name).read_text(encoding='utf-8'))
