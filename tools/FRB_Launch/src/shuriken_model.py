"""Pure, JSON-authored FRB Remote shuriken menu contract.

A hand index identifies a BUTTON, not a radial sector. One button may have
up to ten entries. Two actions use the up/down guide; three actions use three 120-degree
sectors; four actions use cardinal up/right/down/left sectors separated by
45-degree diagonal boundaries. Captions are not hit targets.
"""
import math
from dataclasses import dataclass

DIRECTION_ANGLES = {
    'center': None,
    'right': 0, 'down_right': 45, 'down': 90, 'down_left': 135,
    'left': 180, 'up_left': -135, 'up': -90, 'up_right': -45,
}
MAX_ITEMS_PER_HAND = 10

# FRB three-action 120° circle, in Qt screen coordinates (y grows DOWN).
# Each tuple contains (gesture angle, caption anchor x/y, text alignment),
# measured relative to the fixed-radius preview circle.
# Move the captions outward without growing the circle or moving hit targets.
THREE_SECTOR_LAYOUT = {
    # Compass angle, caption anchor X/Y, alignment. Keep captions clear of
    # the central current ring and selected-direction indicator.
    'up_left': (-150.0, -66.0, -22.0, 'right'),
    'up_right': (-30.0, 66.0, -22.0, 'left'),
    'down': (90.0, 0.0, 70.0, 'center'),
}
THREE_SECTOR_DIVIDERS = (-90.0, 30.0, 150.0)


# Four cardinal flick targets. A +45° rotation of the former diagonal
# target positions preserves the circular order of the four JSON actions:
# up_left -> up, up_right -> right, down_right -> down, down_left -> left.
# The divider lines bisect the gaps at 45/135/225/315 degrees (an X).
FOUR_SECTOR_LAYOUT = {
    'up': (-90.0, 0.0, -70.0, 'center'),
    'right': (0.0, 62.0, 0.0, 'left'),
    'down': (90.0, 0.0, 70.0, 'center'),
    'left': (180.0, -62.0, 0.0, 'right'),
}


def uses_three_sector_guide(entries):
    """True exactly when the buttons' three entries match the 3-way sketch."""
    return (len(entries) == 3
            and {row.direction for row in entries} == set(THREE_SECTOR_LAYOUT))


def uses_four_sector_guide(entries):
    """True exactly when the buttons' four entries match the 4-way sketch."""
    return (len(entries) == 4
            and {row.direction for row in entries} == set(FOUR_SECTOR_LAYOUT))


def three_sector_slot(entry, radius=72.0, marker_distance=42.0):
    """Return (label_x, label_y, marker_x, marker_y, align) for 120° sector."""
    angle, label_x, label_y, align = THREE_SECTOR_LAYOUT[entry.direction]
    radians = math.radians(angle)
    return (label_x, label_y, marker_distance * math.cos(radians),
            marker_distance * math.sin(radians), align)


def four_sector_slot(entry, radius=72.0, marker_distance=42.0):
    """Return (label_anchor_x, label_y, marker_x, marker_y, align)."""
    angle, anchor_x, label_y, align = FOUR_SECTOR_LAYOUT[entry.direction]
    radians = math.radians(angle)
    return (anchor_x, label_y, marker_distance * math.cos(radians),
            marker_distance * math.sin(radians), align)


def current_indicator_position(entries, selected_id='', marker_distance=42.0):
    """Pure current indicator position for a two-to-four action round guide.

    No selection (or an ambiguous/outside drag) means the white center ring's
    origin. Choosing an entry moves the dot to the same sector the renderer
    and release hit-test use. Return None for unsupported guide sizes.
    """
    if not 2 <= len(entries) <= 4:
        return None
    selected = next((row for row in entries if row.item_id == selected_id), None)
    if selected is None:
        return (0.0, 0.0)
    if uses_three_sector_guide(entries):
        return three_sector_slot(selected, marker_distance=marker_distance)[2:4]
    if uses_four_sector_guide(entries):
        return four_sector_slot(selected, marker_distance=marker_distance)[2:4]
    index = entries.index(selected)
    if len(entries) == 2:
        # The up/down guide must not reverse when users reorder the JSON rows.
        if {row.direction for row in entries} == {'up', 'down'}:
            return (0.0, -marker_distance if selected.direction == 'up' else marker_distance)
        return (0.0, -marker_distance if index == 0 else marker_distance)
    # For nonstandard 3/4 menus, retain the existing horizontal row guide.
    return (0.0, -72.0 + (index + 0.5) * (144.0 / len(entries)))


@dataclass(frozen=True)
class ShurikenEntry:
    item_id: str
    title: str
    hand_index: int
    direction: str
    order: int
    context_action_id: str = ''


def configured_entries(data, hand_index=1):
    """Read existing Launch *items*; no second action registry or copied BATs."""
    try:
        hand_index = int(hand_index)
    except (ValueError, TypeError):
        return []
    if not isinstance(data, dict):
        return []
    entries = []
    for row in data.get('items', []):
        if not isinstance(row, dict) or not row.get('shuriken_enabled', False) or not row.get('enabled', True):
            continue
        try:
            button = int(row.get('shuriken_button_index', 0))
            order = int(row.get('shuriken_order', 100))
        except (ValueError, TypeError):
            continue
        direction = str(row.get('shuriken_direction', '')).strip().lower()
        if button != hand_index or direction not in DIRECTION_ANGLES:
            continue
        item_id = str(row.get('item_id', '')).strip()
        if not item_id:
            continue
        entries.append(ShurikenEntry(item_id, str(row.get('title') or item_id), button,
                                      direction, order, str(row.get('shuriken_context_action_id') or '')))
    entries.sort(key=lambda row: (row.order, row.item_id))
    # Never silently execute a hidden eleventh action.
    return entries[:MAX_ITEMS_PER_HAND]


def direction_of(dx, dy, deadzone=14):
    """Return pointer sector in GUI coordinates, or '' before deliberate drag."""
    if math.hypot(dx, dy) < deadzone:
        return ''
    angle = math.degrees(math.atan2(dy, dx))
    octant = int(math.floor((angle + 22.5) / 45.0)) % 8
    order = ('right', 'down_right', 'down', 'down_left',
             'left', 'up_left', 'up', 'up_right')
    return order[octant]


def sector_entries(entries, direction):
    return [row for row in entries if row.direction == direction]


def spoke_angles(entries, direction):
    """Compatibility helper for multiple actions sharing one gesture sector.

    Actual hit testing is performed by choose_entry across the entire hand,
    and actual label geometry is a fixed-size semicircle, not these angles.
    """
    if direction not in DIRECTION_ANGLES or not entries:
        return []
    if direction == 'center':
        return [0.0 for _ in entries]
    base = float(DIRECTION_ANGLES[direction])
    count = len(entries)
    if count == 1:
        return [base]
    if count == 2:
        return [base, base + 18.0]
    # General 3..10 case: technically representable; 4 or fewer are the
    # experimental usability goal. Do not pretend ten blind targets are easy.
    span = 40.0
    return [base - span / 2.0 + span * i / (count - 1) for i in range(count)]


def _gesture_angles(entries):
    """Stable compass gesture slots; repeated directions share a narrow arc."""
    from collections import defaultdict
    grouped = defaultdict(list)
    for index, entry in enumerate(entries):
        grouped[entry.direction].append(index)
    targets = [None] * len(entries)
    for direction, indices in grouped.items():
        base = DIRECTION_ANGLES[direction]
        n = len(indices)
        if direction == 'center':
            offsets = [0.0] * n
        elif n == 1:
            offsets = [0.0]
        elif n == 2:
            # Straight flick gets the first menu, not a boundary tie.
            offsets = [0.0, 18.0]
        else:
            offsets = [-20.0 + (40.0 * i / (n - 1)) for i in range(n)]
        for index, offset in zip(indices, offsets):
            targets[index] = (None if base is None else base + offset)
    return targets


def choose_entry(entries, dx, dy, min_release_distance=27):
    """Blind 'シュッ' uses a compass gesture, NOT whether the popup painted.

    Unlike the center key of a kana pad, clicking without a deliberate flick
    NEVER launches an action. Three sectors map to left-up/right-up/down.
    Four sectors map to the kana-flick cardinal up/right/down/left wedges,
    with 45-degree diagonal divider boundaries.
    """
    if not entries or math.hypot(dx, dy) < min_release_distance:
        return None
    pointer = math.degrees(math.atan2(dy, dx))
    if uses_three_sector_guide(entries):
        candidates = sorted((abs((pointer - THREE_SECTOR_LAYOUT[e.direction][0]
                                  + 180.0) % 360.0 - 180.0), index)
                            for index, e in enumerate(entries))
        nearest, index = candidates[0]
        if len(candidates) > 1 and candidates[1][0] - nearest < 2.0:
            return None
        return entries[index]
    if uses_four_sector_guide(entries):
        candidates = sorted((abs((pointer - FOUR_SECTOR_LAYOUT[e.direction][0]
                                  + 180.0) % 360.0 - 180.0), index)
                            for index, e in enumerate(entries))
        nearest, index = candidates[0]
        if len(candidates) > 1 and candidates[1][0] - nearest < 2.0:
            return None
        return entries[index]
    targets = _gesture_angles(entries)
    candidates = sorted((abs((pointer - angle + 180.0) % 360.0 - 180.0), index)
                        for index, angle in enumerate(targets) if angle is not None)
    if not candidates:
        return None
    nearest_delta, index = candidates[0]
    if nearest_delta > 48.0:
        return None
    if len(candidates) > 1 and (candidates[1][0] - nearest_delta) < 0.25:
        return None
    return entries[index]
