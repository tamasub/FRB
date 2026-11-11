"""studio_work_0269: cascade Delete preflight/CLI, no physical file deletion."""
import ast
import json
import os
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'src'))
from launch_menu_registration import (RegistrationError, _delete_subtree,
    prepare_delete,commit_delete)


def sample():
    return json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def nested():
    doc = sample()
    doc['items'] += [
        {'page_id':'work','item_id':'delete_me','parent_item_id':'','item_kind':'category','title':'親'},
        {'page_id':'work','item_id':'sub','parent_item_id':'delete_me','item_kind':'category','title':'子カテゴリー'},
        {'page_id':'work','item_id':'local_dir','parent_item_id':'sub','item_kind':'directory','title':'実フォルダー'},
        {'page_id':'work','item_id':'child_url','parent_item_id':'sub','item_kind':'command','title':'リンク'},
        {'page_id':'work','item_id':'child_cmd','parent_item_id':'delete_me','item_kind':'command','title':'処理'},
    ]
    return doc


def test_descendant_counts_exclude_selected_and_other_branches():
    original, children = _delete_subtree(nested(), 'work', 'delete_me')
    assert original['title'] == '親'
    assert [r['item_id'] for r in children] == ['sub','local_dir','child_url','child_cmd']
    assert sum(r['item_kind'] in ('category','directory') for r in children) == 2
    assert len(children) - 2 == 2


def test_missing_and_ambiguous_target_is_rejected():
    doc = nested()
    with pytest.raises(RegistrationError):_delete_subtree(doc,'work','missing')
    doc['items'].append(dict(next(r for r in doc['items'] if r['item_id']=='delete_me')))
    with pytest.raises(RegistrationError):_delete_subtree(doc,'work','delete_me')


def test_gui_has_enabled_delete_for_items_and_files_registered_root():
    code = (ROOT/'src/app.py').read_text(encoding='utf-8')
    ast.parse(code)
    assert 'def launch_unregister_action(self, page_id, item_id)' in code
    assert 'prepare_delete_many(CONFIG, root, identities, protected=protected)' in code
    assert 'commit_delete(plan)' in code
    assert 'color=\"#c62828\"' in code
    assert 'フォルダー：' in code and '末端メニューアイテム：' in code
    assert "unregister = launch_sub.addAction('登録解除...')" in code
    assert 'unreg.setEnabled(False)' not in code
    assert 'future_del.setEnabled(False)' not in code


def test_cli_preview_commit_and_no_physical_delete(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source / Node not supplied')
    cfg=tmp_path/'launch.json';doc=nested();cfg.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    physical=tmp_path/'keep_me';physical.mkdir();(physical/'important.txt').write_text('do not delete',encoding='utf-8')
    initial=cfg.read_bytes()
    plan=prepare_delete(cfg,studio,'work','delete_me')
    assert cfg.read_bytes()==initial
    assert (plan['folders'],plan['leaves'],plan['deleted'])==(2,2,5)
    result=commit_delete(plan)
    assert result['status']=='COMMITTED'
    rows=json.loads(cfg.read_text(encoding='utf-8'))['items']
    assert not any(r['item_id'] in {'delete_me','sub','local_dir','child_url','child_cmd'} for r in rows)
    assert any(r['item_id']=='folders' for r in rows)
    assert physical.is_dir() and (physical/'important.txt').read_text()=='do not delete'


def test_sha_conflict_after_confirmation_prevents_delete(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source / Node not supplied')
    cfg=tmp_path/'launch.json';cfg.write_text(json.dumps(nested(),ensure_ascii=False),encoding='utf-8')
    plan=prepare_delete(cfg,studio,'work','delete_me')
    changed=nested();changed['title']='another writer'
    cfg.write_text(json.dumps(changed,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(RegistrationError,match='CONFLICT'):
        commit_delete(plan)
    assert cfg.read_text(encoding='utf-8')==json.dumps(changed,ensure_ascii=False)


def test_files_exp_anchor_protected_before_preview(tmp_path):
    file=tmp_path/'launch.json';file.write_text(json.dumps(sample(),ensure_ascii=False),encoding='utf-8')
    with pytest.raises(RegistrationError,match='内部管理ルート'):
        prepare_delete(file,tmp_path,'system','folders',protected=(('system','folders'),))
