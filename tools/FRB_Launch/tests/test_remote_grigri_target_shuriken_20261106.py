"""Current-dot and column-only selector tests for the new ぐりぐり hold menu."""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import (ShurikenEntry, choose_entry,
    uses_two_horizontal_sector_guide, two_horizontal_sector_slot,
    current_indicator_position)


def exp_list():
    return [
        ShurikenEntry('REMOTE_TARGET_EXP', 'Exp列', 0, 'left', 0),
        ShurikenEntry('REMOTE_TARGET_LIST', 'List列', 0, 'right', 1),
    ]


def test_pair_is_horizontal_not_legacy_vertical():
    entries = exp_list()
    assert uses_two_horizontal_sector_guide(entries)
    assert uses_two_horizontal_sector_guide(entries[::-1])
    assert not uses_two_horizontal_sector_guide([
        ShurikenEntry('a', 'A', 1, 'up', 1), ShurikenEntry('b', 'B', 1, 'down', 2)])
    assert two_horizontal_sector_slot(entries[0]) == (-38, 18, -42, 0.0, 'center')
    assert two_horizontal_sector_slot(entries[1]) == (38, 18, 42, 0.0, 'center')


@pytest.mark.parametrize('dx,dy,expected', [
    (-72, 0, 'REMOTE_TARGET_EXP'),
    (72, 0, 'REMOTE_TARGET_LIST'),
    (-29, 0, 'REMOTE_TARGET_EXP'),
    (29, 0, 'REMOTE_TARGET_LIST'),
    (0, 0, None), (-20, 0, None), (20, 0, None),
    (-60, 60, None), (60, 60, None), (-60, -60, None), (60, -60, None),
    (0, -72, None), (0, 72, None),
    (-28, 25, None), (28, -25, None),
])
def test_canonical_left_right_and_ambiguous_boundaries(dx, dy, expected):
    entry = choose_entry(exp_list(), dx, dy)
    assert (entry.item_id if entry else None) == expected


def test_current_pokemon_eye_moves_from_center_without_current_row_change():
    entries = exp_list()
    assert current_indicator_position(entries) == (0, 0)
    assert current_indicator_position(entries, 'REMOTE_TARGET_EXP') == (-42, 0)
    assert current_indicator_position(entries, 'REMOTE_TARGET_LIST') == (42, 0)
    assert current_indicator_position(entries[::-1], 'REMOTE_TARGET_EXP') == (-42, 0)


def test_old_two_item_vertical_guide_remains_unchanged():
    entries = [ShurikenEntry('above', '上', 1, 'up', 1),
               ShurikenEntry('below', '下', 1, 'down', 2)]
    assert current_indicator_position(entries, 'above') == (0, -42)
    assert current_indicator_position(entries, 'below') == (0, 42)
    assert choose_entry(entries, 0, -40).item_id == 'above'


def test_preview_draws_left_right_split_with_existing_white_ring_and_dot():
    preview = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
    assert 'horizontal_pair = uses_two_horizontal_sector_guide(self.entries)' in preview
    assert 'painter.drawLine(QPointF(0, -radius), QPointF(0, radius))' in preview
    assert 'two_horizontal_sector_slot(entry)' in preview
    assert 'current_indicator_position(' in preview
    assert 'self.CURRENT_RADIUS, self.CURRENT_RADIUS' in preview
    assert 'self.MARKER_RADIUS, self.MARKER_RADIUS' in preview


def test_uses_existing_column_target_command_not_arrows():
    remote = (ROOT / 'src/launch_remote.py').read_text('utf-8')
    app = (ROOT / 'src/app.py').read_text('utf-8')
    assert "ShurikenEntry('REMOTE_TARGET_EXP', 'Exp列', 0, 'left', 0)" in remote
    assert "ShurikenEntry('REMOTE_TARGET_LIST', 'List列', 0, 'right', 1)" in remote
    assert "self.command.emit('LEFT' if dx < 0 else 'RIGHT')" not in remote
    assert "if command in ('REMOTE_TARGET_EXP', 'REMOTE_TARGET_LIST'):" in app
    assert "target = 'files_exp' if command == 'REMOTE_TARGET_EXP' else 'directory'" in app
    assert 'def set_files_operating_target(self, target):' in app
    assert 'self.remote_list_left_to_exp()' in app  # retained for physical ← button


def test_actual_target_setter_does_not_move_list_current_or_selection():
    """Execute the real Launcher setter with UI fakes, not just source grep."""
    import ast
    from types import SimpleNamespace as NS
    from unittest.mock import Mock

    source = (ROOT / 'src/app.py').read_text('utf8')
    launcher = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
    setter = next(n for n in launcher.body
                  if isinstance(n, ast.FunctionDef)
                  and n.name == 'set_files_operating_target')
    scope = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[setter], type_ignores=[])),
                 'app.py', 'exec'), scope)

    class Tree:
        def __init__(self):
            self.cursor = 'row-19'
            self.selected = ['row-19', 'row-23']
            self.remote_highlight_mode = False
            self.remote_logical_active = False
            self.properties = {}
            self.style_ = NS(unpolish=Mock(), polish=Mock())
            self.viewport_ = NS(update=Mock())
        def property(self, k): return self.properties.get(k)
        def setProperty(self, k, v): self.properties[k] = v
        def style(self): return self.style_
        def viewport(self): return self.viewport_

    left, middle = Tree(), Tree()
    view = NS(_workspace_mode='files',
              left=NS(tree=left), middle=NS(tree=middle),
              set_files_operating_area=Mock(),
              current_directory=lambda: 'F:/FRB/current')
    exp_panel = NS(_selection_timer=NS(stop=Mock()), set_operating_active=Mock())
    remote = NS(files_exp_panel=exp_panel, set_operating_target=Mock(), set_area=Mock())
    app = NS(expanded_view=view, remote_window=remote,
             files_exp_embedded_mode=True, files_exp_panels=lambda: [exp_panel],
             _files_operating_target='directory', _remote_area='directory',
             _last_focus_area='directory')

    before = (view.current_directory(), middle.cursor, list(middle.selected),
              left.cursor, list(left.selected))
    assert scope['set_files_operating_target'](app, 'files_exp') is True
    assert app._files_operating_target == 'files_exp'
    assert scope['set_files_operating_target'](app, 'directory') is True
    assert app._files_operating_target == 'directory'
    assert before == (view.current_directory(), middle.cursor, middle.selected,
                      left.cursor, left.selected)
    assert view.set_files_operating_area.call_count == 2
    assert remote.set_operating_target.call_count == 2
    # No setCurrentItem, select, expand, navigate or breadcrumb operation.


def test_exp_list_labels_are_inward_and_above_moving_eye():
    """Labels remain readable when the eye occupies the horizontal sector."""
    left, right = [two_horizontal_sector_slot(e) for e in exp_list()]
    assert left[0] == -right[0]
    assert left[1] == right[1] > 0
    assert abs(left[0]) < 62  # Previous left label was outside the circle.
    assert left[4] == right[4] == 'center'
    assert left[2:4] == (-42, 0.0) and right[2:4] == (42, 0.0)
