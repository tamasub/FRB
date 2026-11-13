"""0278: authored physical Files roots are logical roots; no stale JSON origin.

Shipping functions are extracted from Qt classes for headless execution. The
Windows screenshot cases (zz -> FRB_docsExcel\\設計書 and FRB Root -> F:\\FRB)
are covered without pretending Linux runs the PySide6 desktop.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_address import normalized_directory, directory_row
from directory_navigation_history import DirectoryNavigationHistory
from directory_entry_origin import next_entry_origin, within_entry
from launch_virtual_tree import virtual_lookup_node


def extract(class_name, module, method_names, imports=None):
    tree = ast.parse((ROOT / 'src' / module).read_text('utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in method_names]
    assert set(method_names) == {n.name for n in methods}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(
        name='Headless', bases=[], keywords=[], body=methods, decorator_list=[]
    )], type_ignores=[])), '<shipping-root-navigation>', 'exec'), imports := dict(imports or {}))
    return imports['Headless']


def make_view():
    cls = extract('ExpandedLauncherView', 'expanded_view.py',
                  {'go_to_directory', '_physical_breadcrumb_segments',
                   '_virtual_breadcrumb_segments', '_registered_root_from_row',
                   '_record_directory_location', 'choose_files',
                   'restore_json_folder_origin'},
                  {'normalized_directory': normalized_directory,
                   'directory_row': directory_row,
                   'virtual_lookup_node': virtual_lookup_node})
    view = cls()
    view.launcher = SimpleNamespace(expander=lambda: SimpleNamespace(expand=lambda s: s),
                                    remote_window=None, _files_operating_target='directory')
    view._virtual_directory_node = None
    view._filesystem_entry_origin = None
    view._registered_root_origin = None
    view._direct_entry_root = None
    view.path = []
    view.middle = object()
    view.refresh_middle = lambda: None
    view.focus_panel = lambda _: None
    return view


def names(view, path):
    return [label for label, _ in view._physical_breadcrumb_segments(path)]


def test_switching_from_json_folder_to_unrelated_exp_physical_root_cannot_reparent_it():
    v = make_view()
    # Reproduce 0277's stale virtual context when the user selects another
    # registered physical root from Files Exp.
    v._virtual_directory_node = {
        'source': 'launch_json', 'kind': 'folder', 'page_id': 'p',
        'node_id': 'item:p:zz', 'title': 'zz', 'breadcrumbs': ('testwk', 'zz'),
        'lineage': ('page:p', 'item:p:zz')}
    v._filesystem_entry_origin = {'node': v._virtual_directory_node,
                                  'entry_path': r'C:\Users\Demo\OneDrive\Pictures'}
    registered = {'root_path': r'F:\FRB_docsExcel', 'title': 'FRB_docsExcel',
                  'root_id': 'docs-registered-id'}
    with patch('os.path.isdir', return_value=True):
        assert v.go_to_directory(r'F:\FRB_docsExcel\設計書', registered_root=registered)
    assert v._filesystem_entry_origin is None
    assert v._registered_root_origin == registered
    assert v._virtual_directory_node is None
    assert names(v, r'F:\FRB_docsExcel\設計書') == ['FRB_docsExcel', '設計書']


def test_unrelated_physical_navigation_does_not_infer_current_json_as_parent():
    v = make_view()
    v._virtual_directory_node = {'source': 'launch_json', 'kind': 'folder',
                                 'node_id': 'item:p:zz'}
    with patch('os.path.isdir', return_value=True):
        assert v.go_to_directory(r'F:\FRB_docsExcel\設計書')
    assert v._filesystem_entry_origin is None
    assert v._virtual_directory_node is None


def test_frb_root_registered_label_is_the_breadcrumb_root_not_f_drive():
    v = make_view()
    root = {'root_path': r'F:\FRB', 'title': 'FRB Root', 'root_id': 'frb-root'}
    with patch('os.path.isdir', return_value=True):
        assert v.go_to_directory(r'F:\FRB', registered_root=root)
        assert names(v, r'F:\FRB') == ['FRB Root']
        assert v.go_to_directory(r'F:\FRB\tools\Launch')
    assert names(v, r'F:\FRB\tools\Launch') == ['FRB Root', 'tools', 'Launch']
    assert 'F:\\' not in names(v, r'F:\FRB\tools\Launch')


def test_files_shortcut_row_label_is_logical_root_instead_of_os_dir_name():
    v = make_view()
    row = {'item_kind': 'directory', 'item_id': 'root-id',
           'title': 'FRB Root', 'launch_browse_target': r'F:\FRB'}
    v.row_data = lambda it: it
    v.refresh_middle = lambda: None
    v.choose_files(row, 0)
    assert v._registered_root_origin == {
        'root_path': r'F:\FRB', 'title': 'FRB Root', 'root_id': 'root-id'}
    assert names(v, r'F:\FRB') == ['FRB Root']


def test_authored_physical_root_history_is_separate_from_same_path_direct_input():
    h = DirectoryNavigationHistory()
    r = {'root_path': r'F:\FRB', 'title': 'FRB Root', 'root_id': 'frb-root'}
    assert h.record(r'F:\FRB', [directory_row(r'F:\FRB')], registered_root=r)
    assert h.record(r'F:\FRB', [directory_row(r'F:\FRB')], direct_root=r'F:\FRB')
    assert h.back()['registered_root'] == r
    assert h.forward()['direct_root'] == r'F:\FRB'
    assert h.record(r'F:\FRB', [directory_row(r'F:\FRB')], registered_root=r)
    assert len(h.entries) == 3  # revisiting after Forward is a new footstep


def test_two_shortcut_aliases_to_same_physical_path_have_different_history():
    h = DirectoryNavigationHistory()
    path = r'F:\FRB'
    one = {'root_path': path, 'title': 'FRB Root', 'root_id': 'one'}
    two = {'root_path': path, 'title': 'FRB Project', 'root_id': 'two'}
    assert h.record(path, [directory_row(path)], registered_root=one)
    assert h.record(path, [directory_row(path)], registered_root=two)
    assert h.back()['registered_root'] == one


def test_original_json_mount_still_uses_its_json_breadcrumb():
    v = make_view()
    virtual = {'source': 'launch_json', 'kind': 'linked_directory',
               'node_id': 'item:p:sound', 'page_id': 'p',
               'title': 'サウンド レコーディング',
               'breadcrumbs': ('testwk', 'zz', 'サウンド レコーディング'),
               'lineage': ('page:p', 'item:p:zz', 'item:p:sound')}
    with patch('os.path.isdir', return_value=True):
        assert v.go_to_directory(r'C:\Users\Demo\Recordings', source_virtual=virtual)
    assert names(v, r'C:\Users\Demo\Recordings') == list(virtual['breadcrumbs'])
    assert v._registered_root_origin is None


def test_source_wiring_routes_exp_selection_and_left_handoff_by_registered_root():
    app = (ROOT / 'src/app.py').read_text('utf-8')
    exp = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    pane = (ROOT / 'src/remote_files_explorer.py').read_text('utf-8')
    assert 'panel.current_registered_root(directory)' in app
    assert 'registered_root=registered_root' in app
    assert "preferred_root_id=registered_root['root_id']" in app
    assert "preferred_root_id=view._registered_root_origin['root_id']" in app
    assert 'def current_registered_root(self, directory=None)' in pane
    assert 'registered_root=getattr(self' in exp
    assert "getattr(self, '_registered_root_origin', None)" in exp


def test_selected_files_exp_branch_provides_shortcut_root_context():
    # Reproduce a child below an authored physical root without Qt, verifying
    # that '設計書' resolves to FRB_docsExcel, not testwk/zz or F: drive.
    role = 919
    cls = extract('RemoteFilesExplorer', 'remote_files_explorer.py',
                  {'current_registered_root'}, {'_DATA_ROLE': role})

    class Item:
        def __init__(self, title, data, parent=None):
            self.label = title
            self.attrs = data
            self.parent_item = parent
        def parent(self): return self.parent_item
        def data(self, r): return self.attrs if r == role else None
        def text(self): return self.label

    root = Item('FRB_docsExcel', {'path': r'F:\FRB_docsExcel',
                                'studio_identity': {'item_id': 'docs-id'}})
    child = Item('設計書', {'path': r'F:\FRB_docsExcel\設計書'}, parent=root)
    index = SimpleNamespace(isValid=lambda: True)
    obj = cls()
    obj.tree = SimpleNamespace(currentIndex=lambda: index)
    obj.model = SimpleNamespace(itemFromIndex=lambda ix: child)
    assert obj.current_registered_root(r'F:\FRB_docsExcel\設計書') == {
        'root_path': r'F:\FRB_docsExcel', 'title': 'FRB_docsExcel', 'root_id': 'docs-id'}
    assert obj.current_registered_root(r'C:\Unrelated') is None


def test_up_from_an_authored_root_never_exposes_its_os_parent():
    cls = extract('ExpandedLauncherView', 'expanded_view.py', {'go_up'})
    obj = cls()
    selected = []
    obj.launcher = SimpleNamespace(remote_focus_area=lambda area: selected.append(area),
                                   files_root_hidden_mode=False)
    obj._virtual_directory_node = None
    obj._filesystem_entry_origin = None
    obj._direct_entry_root = None
    obj._registered_root_origin = {'root_path': r'F:\FRB', 'title': 'FRB Root',
                                   'root_id': 'root-id'}
    obj.restore_json_folder_origin = lambda: False
    obj.current_directory = lambda: r'F:\FRB'
    obj.go_up()
    assert selected == ['files_exp']
    # In particular it must not assign the physical parent F:\ to obj.path.
