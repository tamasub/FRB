"""2026-11-11: Files Exp empty ROOT routes to System/Files (not Page)."""
import ast
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import (
    files_exp_root_target, eligible_parent, RegistrationError,
    records_for_sources,
)


def data():
    return json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8'))


def test_root_target_is_files_category_not_system_page_and_title_is_unimportant():
    doc = data()
    anchor = next(x for x in doc['items'] if x['item_id'] == 'folders')
    anchor['title'] = '設定JSONのタイトルを変えても表示はFiles'
    assert files_exp_root_target(doc, {'page_id': 'system', 'files_item_id': 'folders'}) == ('system', 'folders')
    eligible_parent(doc, 'system', 'folders')
    root_children = [x for x in doc['items'] if x.get('parent_item_id') == 'folders']
    assert root_children and all(x['page_id'] == 'system' for x in root_children)


def test_root_target_fails_closed_if_anchor_missing_or_not_category():
    doc = data()
    with pytest.raises(RegistrationError):
        files_exp_root_target(doc, {'page_id': 'work', 'files_item_id': 'folders'})
    for item in doc['items']:
        if item['item_id'] == 'folders':
            item['item_kind'] = 'command'
    with pytest.raises(RegistrationError):
        files_exp_root_target(doc, {'page_id': 'system', 'files_item_id': 'folders'})


def test_registered_directory_records_still_use_launch_schema(tmp_path):
    folder = tmp_path / '新しいフォルダー'
    folder.mkdir()
    row = records_for_sources([{'kind': 'directory', 'value': str(folder), 'title': folder.name}])[0]
    assert row['item_kind'] == 'directory'
    assert row['launch_browse_target'] == str(folder)


def test_both_root_menu_and_drop_use_same_canonical_target():
    text = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    assert 'def _files_exp_root_registration_target(self)' in text
    root_ui = text.split('    def show_launch_root_registration_menu(self, point):', 1)[1].split('    def handle_launch_drop(', 1)[0]
    drop = text.split('    def handle_launch_drop(self, identity, mime):', 1)[1].split('    def show_virtual_launch_context(', 1)[0]
    assert 'self._files_exp_root_registration_target()' in root_ui
    assert 'self._files_exp_root_registration_target()' in drop
    assert 'self._registration_page()' not in root_ui
    assert 'self._registration_page()' not in drop


def test_files_green_header_has_constant_label():
    text = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert "self.left.label.setText('Files')" in text
    assert "self.shared_title.setText('Files')" in text
    assert "self.shared_title.setText(left['title'])" not in text
    ast.parse(text)


def test_studio_cli_persists_directory_beneath_real_files_anchor(tmp_path, monkeypatch):
    """Integration test is opt-in: modifies only a throwaway JSON file."""
    import os
    import shutil
    from launch_menu_registration import commit_add
    root = os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not root or not shutil.which('node'):
        pytest.skip('Studio CLI / Node not supplied')
    config = tmp_path / 'launch.json'
    config.write_bytes((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_bytes())
    folder = tmp_path / 'Dropped Root Folder'
    folder.mkdir()
    doc = data()
    pid, parent = files_exp_root_target(doc, {'page_id': 'system', 'files_item_id': 'folders'})
    result = commit_add(config, root, pid, parent, records_for_sources([
        {'kind': 'directory', 'value': str(folder), 'title': 'Dropped Root Folder'}
    ]))
    assert result['status'] == 'COMMITTED'
    saved = json.loads(config.read_text(encoding='utf-8-sig'))
    matching = [row for row in saved['items'] if row.get('title') == 'Dropped Root Folder']
    assert len(matching) == 1
    assert matching[0]['page_id'] == 'system'
    assert matching[0]['parent_item_id'] == 'folders'
    assert matching[0]['launch_browse_target'] == str(folder)
