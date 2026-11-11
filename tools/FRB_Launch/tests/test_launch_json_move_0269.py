"""Move UX contract: JSON-only drag/drop, stable order, Studio CLI integration."""
import ast
import json
from pathlib import Path
import os
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_json_move import (MOVE_MIME, encode_source, decode_source,
                              drop_placement, exp_folder_placement)
from launch_menu_registration import (RegistrationError, prepare_move, commit_move,
                                      prepare_delete_many, commit_delete)


def node(item_id, *, parent='', kind='command', page='work', runtime=''):
    return {'source':'launch_json','kind':'folder' if kind == 'category' else 'file',
            'page_id':page,'item_id':item_id,'parent_item_id':parent,
            'node_id':f'item:{page}:{item_id}',
            'runtime_catalog':runtime,'row':{'item_kind':kind}}


def test_move_mime_has_no_uri_or_physical_file_path():
    assert MOVE_MIME.startswith('application/x-frb-launch-json-')
    value = encode_source('work', '日本語メニュー')
    assert decode_source(value) == ('work','日本語メニュー')
    assert b'file:///' not in value
    assert decode_source(b'invalid') is None
    assert decode_source(b'{}') is None
    assert decode_source(b'{"version":1,"page_id":"","item_id":"a"}') is None


def test_drop_positions_before_after_inside_and_blank():
    folder = node('home',kind='category')
    entry = node('leaf', parent='home')
    subfolder = node('sub',kind='category',parent='home')
    assert drop_placement(folder, entry, fraction=.1) == {
        'group_id':'work','parent_id':'home','position':'before','anchor_id':'leaf'}
    assert drop_placement(folder, entry, fraction=.9)['position']=='after'
    assert drop_placement(folder, subfolder, fraction=.5) == {
        'group_id':'work','parent_id':'sub','position':'end'}
    assert drop_placement(folder) == {'group_id':'work','parent_id':'home','position':'end'}
    assert exp_folder_placement(subfolder) == {
        'group_id':'work','parent_id':'sub','position':'end'}


def test_physical_runtime_and_noncategory_destinations_are_rejected():
    folder = node('home',kind='category')
    physical = {'source':'filesystem','kind':'folder','path':r'F:\\FRB'}
    runtime = node('runtime', parent='home',runtime='browser_bookmarks')
    leaf = node('leaf')
    assert drop_placement(physical) is None
    assert drop_placement(folder, physical) is None
    assert drop_placement(folder, runtime) is None
    assert drop_placement(folder, node('foreign',page='other')) is None
    assert drop_placement(leaf) is None
    assert exp_folder_placement(physical) is None
    assert exp_folder_placement(runtime) is None
    assert exp_folder_placement(leaf) is None


def test_virtual_list_header_click_sort_disabled_but_physical_preserved():
    source = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
    module = ast.parse(source)
    view = next(c for c in module.body if isinstance(c,ast.ClassDef) and
                c.name=='ExpandedLauncherView')
    header = next(m for m in view.body if isinstance(m,ast.FunctionDef) and
                  m.name=='_middle_header_clicked')
    # The very first branch must reject virtual mode; physical path still
    # enters sort_mode_for_header and set_middle_sort.
    assert isinstance(header.body[0],ast.If)
    assert isinstance(header.body[0].body[0],ast.Return)
    segment = ast.get_source_segment(source,header)
    assert 'sort_mode_for_header' in segment and 'self.set_middle_sort(mode)' in segment
    assert 'rows.sort(key=lambda r: source_order' in source
    assert 'self.middle.tree.header().setSortIndicatorShown(False)' in source


def test_launch_disables_move_during_search_and_keeps_file_copy():
    source = (ROOT/'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'self.middle_search.text().strip()' in source
    assert 'super().startDrag(supported_actions)' in source
    assert 'virtual_studio_target(hovered' in source
    assert 'sender=event.source()' in source
    exp = (ROOT/'src/remote_files_explorer.py').read_text(encoding='utf-8')
    assert 'item.setDragEnabled(False)' in exp  # physical nodes
    assert 'virtual_studio_target(node' in exp
    assert 'exp_folder_placement(node)' in exp


def test_multi_delete_and_move_cli_on_temp_copy(tmp_path):
    studio = os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source and Node required')
    doc = json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text('utf-8'))
    doc['items'].extend([
        {'item_id':'move_a','page_id':'work','parent_item_id':'',
         'item_kind':'category','title':'A','sort_order':990,'enabled':True},
        {'item_id':'move_b','page_id':'work','parent_item_id':'',
         'item_kind':'category','title':'B','sort_order':991,'enabled':True},
        {'item_id':'move_c','page_id':'work','parent_item_id':'',
         'item_kind':'category','title':'C','sort_order':992,'enabled':True},
        {'item_id':'leaf_test','page_id':'work','parent_item_id':'move_a',
         'item_kind':'command','title':'Leaf','sort_order':990,'enabled':True},
    ])
    file = tmp_path/'launch.json'
    file.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    physical = tmp_path/'physical_keep';physical.mkdir()
    (physical/'important.txt').write_text('keep',encoding='utf-8')
    before = file.read_bytes()
    plan = prepare_move(file,studio,'work','move_c',
                        {'group_id':'work','parent_id':'',
                         'position':'before','anchor_id':'move_b'})
    assert plan and file.read_bytes() == before
    committed = commit_move(plan)
    assert committed['status']=='COMMITTED'
    rows = json.loads(file.read_text('utf-8'))['items']
    group = sorted((r for r in rows if r.get('page_id')=='work' and
                    not r.get('parent_item_id')),
                   key=lambda r:r.get('sort_order',0))
    ids = [r['item_id'] for r in group]
    assert ids.index('move_a') < ids.index('move_c') < ids.index('move_b')
    plan = prepare_move(file,studio,'work','move_b',
                        {'group_id':'work','parent_id':'move_a','position':'end'})
    commit_move(plan)
    rows = json.loads(file.read_text('utf-8'))['items']
    assert next(r for r in rows if r.get('item_id')=='move_b')['parent_item_id']=='move_a'
    # Multi-delete is a single atomic ChangeSet, including descendants.
    plan = prepare_delete_many(file,studio,[('work','move_a'),('work','move_c')])
    assert plan['selected_count']==2
    assert plan['deleted']==4
    assert plan['descendants']==2
    commit_delete(plan)
    rows = json.loads(file.read_text('utf-8'))['items']
    assert not any(r.get('item_id') in {'move_a','move_b','move_c','leaf_test'} for r in rows)
    assert (physical/'important.txt').read_text('utf-8')=='keep'


def test_nested_selected_parent_and_child_delete_is_not_double_counted(tmp_path):
    studio = os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source and Node required')
    doc = json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text('utf-8'))
    doc['items'] += [
        {'item_id':'test-parent','page_id':'work','parent_item_id':'',
         'item_kind':'category','title':'Parent','sort_order':990,'enabled':True},
        {'item_id':'test-child','page_id':'work','parent_item_id':'test-parent',
         'item_kind':'category','title':'Child','sort_order':991,'enabled':True},
        {'item_id':'test-leaf','page_id':'work','parent_item_id':'test-child',
         'item_kind':'command','title':'Leaf','sort_order':992,'enabled':True},
    ]
    file=tmp_path/'launch.json'
    file.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8')
    plan=prepare_delete_many(file,studio,
                             [('work','test-parent'),('work','test-child')])
    assert plan['deleted']==3  # not four: nested targets overlap
    assert plan['descendants']==1
    commit_delete(plan)
    remaining=json.loads(file.read_text('utf-8'))['items']
    assert not any(r.get('item_id') in {'test-parent','test-child','test-leaf'}
                   for r in remaining)
