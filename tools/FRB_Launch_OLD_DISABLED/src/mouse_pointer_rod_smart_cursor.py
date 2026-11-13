"""Small, independently testable Qt cursor-warp adapter for Smart Rod.

Do not use this in the original rod mode.  The caller validates that the
new point is in the blue control pad, not over the central wheel button.
"""


def move_smart_cursor(cursor, point):
    """Move cursor; report success rather than assuming Windows accepted it."""
    original = cursor.pos()
    try:
        cursor.setPos(point)
    except Exception:
        return False
    if (cursor.pos() - point).manhattanLength() > 1:
        try:
            cursor.setPos(original)
        except Exception:
            pass
        return False
    return True
