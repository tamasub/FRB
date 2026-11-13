"""Last keyboard-current persistence contract; independent of Windows/Qt."""
import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from focus_session import (normalize_focus_state, focus_area_for_reopen,
                           resolve_path_ids)


@pytest.mark.parametrize('area', [
    'search', 'pages', 'roots', 'files', 'directory', 'bookmarks', 'list',
])
def test_all_keyboard_current_areas_survive_serialization(area):
    import json
    value = normalize_focus_state({'area': area, 'page_id': 'work',
                                   'item_id': 'abc', 'mode': 'expanded',
                                   'path_ids': ['folders', 'F:\\']})
    assert json.loads(json.dumps(value, ensure_ascii=False)) == value
    assert value['area'] == area


def test_bad_or_old_setting_falls_back_to_search():
    for raw in (None, {}, 'invalid', [], {'area': 'unknown'}):
        assert normalize_focus_state(raw)['area'] == 'search'


def test_corrupt_and_excessive_path_entries_are_rejected():
    result = normalize_focus_state({'area': 'directory', 'path_ids':
        [None, 4, 'good'] + ['x'] * 100 + ['y' * 4097],
        'item_id': [42]})
    assert result['path_ids'][0] == 'good'
    assert len(result['path_ids']) == 62  # cap at first 64 supplied entries
    assert 'item_id' not in result


@pytest.mark.parametrize('area', ['files', 'directory', 'bookmarks', 'roots', 'pages'])
def test_expanded_areas_keep_their_keyboard_current(area):
    assert focus_area_for_reopen(area, expanded=True) == area


@pytest.mark.parametrize('area', ['search', 'pages', 'list'])
def test_classic_areas_keep_their_keyboard_current(area):
    assert focus_area_for_reopen(area, expanded=False) == area


def test_hidden_expanded_area_falls_back_when_not_visible():
    assert focus_area_for_reopen('directory', expanded=False) == 'search'
    assert focus_area_for_reopen('list', expanded=True) == 'search'
    assert focus_area_for_reopen('list', expanded=True, selection=True) == 'roots'


def test_paths_resolved_from_live_child_data_not_stale_objects():
    root = {'item_id': 'folders'}
    data = {'folders': [{'item_id': 'dir', 'item_kind': 'directory'}],
            'dir': [{'item_id': 'child', 'item_kind': 'directory'}],
            'child': [{'item_id': 'file', 'item_kind': 'command'}]}
    get_children = lambda node: data[node['item_id']]
    assert [r['item_id'] for r in resolve_path_ids(root, ['dir','child'],get_children)] == ['dir','child']
    assert [r['item_id'] for r in resolve_path_ids(root, ['dir','gone','child'],get_children)] == ['dir']
    assert [r['item_id'] for r in resolve_path_ids(root, ['dir','child','file'],get_children)] == ['dir','child']


def test_removed_or_inaccessible_directory_never_prevents_opening():
    assert resolve_path_ids({'item_id': 'missing'}, ['x'], lambda r: []) == []
    def inaccessible(_):
        raise PermissionError('network directory inaccessible')
    assert resolve_path_ids({'item_id':'missing'}, ['x'], inaccessible) == []


def test_main_window_wiring_preserves_hotkeys_and_restores_prior_focus():
    source = (ROOT/'src/app.py').read_text(encoding='utf8')
    module = ast.parse(source)
    launcher = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    methods = {n.name:ast.get_source_segment(source,n) for n in launcher.body
               if isinstance(n,ast.FunctionDef)}
    assert "self.settings.value('last_current'" in methods['__init__']
    assert 'focusChanged.connect(self.capture_last_focus_change)' in methods['__init__']
    assert 'self.save_last_current()' in methods['dismiss']
    assert methods['dismiss'].index('self.save_last_current()') < methods['dismiss'].index('self.menu.close()')
    assert 'self.restore_last_current()' in methods['summon']
    assert 'self.restore_last_current()' in methods['restore_keyboard_focus']
    assert 'self.list.setFocus()' in methods['summon_menu']
    assert "self.selection and self.view_mode == 'expanded'" in methods['save_last_current']
    assert "root_item_id = self._last_root_id" in methods['save_last_current']
    assert 'resolve_path_ids(' in methods['restore_last_current']
    assert 'self.search.clear()' in methods['summon']  # Do not revive previous query
