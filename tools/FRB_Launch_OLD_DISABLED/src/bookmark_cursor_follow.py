"""Qt-independent geometry for bookmark wheel-to-cursor following.

Keep this logic independent from Windows and QCursor so geometry boundaries
can be regression tested without a running GUI. All positions are logical px.
"""


def cursor_target(viewport_size, row_rect, cursor_x):
    """Return a safe (x, y) inside the visible portion of a bookmark row.

    viewport_size: (width, height). row_rect: (left, top, width, height).
    Preserve the mouse's horizontal position when possible; moving only
    vertically keeps the wheel under the user's hand and clicking intuitive.
    Return None when the row/viewport is not visible.
    """
    viewport_width, viewport_height = viewport_size
    left, top, width, height = row_rect
    if viewport_width <= 0 or viewport_height <= 0 or width <= 0 or height <= 0:
        return None
    visible_left = max(0, left)
    visible_right = min(viewport_width - 1, left + width - 1)
    visible_top = max(0, top)
    visible_bottom = min(viewport_height - 1, top + height - 1)
    if visible_left > visible_right or visible_top > visible_bottom:
        return None
    margin = min(12, (visible_right - visible_left) // 2)
    x = min(max(cursor_x, visible_left + margin), visible_right - margin)
    return x, (visible_top + visible_bottom) // 2


def is_warp_generated_mouse_move(point, last_warp_point, tolerance=3):
    """Ignore synthetic hover caused by warping a pointer onto the new row."""
    if last_warp_point is None:
        return False
    return (abs(point[0] - last_warp_point[0]) <= tolerance and
            abs(point[1] - last_warp_point[1]) <= tolerance)


def nearest_visible_button(viewport_size, row_rects, pointer_xy):
    """Return (index, safe viewport point) for the nearest *visible* button.

    An offscreen bookmark is never a cursor destination, even if it is the
    first/last item in the imported bookmark list.  Coordinates are viewport
    local; `row_rects` contains (left, top, width, height) or None.
    """
    px, py = pointer_xy
    best = None
    for index, rect in enumerate(row_rects):
        if rect is None:
            continue
        landing = cursor_target(viewport_size, rect, px)
        if landing is None:
            continue
        # Horizontal proximity is the intuitive nearest bookmark in a strip.
        # The vertical distance just breaks ties between equal x distances.
        score = (abs(landing[0] - px), abs(landing[1] - py), index)
        if best is None or score < best[0]:
            best = (score, index, landing)
    return (best[1], best[2]) if best is not None else None
