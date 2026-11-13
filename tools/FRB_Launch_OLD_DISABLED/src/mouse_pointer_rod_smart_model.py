"""Qt-free geometry for Smart Mouse Pointer Rod (experimental, opt-in).

The vertical wheel controls the TIP's Y coordinate while preserving its X.
The real cursor follows the new ray, constrained inside the blue aiming pad
and outside the embedded ぐりぐり button.  No Windows input is sent here.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SmartRodResult:
    length: float
    direction: tuple[float, float]
    tip: tuple[float, float]
    cursor: tuple[float, float]


def _ray_box_interval(origin, direction, rect, maximum):
    """Distance interval of a ray inside an axis-aligned closed rectangle."""
    lo, hi = 0.0, float(maximum)
    for point, unit, lower, upper in zip(origin, direction,
                                         (rect[0], rect[1]), (rect[2], rect[3])):
        if abs(unit) < 1e-10:
            if point < lower or point > upper:
                return None
        else:
            a, b = (lower - point) / unit, (upper - point) / unit
            lo = max(lo, min(a, b))
            hi = min(hi, max(a, b))
            if hi < lo:
                return None
    return (lo, hi)


def _cursor_on_ray(origin, direction, length, cursor, blue, forbidden, margin):
    """Keep cursor near its old radial distance, without leaving the pad.

    Rectangles are (left, top, right, bottom) in the same coordinates as tip.
    Both blue insets and the central-button exclusion have a safety margin.
    """
    blue_inner = (blue[0] + margin, blue[1] + margin,
                  blue[2] - margin, blue[3] - margin)
    if blue_inner[0] > blue_inner[2] or blue_inner[1] > blue_inner[3]:
        return None
    interval = _ray_box_interval(origin, direction, blue_inner, length)
    if interval is None:
        return None
    segments = [interval]
    if forbidden is not None:
        inflated = (forbidden[0] - margin, forbidden[1] - margin,
                    forbidden[2] + margin, forbidden[3] + margin)
        block = _ray_box_interval(origin, direction, inflated, length)
        if block is not None:
            left, right = interval
            blocked_start, blocked_end = block
            segments = []
            if left < blocked_start:
                segments.append((left, min(blocked_start - 0.01, right)))
            if blocked_end < right:
                segments.append((max(blocked_end + 0.01, left), right))
    distance = math.hypot(cursor[0] - origin[0], cursor[1] - origin[1])
    possible = [max(a, min(distance, b)) for a, b in segments if a <= b]
    if not possible:
        return None
    r = min(possible, key=lambda value: abs(value - distance))
    return (origin[0] + r * direction[0],
            origin[1] + r * direction[1])


def smart_vertical_step(origin, old_tip, old_cursor, vertical_pixels,
                        blue_rect, forbidden_rect=None, *,
                        min_length=80.0, max_length=3000.0,
                        margin=3.0):
    """Return feasible new geometry or None if no vertical progress is possible.

    `vertical_pixels`: negative=up, positive=down. Constrain each attempt to
    the rod length range and require a cursor ON the new ray and BETWEEN origin
    and tip. When the requested step would cross a boundary, travel only to the
    last feasible location rather than jumping or desynchronizing the cursor.
    """
    if not vertical_pixels:
        return None

    def try_fraction(fraction):
        tip = (float(old_tip[0]), float(old_tip[1]) + vertical_pixels * fraction)
        dx, dy = tip[0] - origin[0], tip[1] - origin[1]
        length = math.hypot(dx, dy)
        if not (min_length - 1e-8 <= length <= max_length + 1e-8):
            return None
        direction = (dx / length, dy / length)
        cursor = _cursor_on_ray(origin, direction, length,
                                old_cursor, blue_rect, forbidden_rect, margin)
        if cursor is None:
            return None
        return SmartRodResult(length, direction, tip, cursor)

    complete = try_fraction(1.0)
    if complete is not None:
        return complete
    # At least the current geometry must be feasible (the physical pointer is
    # inside the blue area); a partially feasible step is enough at the edge.
    if try_fraction(0.0) is None:
        return None
    lower, upper = 0.0, 1.0
    result = None
    for _ in range(28):
        middle = (lower + upper) / 2
        candidate = try_fraction(middle)
        if candidate is None:
            upper = middle
        else:
            lower = middle
            result = candidate
    if result is None or abs(vertical_pixels) * lower < 0.25:
        return None
    return result
