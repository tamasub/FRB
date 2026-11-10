"""Updated contract: all 1–4 first-hand menus use one Launch-owned model.

The old 10:38 baseline is retired. Nothing may launch from the first flick
release: a wheel selection and fresh click are a separate, explicit gate.
"""
import copy
import json
from pathlib import Path
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import configured_entries, choose_entry, current_indicator_position
from first_hand_variable import directions_for_count, choose_variable_entry


def current_config():
    return json.loads((ROOT/'config/frb_launch_sample_data_v0_1.json').read_text('utf-8'))


def with_count(n):
    data = copy.deepcopy(current_config())
    selected = [row for row in data['items'] if row.get('shuriken_enabled')]
    assert selected
    for row in data['items']:
        row['shuriken_enabled'] = False
    for index in range(n):
        if index < len(selected):
            row = selected[index]
        else:
            row = copy.deepcopy(selected[0]);row['item_id'] = f'test_new_{index}'
            data['items'].append(row)
        row['shuriken_enabled'] = True
        row['shuriken_order'] = (index+1)*10
        row['shuriken_direction'] = 'obsolete_shall_not_count'
    return configured_entries(data)


def test_four_uses_same_clockwise_engine_as_one_two_three():
    entries = with_count(4)
    assert [e.direction for e in entries] == ['up','right','down','left']
    directions = [('up',(0,-42)),('right',(42,0)),('down',(0,42)),('left',(-42,0))]
    for direction, position in directions:
        chosen = choose_entry(entries, *position, min_release_distance=14)
        assert chosen is not None and chosen.direction == direction
        assert all(math.isclose(a,b,abs_tol=1e-10) for a,b in
                   zip(current_indicator_position(entries, chosen.item_id), position))


def test_one_to_four_share_one_catalog_and_have_no_phantom_slots():
    probes = {
       1: ((0,-40),),
       2: ((-40,0),(40,0)),
       3: ((-40,-40),(40,-40),(0,40)),
       4: ((0,-40),(40,0),(0,40),(-40,0)),
    }
    for count in (1,2,3,4):
        entries = with_count(count)
        assert len(entries) == count
        assert tuple(e.direction for e in entries) == directions_for_count(count)
        for entry,(dx,dy) in zip(entries,probes[count]):
            assert choose_entry(entries,dx,dy,min_release_distance=14) == entry
            assert choose_variable_entry(entries,dx,dy,distance=14) == entry
        assert choose_entry(entries,0,0,min_release_distance=14) is None
        assert choose_variable_entry(entries,0,0) is None
    assert choose_entry(with_count(1),0,40,min_release_distance=14) is None
    assert choose_entry(with_count(2),0,40,min_release_distance=14) is None
    assert choose_entry(with_count(3),0,-40,min_release_distance=14) is None


def test_old_direction_field_has_no_impact_on_four():
    assert tuple(e.direction for e in with_count(4)) == ('up','right','down','left')


def test_confirmation_intent_is_outside_pure_geometry():
    text=(ROOT/'src/remote_shuriken.py').read_text('utf-8')
    assert 'candidate_id=chosen.item_id, candidate_title=chosen.title' in text
    assert 'self._preview.set_confirmation(self._pending_confirmation)' in text
    assert 'self.triggered.emit(approved)' in text
    assert 'self.triggered.emit(chosen.item_id)' not in text
