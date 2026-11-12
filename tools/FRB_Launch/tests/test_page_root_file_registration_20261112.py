"""Page-root file registration: one Studio Add path, Files List only."""
import ast
import json
import os
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import (eligible_parent, normalize_sources,
                                      records_for_sources, commit_add)
from launch_virtual_tree import virtual_launch_pages, virtual_exp_folders, virtual_list_rows


def test_page_context_uses_same_registration_actions_with_file_enabled():
    app_source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    source_tree = ast.parse(app_source)
    method = next(n for cl in source_tree.body if isinstance(cl, ast.ClassDef)
                  for n in cl.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and n.name == 'show_virtual_launch_context')
    registered = [call for call in ast.walk(method)
                  if isinstance(call, ast.Call)
                  and isinstance(call.func, ast.Attribute)
                  and call.func.attr == '_add_registration_menu_actions']
    assert len(registered) == 1  # no second Page-only implementation
    kwargs = {arg.arg: arg.value for arg in registered[0].keywords}
    assert isinstance(kwargs['allow_file'], ast.Constant)
    assert kwargs['allow_file'].value is True
    # No register-to-Page action is implemented separately from the usual Studio Add.
    assert 'self._registration_commit(chosen_page, str(parent_id or \'\'), records)' in app_source


def test_page_direct_file_visible_in_list_never_in_exp(tmp_path):
    file = tmp_path / 'テスト資料.md'
    file.write_text('Page直下のファイル', encoding='utf-8')
    pages = [{'page_id': 'work', 'title': '仕事', 'enabled': True}]
    assert eligible_parent({'pages': pages, 'items': []}, 'work', '')['item_kind'] == 'page'
    record = records_for_sources(normalize_sources([{'value': str(file)}]))[0]
    record.update(page_id='work', parent_item_id='', item_id='registered_md', sort_order=1)
    page = virtual_launch_pages(pages, [record])[0]
    assert [node['item_id'] for node in page['children']] == ['registered_md']
    assert virtual_exp_folders(page) == []
    visible = virtual_list_rows(page)
    assert len(visible) == 1
    assert visible[0]['title'] == file.name
    assert visible[0]['item_kind'] == 'virtual_launch_file'
    assert visible[0]['_launch_virtual_node']['row']['launch_actions'][0]['launch_target'] == str(file.resolve())


def test_page_direct_file_commits_through_studio_and_is_list_only(tmp_path):
    studio = os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio CLI not provided')
    config = tmp_path / 'launch.json'
    config.write_bytes((ROOT / 'config/frb_launch_data.json').read_bytes())
    created_file = tmp_path / '画面設計.md'
    created_file.write_text('# test', encoding='utf-8')
    before = json.loads(config.read_text(encoding='utf-8'))
    records = records_for_sources(normalize_sources([{'value': str(created_file)}]))
    result = commit_add(config, studio, 'work', '', records)
    assert result['status'] == 'COMMITTED'
    data = json.loads(config.read_text(encoding='utf-8'))
    assert len(data['items']) == len(before['items']) + 1
    inserted = next(row for row in data['items'] if row['title'] == created_file.name)
    assert inserted['page_id'] == 'work'
    assert inserted.get('parent_item_id', '') == ''
    page = next(p for p in virtual_launch_pages(data['pages'], data['items'])
                if p['page_id'] == 'work')
    exp_ids = {n['item_id'] for n in virtual_exp_folders(page)}
    list_ids = {n['item_id'] for n in virtual_list_rows(page)}
    assert inserted['item_id'] not in exp_ids
    assert inserted['item_id'] in list_ids
