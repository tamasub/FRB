"""Reusable no-Qt wheel gestures for navigation between GUI regions.

A sustained wheel push *past* a list/button boundary requests a destination.
After a warp, ignore further wheel navigation until the wheel has been quiet
for ``quiet_seconds``. In particular, momentum must never chain multiple
region jumps or accidentally activate an item.
"""
import time
from wheel_edge_hold import EdgeWheelHold


class WheelZoneNavigation:
    def __init__(self, min_seconds=0.45, min_steps=3,
                 max_gap=0.75, quiet_seconds=0.9, clock=None):
        self.clock = clock or time.monotonic
        self.min_seconds = min_seconds
        self.min_steps = min_steps
        self.max_gap = max_gap
        self.quiet_seconds = quiet_seconds
        self.holds = {}
        self.last_wheel = None
        self.locked = False

    def wheel_is_locked(self):
        """True means discard this wheel event; clicks still work normally."""
        if not self.locked:
            return False
        now = self.clock()
        if self.last_wheel is not None and now - self.last_wheel > self.quiet_seconds:
            self.locked = False
            self.holds.clear()
            self.last_wheel = now
            return False
        self.last_wheel = now
        return True

    def feed(self, zone, at_boundary, steps):
        """Return True on a sustained *extra* push beyond this zone's edge."""
        if self.locked:
            return False
        hold = self.holds.get(zone)
        if hold is None:
            hold = EdgeWheelHold(self.min_seconds, self.min_steps,
                                 self.max_gap, clock=self.clock)
            self.holds[zone] = hold
        if not hold.feed(at_boundary, steps):
            return False
        self.locked = True
        self.last_wheel = self.clock()
        self.holds.clear()
        return True

    def reset(self, zone):
        hold = self.holds.get(zone)
        if hold is not None:
            hold.reset()
