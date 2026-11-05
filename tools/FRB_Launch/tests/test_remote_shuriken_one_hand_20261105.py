"""Pure contract / integration tests for FRB Remote 手裏剣 1の手."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from core import load, searchable_rows, validate
from shuriken_model import (configured_entries, choose_entry, direction_of,
                            sector_entries, spoke_angles, MAX_ITEMS_PER_HAND)
from launch_virtual_tree import virtual_launch_pages


@pytest.fixture
def data():
    return load(ROOT / 'config/frb_launch_sample_data_v0_1.json')


def source(path):
    return (ROOT / path).read_text(encoding='utf-8')


def test_user_config_registers_three_real_actions_in_one_hand(data):
    entries = configured_entries(data, 1)
    assert len(entries) == 3
    assert [x.item_id for x in entries] == [
        'zip_studio', 'launch_source_zip', 'shuriken_git_commit_filename']
    assert [x.direction for x in entries] == ['up_left', 'up_right', 'down']
    assert entries[0].context_action_id == ''
    assert entries[1].context_action_id == ''
    assert entries[2].context_action_id == 'git_commit_from_zip'
    assert configured_entries(data, 2) == []
    assert all(row.hand_index == 1 for row in entries)


def test_buttons_not_limited_to_four_or_one_per_sector(data):
    assert MAX_ITEMS_PER_HAND >= 10
    rows = [r for r in data['items'] if r.get('shuriken_enabled')]
    assert len(rows) == 3
    assert len(sector_entries(configured_entries(data, 1), 'up_left')) == 1
    assert len(sector_entries(configured_entries(data, 1), 'up_right')) == 1
    assert len(sector_entries(configured_entries(data, 1), 'down')) == 1


@pytest.mark.parametrize('dx,dy,direction', [
    (0, -40, 'up'), (50, -50, 'up_right'), (40, 0, 'right'),
    (40, 40, 'down_right'), (0, 40, 'down'), (-40, 40, 'down_left'),
    (-40, 0, 'left'), (-40, -40, 'up_left'), (0, 0, ''),
])
def test_all_eight_direction_sectors(dx,dy,direction):
    assert direction_of(dx, dy) == direction


def test_fixed_circle_upper_lower_and_caption_overflow(data):
    rows = configured_entries(data, 1)
    assert spoke_angles([rows[0]], 'up_left') == [-135.0]  # legacy helper
    src = source('src/remote_shuriken.py')
    assert 'RADIUS = 72' in src
    assert 'GAP_ABOVE_BUTTON = 15' in src
    assert 'painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))' in src
    assert 'band = (radius * 2.0) / count' in src
    assert 'painter.drawEllipse(QPointF(mark_x, mark_y),' in src
    assert 'for angle in THREE_SECTOR_DIVIDERS:' in src
    assert 'painter.drawLine(QPointF(0, 0), QPointF(radius * math.cos(theta),' in src
    assert 'painter.drawText(text_rect,' in src
    assert 'painter.rotate(180)' not in src
    assert 'setPixelSize(self.LABEL_FONT_PX)' in src
    assert 'self._preview.present(self, self._entries, None)' in src
    assert 'self._preview.present(self, self._entries, choice)' in src



def test_three_way_blind_flicks_match_wedge_labels_and_click_cancels(data):
    entries = configured_entries(data, 1)
    assert choose_entry(entries, -40, -30).item_id == 'zip_studio'
    assert choose_entry(entries, 40, -30).item_id == 'launch_source_zip'
    assert choose_entry(entries, 0, 47).item_id == 'shuriken_git_commit_filename'
    assert choose_entry(entries, 0, 0) is None
    assert choose_entry(entries, 0, 20) is None
    # Straight up is the visible divider between two upper wedges.
    assert choose_entry(entries, 0, -47) is None



def test_exactly_ten_actions_per_button_still_supported(data):
    import copy
    draft = copy.deepcopy(data)
    template = next(x for x in draft['items'] if x.get('shuriken_enabled'))
    directions = ('up', 'up_right', 'right', 'down_right', 'down',
                  'down_left', 'left', 'up_left')
    for i in range(7):
        clone = copy.deepcopy(template)
        clone['item_id'] = f'shuriken_extra_{i}'
        clone['shuriken_direction'] = directions[i]
        clone['shuriken_order'] = 100 + i
        draft['items'].append(clone)
    assert len(configured_entries(validate(draft), 1)) == 10


def test_reject_eleven_menu_items_same_button(data):
    import copy
    draft = copy.deepcopy(data)
    template = next(x for x in draft['items'] if x.get('shuriken_enabled'))
    for i in range(8):
        clone = copy.deepcopy(template)
        clone['item_id'] = f'shuriken_extra_{i}'
        draft['items'].append(clone)
    with pytest.raises(ValueError, match='最大10件'):
        validate(draft)


def test_reject_unsupported_context_dispatch(data):
    import copy
    draft = copy.deepcopy(data)
    row = next(x for x in draft['items'] if x.get('shuriken_context_action_id'))
    row['shuriken_context_action_id'] = 'delete'
    with pytest.raises(ValueError, match='未対応の手裏剣'):
        validate(draft)


def test_context_only_action_hidden_from_normal_launch_menu_and_search(data):
    assert all(row.get('item_id') != 'shuriken_git_commit_filename'
               for row, _ in searchable_rows(data, 'ファイル名を使ってGitコミット'))
    # The virtual Files tree is also a projection of the main JSON.
    pages = virtual_launch_pages(data['pages'], data['items'])
    assert 'shuriken_git_commit_filename' not in repr(pages)
    src = source('src/app.py')
    assert 'and not x.get(\'shuriken_only\', False)' in src


def test_button_location_icon_and_runtime_action_dispatch():
    remote = source('src/launch_remote.py')
    assert 'self.shuriken_button = ShurikenButton(launcher, self, hand_index=1)' in remote
    assert remote.index('row_quick.addWidget(self.shuriken_button)') < remote.index('row_quick.addWidget(self.home_button)')
    assert "'HOME', width=68, height=46" in remote
    assert "'REMOTE_KANA_TOGGLE', width=50, height=46" in remote
    view = source('src/remote_shuriken.py')
    assert "f'{self.hand_index}の手'" in view
    assert "assets' / 'remote_shuriken.png'" in view
    app = source('src/app.py')
    assert "if command.startswith('SHURIKEN_ITEM:')" in app
    assert "self.perform_filesystem_context_action(context_action, paths[0], 'file')" in app
    assert 'self.execute(row)' in app
    assert "len(paths) != 1 or not Path(paths[0]).is_file()" in app


def test_studio_can_edit_shuriken_properties():
    definition = json.loads(source('defs/launch/frb_launch_maintenance_view_def_v0_1.json'))
    fields = definition['views'][0]['sections'][1]['fields']
    indexed = {row['field']: row for row in fields}
    for key in ('shuriken_enabled', 'shuriken_button_index', 'shuriken_direction',
                'shuriken_order', 'shuriken_context_action_id'):
        assert indexed[key]['edit']['visible'] is True
    assert indexed['shuriken_enabled']['type'] == 'boolean'
