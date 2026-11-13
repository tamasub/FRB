"""Shared, non-activating mouse-wheel navigation for history popups.

Wheel selection never clicks the item or deletes an entry. The pointer can
follow a selected row so the user's next ordinary click activates it.
"""


def history_target_index(current, count, steps):
    """Move down for positive steps, up for negative; clamp at either end."""
    if count <= 0:
        return -1
    if current is None or current < 0 or current >= count:
        return 0 if steps >= 0 else count - 1
    return max(0, min(count - 1, current + steps))


def warp_to_history_row(tree, item, original_cursor, cursor_class):
    """Warp into the selected row only if the mouse still hasn't moved.

    Imported Qt primitives are local: pure step-selection logic stays reusable
    and testable outside a Qt/Windows session.
    """
    if (item is None or not tree.isVisible() or
            tree.currentItem() is not item or cursor_class.pos() != original_cursor):
        return False
    from PySide6.QtCore import QPoint
    viewport = tree.viewport()
    row = tree.visualItemRect(item)
    if row.isEmpty() or viewport.width() < 1:
        return False
    y = max(0, min(viewport.height() - 1, row.center().y()))
    if y < 0 or row.bottom() < 0 or row.top() >= viewport.height():
        return False
    # Never land on the rightmost × (delete) column.
    safe_right = max(0, viewport.width() - 48)
    current_x = viewport.mapFromGlobal(original_cursor).x()
    x = max(8, min(current_x, safe_right))
    destination = viewport.mapToGlobal(QPoint(x, y))
    if destination != original_cursor:
        cursor_class.setPos(destination)
    return True
