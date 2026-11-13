"""Regression: with cursor movement OFF, wheel never reverses logical current.

The tests mimic the exact failure: after reaching the scrollbar's lower edge,
Qt briefly moves the scrollbar, which resets the old follow anchor; the fixed
mouse position continues hovering a row five items above the selected one.
"""
from types import SimpleNamespace

from wheel_adaptive import monotonic_edge_anchor
from test_wan_middle_files_20261025 import (Demo, Event, Mouse, World,
                                             Coord)


def setup_function():
    Mouse.current = Coord(20, 100)
    Mouse.moves = []
    World.calls = []
    World.buttons = 0


def test_direction_guard_accepts_only_progress_in_requested_direction():
    assert monotonic_edge_anchor(19, 14, 1) == 19
    assert monotonic_edge_anchor(19, 23, 1) == 23
    assert monotonic_edge_anchor(14, 19, -1) == 14
    assert monotonic_edge_anchor(19, 14, -1) == 14
    assert monotonic_edge_anchor(None, 14, 1) == 14
    assert monotonic_edge_anchor(19, None, -1) == 19
    assert monotonic_edge_anchor(None, None, 1) is None


def test_stationary_cursor_near_bottom_never_reverses_on_down_wheel():
    view = Demo(size=30, hovered=24, max_scroll=100)
    view.launcher = SimpleNamespace(pointer_warp_enabled=False)
    tree = view.middle.tree
    tree.current = tree.items[28]
    view._middle_vdi_anchor_pos = None  # reset by prior real scroll
    current_indices = []
    for i in range(7):
        # Even if native Qt scroll occasionally advances, then stops again,
        # the anchor must not relocate to the fixed hover row.
        if i == 2:
            assert not view.wheel_middle_at_edge(Event(), 98, 100)
            assert view._middle_vdi_anchor_pos is None
        assert view.wheel_middle_at_edge(Event(), 100, 100)
        current_indices.append(tree.indexOfTopLevelItem(tree.current))
    assert current_indices == [29] * 7
    assert not Mouse.moves
    assert not World.calls


def test_fixed_pointer_while_down_at_edge_advances_not_bounce_to_hover():
    view = Demo(size=30, hovered=24, max_scroll=100)
    view.launcher = SimpleNamespace(pointer_warp_enabled=False)
    tree = view.middle.tree
    tree.current = tree.items[25]
    for _ in range(4):
        assert view.wheel_middle_at_edge(Event(), 100, 100)
    assert tree.current is tree.items[29]
    assert not Mouse.moves


def test_reverse_wheel_really_moves_in_reverse_at_edge():
    view = Demo(size=30, hovered=24)
    view.launcher = SimpleNamespace(pointer_warp_enabled=False)
    tree = view.middle.tree
    tree.current = tree.items[29]
    assert view.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert tree.current is tree.items[23]
    assert view.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert tree.current is tree.items[22]


def test_fixed_pointer_maintains_one_row_precision_when_follow_anchor_alive():
    view = Demo(size=30, hovered=24)
    view.launcher = SimpleNamespace(pointer_warp_enabled=False)
    view._middle_vdi_anchor_pos = Mouse.current
    tree = view.middle.tree
    tree.current = tree.items[29]
    assert view.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert tree.current is tree.items[28]
    assert not Mouse.moves


def test_pointer_warp_on_keeps_original_hover_as_anchor():
    view = Demo(size=30, hovered=24)
    view.launcher = SimpleNamespace(pointer_warp_enabled=True)
    tree = view.middle.tree
    tree.current = tree.items[29]
    assert view.wheel_middle_at_edge(Event(), 0, 0)
    assert tree.current is tree.items[25]  # original hover+one down
    assert len(World.calls) == 1
