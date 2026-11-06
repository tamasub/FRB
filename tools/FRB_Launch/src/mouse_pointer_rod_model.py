"""Geometry only for the opt-in Mouse Pointer Rod experiment.

The *real* mouse stays inside the Remote pad.  This module never moves a
cursor, clicks, or depends on a target application.  Qt owns the painting.
"""
from __future__ import annotations

import math

DEFAULT_DIRECTION = (0.60, -0.80)
DEFAULT_LENGTH = 420
MIN_LENGTH = 80
MAX_LENGTH = 3000
# v0.5: normal wheel = precise 15px; left-button-held wheel = fast 60px.
# Pointer radius is irrelevant to the length or gear.
NORMAL_WHEEL_STEP_PX = 15
FAST_WHEEL_STEP_PX = 60


def length_after_wheel(length, steps, *, fast=False):
    """Wheel-only length: 15px normally; 60px with left button held."""
    step = FAST_WHEEL_STEP_PX if fast else NORMAL_WHEEL_STEP_PX
    return max(MIN_LENGTH, min(MAX_LENGTH, float(length) + int(steps) * step))


def pointer_distance(origin, pointer):
    """Radial mouse distance inside the control pad, independent of direction."""
    return math.hypot(float(pointer[0]) - float(origin[0]),
                      float(pointer[1]) - float(origin[1]))



def direction_from_pointer(origin, pointer, previous=DEFAULT_DIRECTION, deadzone=5.0):
    """Normalize pointer displacement; retain the last angle near the origin."""
    dx = float(pointer[0]) - float(origin[0])
    dy = float(pointer[1]) - float(origin[1])
    distance = math.hypot(dx, dy)
    return (dx / distance, dy / distance) if distance >= deadzone else previous


def rod_endpoint(origin, direction, length):
    """Absolute desktop tip coordinate, not a physical cursor position."""
    return (float(origin[0]) + float(direction[0]) * float(length),
            float(origin[1]) + float(direction[1]) * float(length))
