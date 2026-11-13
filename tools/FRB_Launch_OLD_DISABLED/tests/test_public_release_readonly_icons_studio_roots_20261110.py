"""Regressions for copyable choices, Studio identities and configured Exp icons."""
import ast
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
from registered_root_studio import verified_registered_root
from remote_files_exp_roots import registered_folder_roots
from launch_virtual_tree import virtual_launch_pages


def _example():
    pages = [{'page_id': 'work', 'enabled': True}]
    items = [{'item_id': 'registered', 'page_id': 'work', 'parent_item_id': 'folders',
              'item_kind': 'directory', 'enabled': True,
              'title': 'DL', 'icon_key': 'category.blue',
              'launch_browse_target': '%HOME%\\Downloads'}]
    expand = lambda value: value.replace('%HOME%', 'C:\\Users\\Test')
    root = registered_folder_roots(items, expand)[0]
    return pages, items, root, expand


def test_authored_folder_root_keeps_identity_and_icon_from_canonical_json():
    pages, items, root, expand = _example()
    assert root == {'label': 'DL', 'path': r'C:\Users\Test\Downloads',
                    'pc': False, 'page_id': 'work', 'item_id': 'registered'}
    assert verified_registered_root(root, pages, items, expand) is items[0]
    # Even if the display row is copied/modded, canonical item is used.
    assert verified_registered_root({**root, 'label': 'Wrong'}, pages, items, expand) is items[0]


def test_only_enabled_matching_authored_directories_open_studio():
    pages, items, root, expand = _example()
    assert verified_registered_root({**root, 'path': r'C:\elsewhere'}, pages, items, expand) is None
    assert verified_registered_root({**root, 'item_id': 'unknown'}, pages, items, expand) is None
    assert verified_registered_root({**root, 'page_id': 'else'}, pages, items, expand) is None
    assert verified_registered_root(root, [{'page_id': 'work', 'enabled': False}], items, expand) is None
    assert verified_registered_root(root, pages, [{**items[0], 'enabled': False}], expand) is None
    assert verified_registered_root(root, pages, [{**items[0], 'item_kind': 'command'}], expand) is None
    assert verified_registered_root(root, pages, [{**items[0], '_installed_app': True}], expand) is None
    assert verified_registered_root({'path': root['path'], 'pc': True}, pages, items, expand) is None
    assert verified_registered_root(root, pages, items, lambda _: (_ for _ in ()).throw(ValueError())) is None


def test_virtual_folders_preserve_original_icon_key_reference():
    pages = [{'page_id': 'work'}]
    items = [{'page_id': 'work', 'item_id': 'zip', 'parent_item_id': '',
              'title': 'ZIP', 'item_kind': 'category', 'icon_key': 'archive'},
             {'page_id': 'work', 'item_id': 'child', 'parent_item_id': 'zip',
              'title': 'script', 'item_kind': 'command'}]
    result = virtual_launch_pages(pages, items)
    assert result[0]['children'][0]['row']['icon_key'] == 'archive'


def test_widgets_and_signal_wiring_in_sources_are_syntactically_sound():
    for filename in ('app.py', 'remote_files_explorer.py', 'expanded_view.py',
                     'launch_remote.py', 'registered_root_studio.py'):
        ast.parse((SRC / filename).read_text(encoding='utf-8'))
    app = (SRC / 'app.py').read_text('utf-8')
    assert "description.setReadOnly(True)" in app
    assert "self.list.setItemWidget(q, 1, description)" in app
    assert "if self.selection:" in app
    assert "self.show_expanded_background_paste_menu(\n            position, remote_folder_list=True" in app
    assert 'self.launch_configuration_studio(item_id=iid)' in app
    exp = (SRC / 'remote_files_explorer.py').read_text('utf-8')
    assert 'self.authored_root_context_requested.emit(path, identity, point)' in exp
    assert 'self._launcher.row_icon({' in exp
    assert 'studio_identity' in exp
    assert 'authored_root_context_requested.connect(' in (SRC / 'expanded_view.py').read_text('utf-8')
    assert 'files_exp_authored_root_context' in (SRC / 'launch_remote.py').read_text('utf-8')
