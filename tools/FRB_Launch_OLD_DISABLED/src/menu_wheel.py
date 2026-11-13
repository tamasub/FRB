"""Wheel-to-selection helpers shared by the classic menu and cascade columns.

Qt's normal scrolling is intentionally preserved in large application catalogs
and the modern file/bookmark panes.  Only explicit menu-navigation surfaces use
these helpers.
"""

WHEEL_UNIT = 120


def wheel_motion(angle_y, pixel_y, remainder=0):
    """Return signed wheel notches and remaining high-resolution motion.

    Positive notches mean upwards (previous menu row).  Qt provides angleDelta
    for typical wheels; precision devices may report only pixelDelta instead.
    Keep the fractional remainder so several small gestures move one row.
    """
    delta = angle_y if angle_y else pixel_y * 3
    total = remainder + delta
    steps = int(total / WHEEL_UNIT)  # Truncation toward zero, also for negatives.
    return steps, total - steps * WHEEL_UNIT


def wheel_neighbor(items, current, steps):
    """Select a row without wrapping or activating its command.

    ``steps`` is positive for the next row, negative for the previous row.
    Long lists can scroll the *viewport* to the selection separately.
    """
    if not items or steps == 0:
        return current if current in items else None
    try:
        index = items.index(current)
    except ValueError:
        index = -1 if steps > 0 else len(items)
    return items[max(0, min(len(items) - 1, index + steps))]
