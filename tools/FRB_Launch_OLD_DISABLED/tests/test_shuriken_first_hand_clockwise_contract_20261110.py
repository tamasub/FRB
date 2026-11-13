"""First-hand: up to four positions; sectors track the actual active count.

Studio provides order/membership only. Launch must never use authored direction.
The green eye, displayed labels and release selection use the same mapping.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from core import validate
from shuriken_model import (
    configured_entries, choose_entry, uses_three_sector_guide,
    uses_four_sector_guide, uses_two_horizontal_sector_guide,
    current_indicator_position, two_first_hand_sector_slot,
    three_sector_slot, four_sector_slot, THREE_SECTOR_DIVIDERS,
    MAX_ITEMS_PER_HAND, FIRST_HAND_SLOTS,
)


def sample():
    return json.loads((ROOT / 'config/frb_launch_data.json').read_text('utf-8'))


def items_of_count(count):
    """Make a source draft with exactly count first-hand commands, no source edits."""
    draft = copy.deepcopy(sample())
    original = [row for row in draft['items'] if row.get('shuriken_enabled')]
    assert len(original) >= 1  # User-editable JSON can register 1..many.
    for row in draft['items']:
        row['shuriken_enabled'] = False
    for idx in range(count):
        if idx < len(original):
            row = next(r for r in draft['items'] if r['item_id'] == original[idx]['item_id'])
        else:
            row = copy.deepcopy(original[0])
            row['item_id'] = f'added_{idx}'
            draft['items'].append(row)
        row['shuriken_enabled'] = True
        row['shuriken_order'] = (idx + 1) * 10
        row['shuriken_direction'] = 'obsolete_value_must_be_ignored'
    return validate(draft)


def test_current_sample_three_clockwise_unchanged():
    entries = configured_entries(items_of_count(3))
    assert MAX_ITEMS_PER_HAND == 4
    assert tuple(e.direction for e in entries) == ('up_left', 'up_right', 'down')
    assert uses_three_sector_guide(entries)
    assert THREE_SECTOR_DIVIDERS == (-90.0, 30.0, 150.0)
    assert choose_entry(entries, -47, -47).item_id == entries[0].item_id
    assert choose_entry(entries, 47, -47).item_id == entries[1].item_id
    assert choose_entry(entries, 0, 47).item_id == entries[2].item_id
    assert choose_entry(entries, 0, -47) is None
    assert current_indicator_position(entries, '') == (0.0, 0.0)
    for entry in entries:
        assert current_indicator_position(entries, entry.item_id) == pytest.approx(
            three_sector_slot(entry)[2:4])


@pytest.mark.parametrize('count, directions, probe', [
    (1, ('up',), ((0, -50),)),
    (2, ('left', 'right'), ((-50, 0), (50, 0))),
    (3, ('up_left', 'up_right', 'down'), ((-50, -50), (50, -50), (0, 50))),
    (4, ('up', 'right', 'down', 'left'), ((0, -50), (50, 0), (0, 50), (-50, 0))),
    (5, ('up', 'right', 'down', 'left'), ((0, -50), (50, 0), (0, 50), (-50, 0))),
    (8, ('up', 'right', 'down', 'left'), ((0, -50), (50, 0), (0, 50), (-50, 0))),
])
def test_each_active_count_has_exactly_its_own_sectors_and_matching_eye(count, directions, probe):
    rows = configured_entries(items_of_count(count))
    assert len(rows) == min(count, 4)
    assert tuple(e.direction for e in rows) == directions
    assert tuple(e.direction for e in rows) == FIRST_HAND_SLOTS[len(rows)]
    assert uses_three_sector_guide(rows) == (len(rows) == 3)
    assert uses_two_horizontal_sector_guide(rows) == (len(rows) == 2)
    assert uses_four_sector_guide(rows) == (len(rows) == 4)
    assert current_indicator_position(rows, '') == (0.0, 0.0)
    for row, (dx, dy) in zip(rows, probe):
        assert choose_entry(rows, dx, dy) == row
        eye = current_indicator_position(rows, row.item_id)
        assert eye is not None
        if len(rows) == 2:
            expected = two_first_hand_sector_slot(row)[2:4]
        elif len(rows) == 3:
            expected = three_sector_slot(row)[2:4]
        elif len(rows) == 4:
            expected = four_sector_slot(row)[2:4]
        else:
            expected = (0.0, -42.0)
        assert eye == pytest.approx(expected)
    assert choose_entry(rows, 0, 0) is None


def test_count_two_shows_only_two_wedges_and_no_bottom_action():
    rows = configured_entries(items_of_count(2))
    assert not uses_three_sector_guide(rows)
    assert choose_entry(rows, -50, 0) == rows[0]
    assert choose_entry(rows, 50, 0) == rows[1]
    assert choose_entry(rows, 0, 50) is None
    assert choose_entry(rows, 0, -50) is None
    assert two_first_hand_sector_slot(rows[0])[-1] == 'right'
    assert two_first_hand_sector_slot(rows[1])[-1] == 'left'


def test_four_way_diagonal_boundary_cancels():
    rows = configured_entries(items_of_count(4))
    for dx,dy in ((50,50),(-50,-50),(50,-50),(-50,50)):
        assert choose_entry(rows,dx,dy) is None


def test_duplicate_priority_preserves_registration_order_and_5th_is_ignored():
    draft = items_of_count(5)
    authored = [r for r in draft['items'] if r.get('shuriken_enabled')]
    for row in authored:
        row['shuriken_order'] = 100
    rows = configured_entries(draft)
    assert [r.item_id for r in rows] == [r['item_id'] for r in authored[:4]]
    assert authored[4]['item_id'] not in [r.item_id for r in rows]
    assert [r.direction for r in rows] == ['up','right','down','left']


def test_studio_and_launch_viewdefs_do_not_author_directions():
    path = ROOT / 'defs/launch/frb_launch_maintenance_view_def_v0_1.json'
    view = json.loads(path.read_text('utf-8'))
    fields = {x['field']: x for x in view['views'][0]['sections'][1]['fields']}
    assert 'shuriken_direction' not in fields
    assert '先頭4件' in fields['shuriken_order']['caption']
    assert fields['shuriken_enabled']['edit']['visible']
    assert fields['shuriken_order']['edit']['visible']
    assert not fields['shuriken_button_index']['edit']['visible']


def test_unconfigured_first_hand_is_empty():
    data=sample()
    for row in data['items']:
        row['shuriken_enabled']=False
    assert configured_entries(data) == []
    assert configured_entries(data,2) == []


def test_circle_geometry_and_eye_authority_are_unchanged():
    source = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
    for value in ('RADIUS = 72', 'CURRENT_RADIUS = 24', 'MARKER_RADIUS = 12.5',
                  'MARKER_DISTANCE = 42'):
        assert value in source
    assert 'for angle in THREE_SECTOR_DIVIDERS:' in source
    assert 'three_sector_slot(entry)' in source
    assert 'two_first_hand_sector_slot(entry)' in source
    assert 'four_sector_slot(entry)' in source
    assert 'chosen = self._selected_entry' in source
    assert 'self.triggered.emit(approved)' in source
    assert 'self._pending_confirmation = FirstHandConfirmation(' in source
