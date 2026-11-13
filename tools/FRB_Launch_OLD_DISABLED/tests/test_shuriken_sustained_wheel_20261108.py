"""Regression: deliberate continuous one-notch wheel must arm shuriken.

Qt-free tests. Keep wheel-area jump disabled and the user's fast-trigger
parameters intact; this only adds a sustained-gesture alternative.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from guriguri_shuriken_auto import WheelShurikenGate
from wheel_zone_navigation import WheelZoneNavigation


def sequence(gate, intervals, *, steps=-1, source='list', initial=100.0):
    return [gate.feed(steps, now=initial + dt, source=source) for dt in intervals]


def test_80ms_single_notch_stream_arms_instead_of_missing_forever():
    ticks = [i * .080 for i in range(30)]
    output = sequence(WheelShurikenGate(), ticks)
    assert -1 in output[:9]  # Within the first 7-9 notches.
    assert output[0] == 0


def test_100ms_single_notch_stream_still_arms():
    output = sequence(WheelShurikenGate(), [i * .100 for i in range(9)])
    assert -1 in output


def test_brief_or_sporadic_wheels_stay_normal():
    assert sequence(WheelShurikenGate(), [0, .08, .16, .24]) == [0]*4
    assert sequence(WheelShurikenGate(), [i*.180 for i in range(20)]) == [0]*20
    assert WheelShurikenGate().feed(-20, now=10.0) == 0


def test_direction_flip_and_source_change_restart_sustained_count():
    gate = WheelShurikenGate()
    first = sequence(gate, [i*.08 for i in range(6)], initial=10.)
    assert first == [0]*6
    assert gate.feed(1, now=10.48) == 0
    assert sequence(gate, [.56, .64, .72], steps=1, initial=10.) == [0]*3

    gate = WheelShurikenGate()
    assert sequence(gate, [i*.08 for i in range(5)], initial=20.) == [0]*5
    assert gate.feed(-1, source='remote', now=20.40) == 0
    assert sequence(gate, [.48, .56], source='remote', initial=20.) == [0]*2


def test_fast_burst_still_works_while_zone_jump_is_off():
    nav = WheelZoneNavigation(enabled=False)
    gate = WheelShurikenGate()
    output = []
    for dt in (0.0, 0.075, 0.150, 0.225):
        output.append(gate.feed(-2, now=30+dt))
        assert not nav.feed('directory-last', True, 2)
        assert not nav.wheel_is_locked()
    assert output == [0,0,0,-1]


def test_cooldown_and_reverse_are_preserved():
    g = WheelShurikenGate()
    out = sequence(g, [i*.08 for i in range(8)], initial=50.)
    assert out.count(-1) == 1
    assert g.feed(+5, now=50.6) == 0  # Recent launch cannot immediately rearm.
    assert g.feed(+1, now=51.5) == 0  # New direction begins a new sequence.


def test_tuning_knobs_and_original_engine_left_intact():
    source = (ROOT/'src/guriguri_shuriken_auto.py').read_text('utf-8')
    view = (ROOT/'src/expanded_view.py').read_text('utf-8')
    app = (ROOT/'src/app.py').read_text('utf-8')
    assert 'AUTO_SHURIKEN_MIN_RATE_NPS = 25.0' in source
    assert 'AUTO_SHURIKEN_SUSTAINED_MIN_EVENTS = 7' in source
    assert 'WheelZoneNavigation(enabled=False)' in view
    assert 'self.wheel_middle_at_edge(event, at, at, movement_override=-remaining)' in view
    assert 'pad.start_from_wheel(direction, source=source)' in app


def test_sustained_gate_can_start_existing_scroll_engine():
    """Gate -> existing engine, without any inter-area wheel jump."""
    from test_guriguri_shuriken_auto_20261108 import make_auto_pad
    _, pad, _tree, _bar = make_auto_pad(position=6000, maximum=20000)
    gate = WheelShurikenGate()
    launched = False
    for i in range(12):
        direction = gate.feed(-1, now=80.0 + i*.08, source='list')
        if direction:
            launched = pad.start_from_wheel(direction, source='list')
            break
    assert launched
    assert pad._flight is not None
    assert pad._flight.full_range
