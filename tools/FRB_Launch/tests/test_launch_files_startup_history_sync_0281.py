"""0281: startup/history Exp selection always matches the logical Files List.

Runs production method AST without PySide6, plus the actual supplied Launch
configuration. Windows UI focus/painting still needs a manual smoke test.
"""
import ast
import json
from pathlib import Path
from types import SimpleNamespace as NS
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from directory_navigation_history import DirectoryNavigationHistory
from launch_virtual_tree import virtual_lookup_node, virtual_list_rows

SOURCE = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')


def extracted(name, namespace=None):
    tree = ast.parse(SOURCE)
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef)
               and x.name == 'ExpandedLauncherView')
    func = next(x for x in cls.body if isinstance(x, ast.FunctionDef)
                and x.name == name)
    ns = dict(namespace or {})
    exec(compile(ast.fix_missing_locations(
        ast.Module(body=[func], type_ignores=[])), '<expanded-live>', 'exec'), ns)
    return ns[name]


def sample():
    data = json.loads((ROOT / 'config/frb_launch_data.json').read_text(encoding='utf-8'))
    root = virtual_lookup_node(data['pages'], data['items'], 'work', '', data['items'])
    return data, root


def make_panel():
    log = []
    def selected(kind, value=None):
        log.append((kind, value))
        return True
    return NS(isVisible=lambda: True, log=log,
              remote_select_virtual_node=lambda n: selected('virtual', n['node_id']),
              remote_select_pc_root=lambda: selected('pc'),
              remote_select_mounted_directory=lambda n, e, p: selected('mount', n['node_id']),
              ensure_direct_root=lambda p: selected('direct-root', p),
              sync_current_directory=lambda p, **kw: selected('physical', (p, kw)),
              restore_previous_tree_state=lambda: selected('restored-stale'))


def test_startup_page_is_my_work_and_not_pc_on_real_data():
    data, work = sample()
    assert work['node_id'] == 'page:work'
    assert work['kind'] == 'page'
    assert any(row['title'] == 'ZIP' for row in virtual_list_rows(work))
    refresh = extracted('refresh')
    # Startup is resolved before the existing legacy PC fallback and before
    # refresh_middle() records the first navigation history entry.
    source = ast.get_source_segment(SOURCE, next(n for n in ast.walk(ast.parse(SOURCE))
        if isinstance(n, ast.FunctionDef) and n.name == 'refresh'))
    assert source.index('initial_virtual = virtual_lookup_node(') < source.index('self.refresh_middle()')
    assert 'self._virtual_directory_node = initial_virtual' in source
    assert 'and self._virtual_directory_node is None' in source
    assert 'self._initial_files_location_committed' in source


def test_restore_history_pc_and_work_never_leave_opposite_exp_selected():
    data, work = sample()
    panel = make_panel()
    pc_row = {'item_id': 'pc', '_system_drives_root': True, 'item_kind': 'category'}
    pc_item = object()
    current_roots = []
    left = NS(tree=NS(topLevelItemCount=lambda: 1,
                      topLevelItem=lambda i: pc_item,
                      setCurrentItem=lambda obj: current_roots.append(obj)))
    view = NS(left=left, path=[], _virtual_directory_node=None,
              _filesystem_entry_origin=None, _direct_entry_root=None,
              _registered_root_origin=None,
              embedded_files_exp=panel,
              launcher=NS(remote_window=None, _nav_update_buttons=lambda: None), middle=object(),
              row_data=lambda _: pc_row, current_directory=lambda: None,
              refresh_middle=lambda: None, focus_panel=lambda _: None)
    view.align_files_exp_with_location = extracted('align_files_exp_with_location').__get__(view)
    view._restore_directory_history = extracted('_restore_directory_history').__get__(view)
    view.directory_history = DirectoryNavigationHistory()
    view._restoring_directory_history = False
    view.directory_history.record(None, [pc_row], root_id='pc')
    view.directory_history.record(None, [], virtual_node=work)
    panel.log.clear()
    assert view._restore_directory_history(view.directory_history.back())
    assert panel.log[-1] == ('pc', None), 'PC list cannot be paired with My Work Exp'
    panel.log.clear()
    assert view._restore_directory_history(view.directory_history.forward())
    assert panel.log[-1] == ('virtual', 'page:work')
    assert view._virtual_directory_node['node_id'] == 'page:work'


def test_reload_stale_exp_selection_is_overridden_by_displayed_work():
    data, work = sample()
    panel = make_panel()
    panel.set_roots = lambda *_: panel.log.append(('set_roots', None))
    view = NS(embedded_files_exp=panel, _embedded_files_exp_roots_ready=False,
              _virtual_directory_node=work, _filesystem_entry_origin=None,
              _direct_entry_root=None, _registered_root_origin=None,
              path=[], current_directory=lambda: None,
              launcher=NS(expander=lambda: NS(expand=lambda p: p), remote_window=None),
              left=NS(tree=NS(topLevelItemCount=lambda: 1, topLevelItem=lambda _: object())),
              row_data=lambda _: {'item_id': 'root'})
    view.align_files_exp_with_location = extracted('align_files_exp_with_location').__get__(view)
    view.reload_embedded_files_exp_roots = extracted('reload_embedded_files_exp_roots').__get__(view)
    assert view.reload_embedded_files_exp_roots()
    assert panel.log == [('set_roots', None), ('restored-stale', None),
                         ('virtual', 'page:work')]


def test_virtual_history_does_not_capture_unrelated_physical_root():
    _, work = sample()
    view = NS(_restoring_directory_history=False, _virtual_directory_node=work,
              _filesystem_entry_origin=None, _direct_entry_root=None,
              _registered_root_origin=None, path=[], current_directory=lambda: None,
              left=NS(tree=NS(currentItem=lambda: object())),
              row_data=lambda _: {'item_id': 'pc'}, directory_history=DirectoryNavigationHistory())
    record = extracted('_record_directory_location')
    assert record(view) is None
    assert view.directory_history.current['root_id'] is None
    assert view.directory_history.current['virtual_node']['node_id'] == 'page:work'


def test_alignment_keeps_mount_and_registered_aliases_distinct():
    panel = make_panel()
    node = {'node_id': 'item:work:mounted'}
    view = NS(embedded_files_exp=panel, launcher=NS(remote_window=None),
              _virtual_directory_node=None,
              _filesystem_entry_origin={'node': node, 'entry_path': r'C:\Audio'},
              _direct_entry_root=None, _registered_root_origin=None,
              current_directory=lambda: r'C:\Audio\2026', path=[])
    align = extracted('align_files_exp_with_location')
    align(view)
    assert panel.log[-1] == ('mount', 'item:work:mounted')
    view._filesystem_entry_origin = None
    view._registered_root_origin = {'root_id': 'frb_root'}
    align(view)
    assert panel.log[-1] == ('physical', (r'C:\Audio\2026', {'preferred_root_id': 'frb_root'}))
