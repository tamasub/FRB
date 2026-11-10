"""1の手: one configured item is selected only by upward flick.

Pure-model regression, independent of the user's changing personal JSON.
Green eye rendering takes its selected ID directly from choose_entry's result.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import (configured_entries, choose_entry,
                            current_indicator_position, FIRST_HAND_SLOTS)


def one():
    data = {'items': [dict(item_id='one', title='ONE', enabled=True,
                            shuriken_enabled=True, shuriken_order=10,
                            shuriken_button_index=1,
                            shuriken_direction='down')]}
    rows = configured_entries(data)
    assert len(rows) == 1
    assert rows[0].direction == 'up'  # JSON's old direction is ignored
    assert FIRST_HAND_SLOTS[1] == ('up',)
    return rows


@pytest.mark.parametrize('dx,dy,selected', [
    (0, -50, True),
    (12, -50, True),
    (-12, -50, True),
    (0, -14, True),
    (0, -13, False),  # 14px drag deadzone
    (0, 0, False),
    (0, 50, False),  # observed bug: downward flick moved the eye upward
    (50, 0, False),
    (-50, 0, False),
    (50, -50, False),  # diagonal boundary, not a deliberate upward flick
    (-50, -50, False),
    (50, 50, False),
    (-50, 50, False),
])
def test_one_hand_flick_direction_and_eye_agree(dx, dy, selected):
    rows = one()
    choice = choose_entry(rows, dx, dy, min_release_distance=14)
    assert (choice is rows[0]) == selected
    selected_id = choice.item_id if choice else ''
    assert current_indicator_position(rows, selected_id) == (
        (0.0, -42.0) if selected else (0.0, 0.0))


def test_one_hand_uses_same_choice_for_visual_eye_and_release():
    # The UI must not re-select on mouse release.
    view = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
    assert 'self._selected_entry = choose_entry(' in view
    assert 'self._preview.present(self, self._entries, self._selected_entry)' in view
    assert 'chosen = self._selected_entry' in view
    assert 'self._pending_confirmation = FirstHandConfirmation(' in view
    assert 'self.triggered.emit(approved)' in view


def test_other_counts_keep_current_clockwise_mapping():
    for count, dirs in ((2, ('left', 'right')),
                        (3, ('up_left', 'up_right', 'down')),
                        (4, ('up', 'right', 'down', 'left'))):
        data = {'items': [dict(item_id=f'item_{i}', title=f'item_{i}', enabled=True,
                               shuriken_enabled=True, shuriken_order=i * 10,
                               shuriken_button_index=1)
                          for i in range(count)]}
        assert tuple(r.direction for r in configured_entries(data)) == dirs
