"""Shuriken contract: 3-way blind flick + round preview + text overflow."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import (ShurikenEntry, configured_entries, choose_entry,
                            direction_of)


def sample():
    # Historical 3-action fixture, independent of the live cardinal 4-action JSON.
    data = json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text('utf-8'))
    keep = {'zip_studio': 'up_left', 'launch_source_zip': 'up_right',
            'shuriken_git_commit_filename': 'down'}
    for row in data['items']:
        if row.get('item_id') in keep:
            row['shuriken_direction'] = keep[row['item_id']]
            if row['item_id'] == 'shuriken_git_commit_filename':
                row['shuriken_order'] = 30
        elif row.get('shuriken_enabled'):
            row['shuriken_enabled'] = False
    return data


def preview_source():
    return (ROOT / 'src/remote_shuriken.py').read_text('utf-8')


def test_identifiers_and_three_actions_in_wedge_order():
    entries = configured_entries(sample(), 1)
    assert [(e.order, e.direction) for e in entries] == [
        (10, 'up_left'), (20, 'up_right'), (30, 'down')]
    assert [e.item_id for e in entries] == [
        'zip_studio', 'launch_source_zip', 'shuriken_git_commit_filename']


@pytest.mark.parametrize('dx,dy,expected', [
    (-40, -40, 'zip_studio'), (-80, -60, 'zip_studio'),
    (40, -40, 'launch_source_zip'), (80, -60, 'launch_source_zip'),
    (0, 35, 'shuriken_git_commit_filename'),
    (0, 120, 'shuriken_git_commit_filename'),
    (0, 0, None), (0, -20, None), (0, -50, None),
])
def test_blind_flick_action_without_visual_preview(dx, dy, expected):
    selected = choose_entry(configured_entries(sample(), 1), dx, dy)
    assert (selected.item_id if selected else None) == expected


def test_titles_are_not_involved_in_selection():
    entries = configured_entries(sample(), 1)
    long_title = '長いメニュー名' * 120
    amended = [ShurikenEntry(e.item_id, long_title, e.hand_index,
                             e.direction, e.order, e.context_action_id)
               for e in entries]
    for xy in ((0, -40), (0, 40), (55, 0)):
        baseline = choose_entry(entries, *xy)
        changed = choose_entry(amended, *xy)
        assert (changed.item_id if changed else None) == (baseline.item_id if baseline else None)


def test_ui_full_circle_is_fixed_above_button():
    src = preview_source()
    assert 'RADIUS = 72' in src
    assert 'GAP_ABOVE_BUTTON = 15' in src
    assert 'button.mapToGlobal(QPoint(button.width() // 2, 0))' in src
    assert 'cy = button_top.y() - self.GAP_ABOVE_BUTTON - self.RADIUS' in src
    assert 'painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))' in src
    assert 'band = (radius * 2.0) / count' in src
    assert 'self._preview.present(self, self._entries, None)' in src
    assert 'self._preview.present(self, self._entries, choice)' in src


def test_ui_does_not_expand_circle_to_fit_long_menu_names():
    src = preview_source()
    assert 'radius = self.RADIUS' in src
    assert 'metrics.horizontalAdvance(caption)' in src
    assert 'painter.drawText(text_draw_rect,' in src
    assert 'Qt.TextElideMode.ElideRight' in src
    assert 'painter.rotate(180)' not in src
    assert 'painter.setClipPath' not in src
    assert 'LABEL_FONT_PX = 12' in src


def test_ui_shows_white_origin_and_selection_indicator():
    src = preview_source()
    assert 'CURRENT_RADIUS = 24' in src
    assert 'MARKER_RADIUS = 12.5' in src
    assert 'current_indicator_position(' in src
    assert src.index('self.CURRENT_RADIUS, self.CURRENT_RADIUS)') < src.index('self.MARKER_RADIUS, self.MARKER_RADIUS)')
    assert 'active = entry.item_id == self.selected_id' in src
    assert 'painter.drawEllipse(QPointF(marker_x, marker_y),' in src
    assert "self.selected_id = selected.item_id if selected is not None else ''" in src



def test_ui_does_not_need_preview_to_complete_fast_throw():
    src = preview_source()
    release = src[src.index('    def mouseReleaseEvent('):src.index('    def hideEvent(')]
    assert 'chosen = choose_entry(self._entries, dx, dy)' in release
    assert 'self.triggered.emit(chosen.item_id)' in release
    assert 'self._preview.hide()' in release
    assert 'if chosen is not None:' in release


def test_preview_does_not_capture_mouse_or_activate_window():
    src = preview_source()
    assert 'Qt.WindowType.WindowTransparentForInput' in src
    assert 'Qt.WindowType.WindowDoesNotAcceptFocus' in src
    assert 'Qt.WidgetAttribute.WA_ShowWithoutActivating' in src


def test_only_one_hand_instance_and_same_action_ids():
    remote = (ROOT / 'src/launch_remote.py').read_text('utf-8')
    app = (ROOT / 'src/app.py').read_text('utf-8')
    assert "ShurikenButton(launcher, self, hand_index=1)" in remote
    assert "'SHURIKEN_ITEM:' + item_id" in remote
    assert "self.execute_shuriken_item(item_id)" in app
