"""Integration: reorder actual Files Exp registered directory records via Studio CLI."""
import json
import os
from pathlib import Path
import shutil
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from launch_menu_registration import prepare_move, commit_move
from registered_root_studio import verified_registered_root


def test_files_root_directory_reorder_via_studio_cli(tmp_path):
    studio = os.environ.get('FRB_STUDIO_TEST_ROOT')
    if not studio or not shutil.which('node'):
        pytest.skip('Studio Move CLI and Node are not available')
    source = json.loads((ROOT / 'config/frb_launch_data.json').read_text('utf-8'))
    # These are genuine registered roots in System/Files; leave PC fixed.
    first = next(row for row in source['items'] if row.get('item_id') == 'frb_root_folder')
    second = next(row for row in source['items'] if row.get('item_id') == 'studio_dir')
    assert first.get('parent_item_id') == second.get('parent_item_id') == 'folders'
    root = tmp_path / 'launch.json'
    root.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding='utf-8')
    before = root.read_bytes()
    plan = prepare_move(root, studio, 'system', second['item_id'], {
        'group_id': 'system', 'parent_id': 'folders',
        'position': 'before', 'anchor_id': first['item_id']})
    assert plan is not None
    assert root.read_bytes() == before  # dry-run must not change JSON
    commit_move(plan)
    after = json.loads(root.read_text('utf-8'))
    ids = [r['item_id'] for r in sorted((r for r in after['items'] if
           r.get('page_id') == 'system' and r.get('parent_item_id') == 'folders'),
           key=lambda r:r.get('sort_order') or 0)]
    assert ids.index(second['item_id']) < ids.index(first['item_id'])
    # PC and every physical path stay byte-for-byte the same string.
    assert {r['item_id']:r.get('launch_browse_target') for r in source['items']} == {
        r['item_id']:r.get('launch_browse_target') for r in after['items']}
