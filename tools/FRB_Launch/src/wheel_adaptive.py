"""Qt-independent wheel edge navigation helpers for the Files middle column.

The widget first performs its normal wheel scroll.  Only when the actual
vertical scrollbar value stays unchanged at the relevant edge do we navigate
by selected row and move the pointer.  This preserves native scrolling.
"""


def wheel_steps(pending, angle_delta, pixel_delta=0):
    """Accumulate high-resolution wheel input; down is positive row movement.

    Return (remaining signed delta, signed number of whole row steps).
    """
    delta = angle_delta if angle_delta else pixel_delta * 3
    if not delta:
        return pending, 0
    pending += delta
    steps = int(abs(pending) // 120)
    if not steps:
        return pending, 0
    sign = 1 if pending > 0 else -1
    pending -= sign * steps * 120
    return pending, -sign * steps


def can_follow_at_edge(scroll_before, scroll_after, scroll_min, scroll_max,
                       row_direction):
    """True only when native scroll really did not move at the input edge.

    A zero movement in the middle of the scroll range (e.g. a precision wheel
    substep) must *not* unexpectedly warp the pointer.
    """
    if not row_direction or scroll_after != scroll_before:
        return False
    if row_direction > 0:
        return scroll_after >= scroll_max
    return scroll_after <= scroll_min
