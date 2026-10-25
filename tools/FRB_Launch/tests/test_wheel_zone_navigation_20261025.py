import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from wheel_zone_navigation import WheelZoneNavigation


def test_sustained_extra_wheel_and_lock_requires_quiet():
    now = [0.0]
    nav = WheelZoneNavigation(clock=lambda: now[0])
    assert not nav.feed('page-last', True, 1)
    now[0] = .24
    assert not nav.feed('page-last', True, 1)
    now[0] = .48
    assert nav.feed('page-last', True, 1)
    # Even after a long spin, do not cascade to a second destination.
    for timestamp in (.6, .9, 1.4):
        now[0] = timestamp
        assert nav.wheel_is_locked()
        assert not nav.feed('root-last', True, 5)
    now[0] = 2.35
    assert not nav.wheel_is_locked()
    assert not nav.feed('root-last', True, 1)


def test_arrival_reset_and_reverse_direction():
    now = [0.0]
    nav = WheelZoneNavigation(clock=lambda: now[0])
    nav.feed('files-last', True, 1)
    now[0] = .3
    nav.feed('files-last', False, 1)
    now[0] = .5
    assert not nav.feed('files-last', True, 2)
    now[0] = 1.0
    assert nav.feed('files-last', True, 1)


def test_gap_discards_old_sequence():
    now = [0.0]
    nav = WheelZoneNavigation(clock=lambda: now[0])
    nav.feed('bookmarks-last', True, 1)
    now[0] = .8
    assert not nav.feed('bookmarks-last', True, 1)
    now[0] = 1.4
    assert nav.feed('bookmarks-last', True, 2)
