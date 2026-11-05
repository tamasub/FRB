"""Three 120-degree visual/gesture agreement, without PySide6."""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import (configured_entries, choose_entry, three_sector_slot,
                            uses_three_sector_guide, THREE_SECTOR_DIVIDERS)


def entries():
    data = json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text('utf-8'))
    return configured_entries(data, 1)


def test_three_sectors_match_reference_picture_and_real_action_ids():
    rows = entries()
    assert uses_three_sector_guide(rows)
    mapping = {e.direction: e.item_id for e in rows}
    assert mapping == {'up_left': 'zip_studio',
                       'up_right': 'launch_source_zip',
                       'down': 'shuriken_git_commit_filename'}
    label_positions = {e.direction: three_sector_slot(e)[:2] for e in rows}
    assert label_positions['up_left'][0] < 0
    assert label_positions['up_right'][0] > 0
    assert label_positions['down'][1] > 0
    assert THREE_SECTOR_DIVIDERS == (-90.0, 30.0, 150.0)


@pytest.mark.parametrize('dx,dy,expected', [
    (-40,-35,'zip_studio'), (40,-35,'launch_source_zip'),
    (0,47,'shuriken_git_commit_filename'),
    (0,0,None), (0,12,None), (0,-40,None),
])
def test_flick_and_cancel(dx,dy,expected):
    selected = choose_entry(entries(), dx, dy)
    assert (selected.item_id if selected else None) == expected


def test_current_circle_diameter_48_fits_each_wedge():
    # Radius 72; marker center 42. Nearest edge of a 120-degree sector:
    # 42*sin(60deg) > 24; outer-ring margin 72-42 > 24.
    for row in entries():
        _, _, marker_x, marker_y = three_sector_slot(row)
        distance = math.hypot(marker_x, marker_y)
        assert distance + 24 < 72
        assert distance * math.sin(math.radians(60)) > 24


def test_two_menu_legacy_up_down_flick_behavior_is_retained():
    two = [row for row in entries() if row.direction != 'up_left']
    # Legacy 2-menu layout has true up/down directions.
    from shuriken_model import ShurikenEntry
    two = [ShurikenEntry('launch','Launch',1,'up',10),
           ShurikenEntry('git','Git',1,'down',20)]
    assert choose_entry(two,0,-45).item_id == 'launch'
    assert choose_entry(two,0,45).item_id == 'git'
    assert choose_entry(two,0,0) is None


def test_paint_uses_same_geometry_as_model_and_does_not_preselect():
    source = (ROOT/'src/remote_shuriken.py').read_text('utf-8')
    assert 'uses_three_sector_guide(self.entries)' in source
    assert 'three_sector_slot(entry)' in source
    assert 'THREE_SECTOR_DIVIDERS' in source
    assert 'self._preview.present(self, self._entries, None)' in source
    assert 'CURRENT_RADIUS = 24' in source
