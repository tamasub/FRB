"""studio_work_0269 / simple edit contract and remote selector regression."""
import ast
import json
import os
from pathlib import Path
import shutil
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from launch_menu_registration import (read_item_for_edit,prepare_update,commit_update,RegistrationError)


def test_gui_three_fields_no_path_ui_and_remote_assisted_dialogs():
    app=(ROOT/'src/app.py').read_text(encoding='utf-8')
    remote=(ROOT/'src/remote_confirmation.py').read_text(encoding='utf-8')
    ast.parse(app)
    assert "def launch_simple_edit_action(self, page_id, item_id):" in app
    section=app.split('def launch_simple_edit_action(self, page_id, item_id):',1)[1].split('def launch_unregister_action',1)[0]
    assert "QLabel('アイコン'" in section and "QLabel('タイトル'" in section and "QLabel('説明'" in section
    assert "QLabel('パス'" not in section
    assert "RemoteTextDialog(self, dialog, title_editor, buttons)" in section
    assert 'commit_update(plan)' in section
    assert "simple.setEnabled(False)" not in app
    assert "future_edit.setEnabled(False)" not in app
    delete=app.split('def launch_unregister_action',1)[1].split('def show_virtual_launch_context',1)[0]
    assert 'self.ask_remote_confirmation(' in delete
    assert "yes_text='登録解除'" in delete
    assert 'dialog.exec()' not in delete
    assert 'self.dialog.button(self.YES).setText(yes_text)' in remote


def test_update_roundtrip_and_path_untouched(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source / Node not supplied')
    original=json.loads((ROOT/'config/frb_launch_data.json').read_text(encoding='utf-8'))
    row=next(r for r in original['items'] if r.get('item_id')=='folders')
    cfg=tmp_path/'launch.json';cfg.write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8')
    item,base=read_item_for_edit(cfg,row['page_id'],'folders')
    assert item['item_id']=='folders'
    changes=[{'path':'title','value':'Files 改訂'}, {'path':'description','value':'説明改訂'}, {'path':'icon_key','value':'folder.green'}]
    plan=prepare_update(cfg,studio,row['page_id'],'folders',changes,base_sha256=base)
    result=commit_update(plan)
    assert result['status']=='COMMITTED' and result['summary']['changed_existing']==1
    new=json.loads(cfg.read_text(encoding='utf-8'))
    changed=next(r for r in new['items'] if r.get('item_id')=='folders')
    for key in ('title','description','icon_key'):
        assert changed[key]==next(c['value'] for c in changes if c['path']==key)
    for key in ('launch_actions','launch_browse_target','item_id','parent_item_id','page_id','sort_order'):
        assert changed.get(key)==item.get(key)
    assert len(new['items'])==len(original['items'])


def test_dialog_stale_sha_rejects_and_preserves_external_edit(tmp_path):
    studio=os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio source / Node not supplied')
    original=json.loads((ROOT/'config/frb_launch_data.json').read_text(encoding='utf-8'))
    cfg=tmp_path/'launch.json';cfg.write_text(json.dumps(original,ensure_ascii=False),encoding='utf-8')
    row,base=read_item_for_edit(cfg,'system','folders')
    original['title']='external edit';cfg.write_text(json.dumps(original,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(RegistrationError,match='CONFLICT'):
        prepare_update(cfg,studio,'system','folders',[{'path':'title','value':'unsafe'}],base_sha256=base)
    assert json.loads(cfg.read_text(encoding='utf-8'))['title']=='external edit'


def test_studio_context_is_detail_edit_but_filesystem_properties_are_unchanged():
    source=(ROOT/'src/app.py').read_text(encoding='utf-8')
    assert "properties_action = menu.addAction('詳細編集...')" in source
    assert source.count("menu.addAction('詳細編集...',") == 2
    assert "detail = launch_sub.addAction('詳細編集...')" in source
    assert "detail.triggered.connect(" in source
    assert "menu.addAction('プロパティ')" not in source
    assert "menu.addAction('プロパティ'," not in source
    assert "'Windowsのプロパティ'" in source
    assert "menu.addMenu('Launch Menu')" in source
