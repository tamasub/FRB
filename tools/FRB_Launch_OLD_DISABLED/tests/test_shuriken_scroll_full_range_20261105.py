"""One shuriken throw targets the real Files List scroll END, not 2,000px.

The user should have time to brake, even on very long lists. Qt-free tests
exercise actual release -> timer -> scroll signal with lightweight test doubles.
"""
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from shuriken_scroll_model import (plan_flick,
                                   plan_full_range_flight, eased_displacement,
                                   FULL_RANGE_MIN_DURATION_S, FULL_RANGE_MAX_DURATION_S)
from test_shuriken_scroll_inertia_20261105 import (scroll_pad, Event, FakeListTree,
                                                  FakeScrollBar)


def flick(dy=-55, duration=.08):
    return [(0.0, 100, 100), (duration * .6, 100, 100 + dy * .7),
            (duration, 100, 100 + dy)]


def test_up_flick_from_middle_travels_all_remaining_units_without_cap():
    gesture = plan_flick(flick(-55))
    flight = plan_full_range_flight(gesture, current=340, minimum=0,
                                    maximum=321_000, page_step=500)
    assert flight.distance_px == 320_660
    assert flight.distance_px > 2000
    assert FULL_RANGE_MIN_DURATION_S <= flight.duration_s <= FULL_RANGE_MAX_DURATION_S
    assert eased_displacement(flight, flight.duration_s) == 320_660


def test_down_flick_from_middle_travels_to_minimum():
    gesture = plan_flick(flick(+55))
    flight = plan_full_range_flight(gesture, current=18_123, minimum=100,
                                    maximum=210_000, page_step=800)
    assert flight.distance_px == -(18_123 - 100)
    assert eased_displacement(flight, flight.duration_s) == -18_023


def test_existing_edge_and_invalid_ranges_do_not_launch():
    up = plan_flick(flick(-45))
    down = plan_flick(flick(+45))
    assert plan_full_range_flight(up, 400, 0, 400, 600) is None
    assert plan_full_range_flight(down, 0, 0, 400, 600) is None
    assert plan_full_range_flight(up, 1200, 0, 400, 600) is None
    assert plan_full_range_flight(up, 200, 500, 400, 600) is None
    assert plan_full_range_flight(None, 200, 0, 400, 600) is None
    assert plan_full_range_flight(up, 200, 0, 400, None) is None


def test_strength_changes_duration_not_distance():
    weak = plan_flick(flick(-45, .27))
    strong = plan_flick(flick(-45, .035))
    a = plan_full_range_flight(weak, 5, 0, 15_000, 650)
    b = plan_full_range_flight(strong, 5, 0, 15_000, 650)
    assert a.distance_px == b.distance_px == 14_995
    assert b.duration_s < a.duration_s
    assert b.duration_s > 2.8  # pause to brake; not a 1-second flash


def test_scroll_distance_depends_on_remaining_range_not_a_global_cap():
    gesture = plan_flick(flick(-60))
    near = plan_full_range_flight(gesture, 19_500, 0, 20_000, 600)
    far = plan_full_range_flight(gesture, 500, 0, 20_000, 600)
    assert near.distance_px == 500
    assert far.distance_px == 19_500
    assert far.duration_s > near.duration_s


def test_release_launches_full_distance_to_bottom_and_stops_at_edge():
    module, pad = scroll_pad()
    clock = [100.0]
    bar = FakeScrollBar(position=260, maximum=14_000, page_step=600)
    tree = FakeListTree(bar)
    pad.target_provider = lambda: tree
    # Spy on the output, while updating the *real* bar as Launch does.
    # The lightweight FakeSignal records output without automatically
    # invoking connected callbacks, so apply emitted deltas explicitly.
    original_emit = pad.scroll_requested.emit
    def apply_and_record(delta):
        original_emit(delta)
        bar.setValue(bar.value() + delta)
    pad.scroll_requested.emit = apply_and_record
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        pad.mousePressEvent(Event(100, 100))
        clock[0] += .05
        pad.mouseMoveEvent(Event(100, 60))
        assert bar.value() == 260   # No movement while held.
        clock[0] += .03
        pad.mouseReleaseEvent(Event(100, 40))
        assert pad._timer.active
        assert pad._flight.distance_px == 14_000 - 260
        assert pad._flight.duration_s > 2.8
        duration = pad._flight.duration_s
        clock[0] += duration * .25
        pad._scroll_tick()
        assert 260 < bar.value() < 14_000  # Braking is possible mid-flight.
        clock[0] += duration
        pad._scroll_tick()
        assert bar.value() == 14_000
        assert pad._flight is None and not pad._timer.active


def test_short_click_brakes_before_end_and_continues_to_target():
    module, pad = scroll_pad()
    clock = [50.0]
    bar = FakeScrollBar(position=5_000, maximum=30_000, page_step=450)
    tree = FakeListTree(bar)
    pad.target_provider = lambda: tree
    pad.scroll_requested.emit = lambda delta: bar.setValue(bar.value() + delta)
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        pad.mousePressEvent(Event(100, 100))
        clock[0] += .07
        pad.mouseReleaseEvent(Event(100, 30))
        duration = pad._flight.duration_s
        clock[0] += duration * .30
        pad._scroll_tick()
        mid_position = bar.value()
        assert 5_000 < mid_position < 30_000
        pad.mousePressEvent(Event(100, 100))
        assert pad._flight is not None and pad._timer.active
        clock[0] += .02
        pad.mouseReleaseEvent(Event(100, 100))
        assert 0 < pad._cruise_rate < 1
        clock[0] += duration * .20
        pad._scroll_tick()
        assert mid_position < bar.value() < 30_000
        clock[0] += duration * 4
        pad._scroll_tick()
        assert bar.value() == 30_000 and pad._flight is None


def test_changed_scrollbar_range_cancels_stale_destination():
    module, pad = scroll_pad()
    clock = [1.0]
    bar = FakeScrollBar(position=500, maximum=5_000)
    tree = FakeListTree(bar)
    pad.target_provider = lambda: tree
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(100, 100))
        clock[0] += .05
        pad.mouseReleaseEvent(Event(100, 35))
        assert pad._timer.active
        bar.high = 3_000
        clock[0] += .2
        pad._scroll_tick()
        assert not pad._timer.active and pad._flight is None
        assert not pad.scroll_requested.emitted
