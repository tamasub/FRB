"""Public Launch: wheel-edge pushes stay in their current area.

The mechanism remains for older internal code/tests, but it is disabled in the
actual ExpandedLauncherView. No post-jump lock may swallow reverse wheels.
"""
from pathlib import Path
from types import SimpleNamespace

from wheel_zone_navigation import WheelZoneNavigation
from test_wan_middle_files_20261025 import Demo, Event, Mouse, World, Coord

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'expanded_view.py'


def test_public_view_disables_wheel_area_jump_globally():
    text = SOURCE.read_text(encoding='utf8')
    assert 'self.wheel_zone_navigation = WheelZoneNavigation(enabled=False)' in text
    assert 'self.launcher' in text
    # The same controller is used by Files, Bookmarks, Back, root strip and Page.
    assert "self.zone_jump('back')" in text
    assert "self.zone_jump('bookmarks')" in text
    assert "self.zone_jump('directory')" in text
    assert "self.zone_jump('files')" in text


def test_sustained_wheel_at_any_area_edge_does_not_jump_or_lock():
    now = [0.0]
    nav = WheelZoneNavigation(enabled=False, clock=lambda: now[0])
    zones = ('directory-first', 'directory-last', 'files-first', 'files-last',
             'bookmarks-first', 'bookmarks-last', 'back-up',
             'roots-left', 'roots-right')
    for zone in zones:
        for n in range(12):
            now[0] += 0.25
            assert nav.feed(zone, True, 1) is False
            assert not nav.wheel_is_locked()
    assert not nav.locked
    assert nav.holds == {}
    # Even if a stale previous implementation left a lock, disabled mode
    # must not eat the next wheel input.
    nav.locked = True
    assert not nav.wheel_is_locked()
    assert not nav.feed('directory-last', True, 9)


def test_historical_navigation_helper_still_available_for_internal_regression():
    now = [0.0]
    nav = WheelZoneNavigation(enabled=True, clock=lambda: now[0])
    assert not nav.feed('directory-first', True, 1)
    now[0] = .25
    assert not nav.feed('directory-first', True, 1)
    now[0] = .5
    assert nav.feed('directory-first', True, 1)
    assert nav.wheel_is_locked()


def demo_at_edge(*, selected_row, cursor_row, warp_enabled=False, size=7):
    mouse = Mouse
    mouse.current = Coord(20, 100)
    mouse.moves = []
    World.calls = []
    World.buttons = 0
    v = Demo(size=size, hovered=cursor_row)
    v.launcher = SimpleNamespace(pointer_warp_enabled=warp_enabled)
    v.wheel_zone_navigation = WheelZoneNavigation(enabled=False, clock=lambda: 0)
    v._middle_vdi_anchor_pos = None
    v.middle.tree.current = v.middle.tree.items[selected_row]
    v.jumps = []
    v.zone_jump = lambda *args, **kwargs: v.jumps.append((args, kwargs))
    return v


def test_pointer_off_top_edge_reverses_without_dead_wheels():
    v = demo_at_edge(selected_row=0, cursor_row=2)
    for _ in range(12):
        assert v.wheel_middle_at_edge(Event(degrees=120), 0, 0)
        assert v.middle.tree.current == 'item-0'
    assert v.wheel_middle_at_edge(Event(degrees=-120), 0, 0)
    assert v.middle.tree.current == 'item-3'  # deliberate cursor-origin behavior
    assert not v.jumps
    assert Mouse.moves == []


def test_pointer_off_bottom_edge_reverses_without_dead_wheels():
    v = demo_at_edge(selected_row=6, cursor_row=3)
    for _ in range(12):
        assert v.wheel_middle_at_edge(Event(degrees=-120), 0, 0)
        assert v.middle.tree.current == 'item-6'
    assert v.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert v.middle.tree.current == 'item-2'  # cursor-origin, then one step up
    assert not v.jumps
    assert Mouse.moves == []


def test_pointer_on_also_stays_in_same_area_at_top_edge():
    v = demo_at_edge(selected_row=0, cursor_row=0, warp_enabled=True)
    for _ in range(8):
        assert v.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert not v.jumps
    assert v.wheel_middle_at_edge(Event(degrees=-120), 0, 0)
    assert v.middle.tree.current == 'item-1'
    assert not v.jumps
