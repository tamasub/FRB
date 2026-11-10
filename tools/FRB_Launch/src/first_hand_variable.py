"""Common first-hand menu direction/selection rules for 1–4 actions.

Membership and priority come from JSON, but positions belong to Launch.
The selector is a pure function; confirmation and execution are separate.
"""
import math

POSITIONS = {
    1: ('up',),
    2: ('left', 'right'),
    3: ('up_left', 'up_right', 'down'),
    4: ('up', 'right', 'down', 'left'),
}
# On-screen Qt coordinates: +y is DOWN.
ANGLES = {
    3: (-150.0, -30.0, 90.0),
    4: (-90.0, 0.0, 90.0, 180.0),
}


def directions_for_count(count):
    if count not in POSITIONS:
        raise ValueError('first hand menu supports 1..4 items')
    return POSITIONS[count]


def choose_variable_entry(entries, dx, dy, distance=14):
    """Match 1..4 pointer regions. Selection is never execution."""
    count = len(entries)
    if count not in POSITIONS or math.hypot(dx, dy) < distance:
        return None
    if count == 1:
        # The only target is at the top. The bottom is never a target.
        return entries[0] if dy < 0 and -dy > abs(dx) else None
    if count == 2:
        # Two full horizontal sectors (vertical motion cancels).
        if abs(dx) < distance or abs(dx) <= abs(dy) + 3.0:
            return None
        return entries[0] if dx < 0 else entries[1]
    # Exactly three sectors, center angles: upper left, upper right, bottom.
    pointer = math.degrees(math.atan2(dy, dx))
    def delta(angle):
        return abs((pointer - angle + 180.0) % 360.0 - 180.0)
    candidates = sorted((delta(angle), index) for index, angle in enumerate(ANGLES[count]))
    nearest, index = candidates[0]
    # A short diagonal into an exact boundary is ambiguous and cancels.
    if len(candidates) > 1 and candidates[1][0] - nearest < 2.0:
        return None
    return entries[index]
