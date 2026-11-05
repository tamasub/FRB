"""Small, platform-independent flick-scroll mapping for FRB Remote.

Qt widgets call these functions, but they do not depend on Qt, focus or
keyboard events. A gesture is a vertical pointer delta from its press point.
"""

DEADZONE_PX = 12
MAX_DRAG_PX = 90
TICK_MS = 40


def pixels_per_tick(dy):
    """40-ms real-time scroll: upward hand drag scrolls content upward.

    The fixed scroll target moves, not the selection/cursor. Return a signed
    scrollbar delta; positive means content moves up (scrollbar advances).
    """
    try:
        dy = float(dy)
    except (TypeError, ValueError):
        return 0
    if abs(dy) < DEADZONE_PX:
        return 0
    distance = min(MAX_DRAG_PX, abs(dy)) - DEADZONE_PX
    amount = round(6 + 0.55 * distance)
    return amount if dy < 0 else -amount


def release_impulse(dy, ticks_emitted):
    """Very fast flick (<40 ms) must still scroll at least once on release.

    Do not generate an extra fling after real-time ticks have already run;
    release should immediately stop the gesture, not start inertia.
    """
    if ticks_emitted or abs(dy) < DEADZONE_PX:
        return 0
    amount = min(460, max(35, round(abs(dy) * 3)))
    return amount if dy < 0 else -amount
