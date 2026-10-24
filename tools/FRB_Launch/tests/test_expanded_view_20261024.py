"""No Qt needed: View/Data isolation and first-level-only contracts."""
import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_view_model import (normalize_options, page_roots, expanded_targets,
                                 should_expand)


def sample():
    return json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf8'))


def test_sample_has_both_targets_and_all_work_roots():
    items = sample()['items']
    options = normalize_options(json.loads((ROOT / 'config/expanded_view_options.json').read_text(encoding='utf8')))
    roots, left, right = expanded_targets(items, options)
    assert left['title'] == 'Files'
    assert right['title'] == 'ブックマーク'
    assert {'設定', 'ZIP', 'Files', 'ブックマーク', 'Quick', '日付・定型文', 'メール宛先'} <= {r['title'] for r in roots}
    assert all(not row.get('parent_item_id') for row in roots)


def test_page_roots_sorts_and_excludes_subfolders():
    items = [dict(item_id='c', page_id='work', title='C', sort_order=30),
             dict(item_id='b', page_id='work', title='B', sort_order=10),
             dict(item_id='a', page_id='work', title='A', parent_item_id='b'),
             dict(item_id='d', page_id='other', title='D'),
             dict(item_id='e', page_id='work', title='E', enabled=False)]
    assert [row['item_id'] for row in page_roots(items, 'work')] == ['b', 'c']


@pytest.mark.parametrize('kwargs,expected', [
    ({}, True),
    ({'view_mode': 'classic'}, False),
    ({'page_id': 'windows'}, False),
    ({'query': 'abc'}, False),
    ({'stack': [{'item_id': 'zip'}]}, False),
    ({'selection': {'item_id': 'x'}}, False),
    ({'available': False}, False),
])
def test_activation_condition(kwargs, expected):
    base = dict(view_mode='expanded', page_id='work', query='', stack=[],
                selection=None, options=normalize_options(None), available=True)
    base.update(kwargs)
    assert should_expand(**base) == expected


def test_bad_configuration_fails_safely():
    with pytest.raises(ValueError):
        normalize_options({'files_item_id': '__browser_bookmarks_root'})
    with pytest.raises(ValueError):
        normalize_options({'enabled': 'true'})


def test_missing_target_or_wrong_kind_disables_expanded():
    options = normalize_options(None)
    rows = sample()['items']
    assert expanded_targets([r for r in rows if r.get('item_id') != options['files_item_id']], options) is None
    bad = [dict(r, item_kind='command') if r.get('item_id') == options['files_item_id'] else r for r in rows]
    assert expanded_targets(bad, options) is None


def test_app_wiring_and_python_syntax():
    app = (ROOT / 'src/app.py').read_text(encoding='utf8')
    view = (ROOT / 'src/expanded_view.py').read_text(encoding='utf8')
    ast.parse(app)
    ast.parse(view)
    for token in ('toggle_expanded_view', 'update_expanded_visibility',
                  'expanded_window_width', 'self.expanded_view.refresh(',
                  'self.expanded_view.setVisible(active)'):
        assert token in app
    for token in ('QSplitter', 'QTreeWidget', 'open_expanded_cascade',
                  'show_launch_context_menu', 'save_splitter_sizes'):
        assert token in view
