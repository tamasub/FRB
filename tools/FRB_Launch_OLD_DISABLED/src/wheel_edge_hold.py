"""Detect sustained extra upward wheel motion at the top of a list.

This is intentionally Qt-free: the Experience layer can reuse it in other
views. The caller must verify that scrolling is at the upper bound, row 0 is
current, and the pointer is within the intended list viewport.
"""
import time


class EdgeWheelHold:
    def __init__(self, min_seconds=0.45, min_steps=3, max_gap=0.75, clock=None):
        self.min_seconds = min_seconds
        self.min_steps = min_steps
        self.max_gap = max_gap
        self.clock = clock or time.monotonic
        self.reset()

    def reset(self):
        self.first = None
        self.last = None
        self.steps = 0
        self.fired = False

    def feed(self, at_edge, steps=0):
        """Return True once per sustained episode; never trigger on arrival."""
        if not at_edge or steps <= 0:
            self.reset()
            return False
        now = self.clock()
        if self.last is None or now - self.last > self.max_gap:
            self.first = now
            self.steps = 0
            self.fired = False
        self.last = now
        self.steps += steps
        if (not self.fired and self.steps >= self.min_steps and
                now - self.first >= self.min_seconds):
            self.fired = True
            return True
        return False
