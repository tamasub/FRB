"""End-arrival scene and tap-to-slow/hold-to-stop experiments (Qt-free)."""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_scroll_model import (ScrollFlight, arrival_progress,
                                   eased_displacement, ARRIVAL_DECEL_START)
from test_shuriken_scroll_inertia_20261105 import scroll_pad, Event, FakeListTree, FakeScrollBar


def launched_pad(clock, module, pad, *, maximum=50000):
    bar = FakeScrollBar(position=700, maximum=maximum, page_step=700)
    tree = FakeListTree(bar)
    pad.target_provider = lambda: tree
    pad.scroll_requested.emit = lambda delta: bar.setValue(bar.value() + delta)
    pad.mousePressEvent(Event(100,100))
    clock[0] += .04
    pad.mouseMoveEvent(Event(100,60))
    clock[0] += .02
    pad.mouseReleaseEvent(Event(100,30))
    assert pad._flight is not None
    assert pad._flight.full_range
    return module, pad, bar


def test_end_deceleration_begins_after_about_80_percent_of_distance():
    progress = arrival_progress(ARRIVAL_DECEL_START)
    assert .79 <= progress <= .83
    assert arrival_progress(0) == 0
    assert arrival_progress(1) == 1
    assert all(arrival_progress(i/200) <= arrival_progress((i+1)/200)
               for i in range(200))


def test_end_speed_slows_strongly_in_the_last_third_of_flight():
    flight = ScrollFlight(100_000, 10.0, 900, full_range=True)
    increments = [eased_displacement(flight, 10 * (i+1)/100)
                  - eased_displacement(flight, 10 * i/100)
                  for i in range(100)]
    assert increments[15] < increments[33]  # accelerate early
    assert increments[32] > increments[80] * 2.0
    assert increments[80] > increments[92] * 3.0
    assert abs(sum(increments) - 100000) < .001
    reverse = ScrollFlight(-100_000, 10.0, 900, full_range=True)
    assert eased_displacement(reverse, 10) == -100_000


def test_arrival_label_switches_only_during_end_approach():
    module, pad = scroll_pad()
    clock=[10.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        _, pad, bar = launched_pad(clock, module, pad)
        duration = pad._flight.duration_s
        assert pad._caption.text() == '滑走中'
        clock[0] += duration * .58
        pad._scroll_tick()
        assert pad._caption.text() == '滑走中'
        clock[0] += duration * .08
        pad._scroll_tick()
        assert pad._caption.text() == '終点間近'
        assert bar.value() < bar.maximum()
        clock[0] += duration
        pad._scroll_tick()
        assert pad._caption.text() == '手裏剣↕'
        assert bar.value() == bar.maximum()


def test_short_brake_preserves_endpoint_and_reduces_virtual_time_speed():
    module, pad=scroll_pad()
    clock=[20.0]
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        _, pad, bar = launched_pad(clock, module, pad)
        target = bar.maximum()
        duration = pad._flight.duration_s
        clock[0] += duration*.22
        pad._scroll_tick()
        old_elapsed = pad._flight_elapsed_s
        pad.mousePressEvent(Event(100,100))
        clock[0] += .10
        pad._scroll_tick()
        assert pad._flight_elapsed_s-old_elapsed < .05
        pad.mouseReleaseEvent(Event(100,100))
        assert .4 < pad._cruise_rate < .5
        assert pad._caption.text() == '減速中'
        earlier = pad._flight_elapsed_s
        clock[0] += .2
        pad._scroll_tick()
        assert .07 < pad._flight_elapsed_s-earlier < .1
        assert bar.value() < target
        clock[0] += duration*3
        pad._scroll_tick()
        assert bar.value()==target
        assert pad._flight is None


def test_two_short_taps_slow_progressively_and_holding_while_running_stops():
    module,pad=scroll_pad()
    clock=[30.0]
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        _, pad, bar=launched_pad(clock, module, pad)
        clock[0]+=.15
        pad._scroll_tick()
        for _ in range(2):
            pad.mousePressEvent(Event(100,100))
            clock[0]+=.05
            pad.mouseReleaseEvent(Event(100,100))
        assert .17 < pad._cruise_rate < .20
        assert pad._flight is not None
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.54
        pad._scroll_tick()  # stops even without release
        frozen=bar.value()
        assert pad._flight is None and not pad._timer.active
        pad.mouseReleaseEvent(Event(100,100))
        clock[0]+=6
        pad._scroll_tick()
        assert bar.value()==frozen


def test_holding_without_a_running_flight_never_launches():
    module,pad=scroll_pad()
    clock=[40.0]
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(100,100))
        clock[0]+=1.0
        pad.mouseReleaseEvent(Event(100,100))
        assert pad._flight is None and not pad._timer.active
