"""FRB Launch 2026-11-05: four-way kana flick and 2-4 guide current dot.

No Qt dependency: numerical geometry, JSON action binding and source contract.
Live Windows paint/mouse capture still require on-device inspection.
"""
from pathlib import Path
import json
import math
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import (
    ShurikenEntry, choose_entry, configured_entries, uses_four_sector_guide,
    uses_three_sector_guide, four_sector_slot, three_sector_slot,
    current_indicator_position,
)


def live_entries():
    return configured_entries(json.loads(
        (ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text('utf8')), 1)


def legacy_four_entries():
    """Four-sector geometry remains available to non-first-hand consumers."""
    return [
        ShurikenEntry('a', 'A', 1, 'up', 10),
        ShurikenEntry('b', 'B', 1, 'right', 20),
        ShurikenEntry('c', 'C', 1, 'down', 30),
        ShurikenEntry('d', 'D', 1, 'left', 40),
    ]


def legacy_three_entries():
    return [
        ShurikenEntry('a', 'A', 1, 'up_left', 10),
        ShurikenEntry('b', 'B', 1, 'up_right', 20),
        ShurikenEntry('c', 'C', 1, 'down', 30),
    ]


def two_entries():
    return [ShurikenEntry('a', 'A', 1, 'up', 1),
            ShurikenEntry('b', 'B', 1, 'down', 2)]


def test_existing_four_cardinal_primitive_remains_usable():
    entries = legacy_four_entries()
    assert len(entries) == 4
    assert uses_four_sector_guide(entries)
    assert {e.direction: e.item_id for e in entries} == {
        'up': 'a', 'right': 'b', 'down': 'c', 'left': 'd'}


def test_three_actions_have_three_sectors_from_priority():
    import copy
    data = json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text('utf8'))
    # The authored live count changes; construct exactly three actions.
    enabled = [row for row in data['items'] if row.get('shuriken_enabled')]
    for row in data['items']:
        row['shuriken_enabled'] = False
    for idx in range(3):
        if idx < len(enabled):
            row = enabled[idx]
        else:
            row = copy.deepcopy(enabled[0])
            row['item_id'] = 'test_third_first_hand'
            data['items'].append(row)
        row['shuriken_enabled'] = True
        row['shuriken_order'] = (idx+1)*10
    entries = configured_entries(data, 1)
    assert len(entries) == 3
    assert uses_three_sector_guide(entries)
    assert [(e.order, e.direction) for e in entries] == [
        (10, 'up_left'), (20, 'up_right'), (30, 'down')]


@pytest.mark.parametrize('dx,dy,expected', [
    (0, -70, 'a'),
    (70, 0, 'b'),
    (0, 70, 'c'),
    (-70, 0, 'd'),
    (0, 0, None),
    (0, -20, None),
    (50, -50, None), (50, 50, None), (-50, 50, None), (-50, -50, None),
])
def test_four_compass_flick_and_boundary_cancel(dx, dy, expected):
    choice = choose_entry(legacy_four_entries(), dx, dy)
    assert (choice.item_id if choice else None) == expected


def test_idle_is_center_and_selection_dots_match_all_four_axes():
    entries = legacy_four_entries()
    assert current_indicator_position(entries, '') == (0, 0)
    assert current_indicator_position(entries, 'missing') == (0, 0)
    expected = {'up': (0, -42), 'right': (42, 0),
                'down': (0, 42), 'left': (-42, 0)}
    for entry in entries:
        xy = current_indicator_position(entries, entry.item_id)
        assert xy == pytest.approx(expected[entry.direction])
        assert xy == pytest.approx(four_sector_slot(entry)[2:4])
        assert math.hypot(*xy) + 12.5 < 72
        assert math.hypot(*xy) - 12.5 > 24


def test_two_and_three_have_center_origin_and_one_moving_dot():
    for entries in (two_entries(), legacy_three_entries()):
        assert current_indicator_position(entries, '') == (0, 0)
        for row in entries:
            xy = current_indicator_position(entries, row.item_id)
            assert xy is not None
            assert math.hypot(*xy) == pytest.approx(42)
            assert current_indicator_position(entries, '') != xy
    assert current_indicator_position(list(reversed(two_entries())), 'a') == (0, -42)
    assert current_indicator_position(list(reversed(two_entries())), 'b') == (0, 42)
    assert uses_three_sector_guide(legacy_three_entries())
    for row in legacy_three_entries():
        assert current_indicator_position(legacy_three_entries(), row.item_id) == pytest.approx(
            three_sector_slot(row)[2:4])
    assert current_indicator_position([]) is None
    assert current_indicator_position([two_entries()[0]]) == (0.0, 0.0)


def test_preview_uses_model_dot_white_center_x_and_dialog_safety_remains():
    source = (ROOT/'src/remote_shuriken.py').read_text('utf8')
    assert 'current_indicator_position(' in source
    assert '1 <= count <= 4' in source
    assert "painter.setBrush(QColor('#ffffff'))" in source
    assert "painter.setBrush(QColor('#aed2a0'))" in source
    assert 'CURRENT_RADIUS = 24' in source
    assert 'MARKER_RADIUS = 12.5' in source
    assert 'diagonal = radius / math.sqrt(2.0)' in source
    assert 'painter.drawLine(QPointF(-diagonal, -diagonal)' in source
    assert 'painter.drawLine(QPointF(-diagonal, diagonal)' in source
    assert source.index('self.CURRENT_RADIUS, self.CURRENT_RADIUS)') < source.index('self.MARKER_RADIUS, self.MARKER_RADIUS)')
    assert 'self._preview.present(self, self._entries, None)' in source
    assert 'self._preview.present(self, self._entries, self._selected_entry)' in source
    # Candidate release is inert; only a new wheel-confirm click executes.
    assert 'self._pending_confirmation = FirstHandConfirmation(' in source
    assert 'self.triggered.emit(approved)' in source
    assert 'pending.commit(clicked_inside)' in source
    assert 'self._commit_first_hand_confirmation(clicked_inside=inside)' in source
