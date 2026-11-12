"""Logical path is the one navigation truth: JSON mount + direct OS roots.

Headless contracts deliberately execute methods extracted from the shipping Qt
source rather than importing PySide6 (not required by CI). Windows GUI tests
are still necessary for actual mouse, focus, and drag gestures.
"""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_navigation_history import DirectoryNavigationHistory
from directory_address import normalized_directory, directory_row
from directory_entry_origin import next_entry_origin, within_entry
from launch_virtual_tree import virtual_exp_roots, virtual_exp_folders, virtual_list_rows, virtual_lookup_node


def source_class(module, name, names, ns):
    tree = ast.parse((ROOT / 'src' / module).read_text('utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in methods} == set(names)
    isolated = ast.ClassDef(name='Headless', bases=[], keywords=[], body=methods, decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[isolated], type_ignores=[])),
                 '<shipping-navigation>', 'exec'), ns)
    return ns['Headless']


def sample():
    data = json.loads((ROOT / 'config/frb_launch_data.json').read_text('utf-8'))
    roots = virtual_exp_roots(data['pages'], data['items'])
    def walk(node):
        yield node
        for child in node.get('children', ()): yield from walk(child)
    sound = next(node for root in roots for node in walk(root)
                 if node['title'] == 'サウンド レコーディング')
    parent = next(node for root in roots for node in walk(root)
                  if node['node_id'] == sound['lineage'][-2])
    return data, sound, parent


def test_registered_filesystem_directory_is_a_logical_folder_in_both_columns():
    data, sound, zz = sample()
    assert sound['kind'] == 'linked_directory'
    assert sound in virtual_exp_folders(zz)
    assert sound['breadcrumbs'][-3:] == ('💟 testwk', 'zz', 'サウンド レコーディング')
    listed = next(item for item in virtual_list_rows(zz) if item['title'] == sound['title'])
    assert listed['item_kind'] == 'directory'
    assert listed['_launch_virtual_node']['node_id'] == sound['node_id']
    assert listed['launch_browse_target'] == sound['row']['launch_browse_target']
    # No mutation or additional JSON metadata required in the persisted source.
    assert 'linked_directory' not in json.dumps(data, ensure_ascii=False)


def test_mount_origin_remains_identical_through_children_and_stops_at_entry():
    _, sound, _ = sample()
    root = sound['row']['launch_browse_target']
    origin = next_entry_origin(None, sound, root)
    assert origin['node'] is sound and origin['entry_path'] == root
    assert next_entry_origin(origin, None, root + r'\2026\recording') == origin
    assert not within_entry(root + r'\..\Other', root)
    assert next_entry_origin(origin, None, r'C:\CompletelyOther') is None


def test_history_keeps_json_node_and_mount_identity_separate_from_same_physical_path():
    _, sound, zz = sample()
    path = sound['row']['launch_browse_target']
    h = DirectoryNavigationHistory()
    assert h.record(None, [], virtual_node=zz)
    assert h.record(path, [directory_row(path)],
                    entry_origin={'node': sound, 'entry_path': path})
    assert not h.record(path.lower(), [directory_row(path)],
                        entry_origin={'node': sound, 'entry_path': path})
    assert h.record(path, [directory_row(path)], direct_root=path)
    assert h.back()['entry_origin']['node']['node_id'] == sound['node_id']
    assert h.back()['virtual_node']['node_id'] == zz['node_id']
    assert h.forward()['entry_origin']['entry_path'] == path


def test_same_physical_path_in_two_json_locations_has_two_back_targets():
    _, sound, zz = sample()
    fake = dict(sound, node_id='item:other:unique-id')
    path = sound['row']['launch_browse_target']
    h = DirectoryNavigationHistory()
    h.record(path, [directory_row(path)], entry_origin={'node': sound, 'entry_path': path})
    h.record(path, [directory_row(path)], entry_origin={'node': fake, 'entry_path': path})
    assert len(h.entries) == 2
    assert h.back()['entry_origin']['node']['node_id'] == sound['node_id']


def test_breadcrumbs_mount_under_json_and_do_not_include_os_ancestors():
    _, sound, zz = sample()
    methods = {'_physical_breadcrumb_segments', '_virtual_breadcrumb_segments'}
    cls = source_class('expanded_view.py', 'ExpandedLauncherView', methods, {})
    view = cls()
    root = sound['row']['launch_browse_target']
    view._filesystem_entry_origin = {'node': sound, 'entry_path': root}
    view._direct_entry_root = None
    labels = [label for label, _ in view._physical_breadcrumb_segments(root)]
    assert labels == list(sound['breadcrumbs'])
    assert 'Users' not in labels and 'OneDrive' not in labels
    child_labels = [label for label, _ in view._physical_breadcrumb_segments(root + r'\2026\October')]
    assert child_labels[-2:] == ['2026', 'October']
    assert child_labels[:len(labels)] == labels
    assert view._physical_breadcrumb_segments(r'C:\Elsewhere') is None


def test_direct_input_is_its_own_root_while_other_navigation_can_mount_json():
    _, sound, parent = sample()
    ns = {'normalized_directory': normalized_directory, 'directory_row': directory_row}
    cls = source_class('expanded_view.py', 'ExpandedLauncherView',
                       {'go_to_directory', '_physical_breadcrumb_segments',
                        '_virtual_breadcrumb_segments'}, ns)
    view = cls()
    view.launcher = SimpleNamespace(expander=lambda: SimpleNamespace(expand=lambda p: p),
                                    remote_window=None, _files_operating_target='directory')
    view._virtual_directory_node = None
    view._filesystem_entry_origin = None
    view._direct_entry_root = None
    view._workspace_mode = 'files'
    view.middle = object()
    view.path = []
    view.refresh_middle = lambda: None
    view.focus_panel = lambda _: None
    root = r'C:\Users\tsub-\OneDrive\Pictures'
    with patch('os.path.isdir', return_value=True):
        assert view.go_to_directory(root, direct_anchor=True)
        assert view._direct_entry_root == root
        assert view._filesystem_entry_origin is None
        assert view.go_to_directory(root + r'\2026')
        assert view._direct_entry_root == root
        assert [x[0] for x in view._physical_breadcrumb_segments(root + r'\2026')] == ['Pictures', '2026']
        assert view.go_to_directory(sound['row']['launch_browse_target'], source_virtual=sound)
        assert view._direct_entry_root is None
        assert view._filesystem_entry_origin['node'] is sound
        assert view.go_to_directory(sound['row']['launch_browse_target'] + r'\recordings')
        assert view._filesystem_entry_origin['node'] is sound


def test_up_from_mount_root_returns_json_parent_not_one_drive():
    _, sound, zz = sample()
    ns = {'virtual_lookup_node': virtual_lookup_node}
    cls = source_class('expanded_view.py', 'ExpandedLauncherView', {'restore_json_folder_origin'}, ns)
    view = cls()
    path = sound['row']['launch_browse_target']
    data, _, _ = sample()
    view.launcher = SimpleNamespace(pages=data['pages'], authored_items=data['items'], data=data)
    view._virtual_directory_node = None
    view._filesystem_entry_origin = {'node': sound, 'entry_path': path}
    view.current_directory = lambda: path
    seen = []
    view.show_virtual_launch_directory = lambda node: seen.append(node) or True
    assert view.restore_json_folder_origin()
    assert seen[-1]['node_id'] == zz['node_id']
    view.current_directory = lambda: path + r'\recordings'
    assert not view.restore_json_folder_origin()


def test_presentation_wiring_for_exp_left_up_history_and_real_path_tooltips():
    view = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    exp = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
    app = (ROOT / 'src/app.py').read_text('utf-8')
    for content in (view, exp, app): ast.parse(content)
    assert 'self.address_bar.set_logical_directory(' in view
    assert 'navigate_logical=self.navigate_logical_crumb' in view
    assert "origin['entry_path']" in view
    assert 'def remote_select_mounted_directory(self, node, entry_path, target_path)' in exp
    assert 'def ensure_direct_root(self, path)' in exp
    assert 'remote_select_mounted_directory(' in app
    assert 'view.restore_json_folder_origin()' not in app  # keyboard Left is NOT Up
    assert "'実パス: ' + self.current_path" in view
