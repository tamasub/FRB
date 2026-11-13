"""Restore a usable current row after an Explorer column-2 selection is lost.

Qt-free on purpose: the selection policy can be regression-tested without a
Windows desktop. Never clears an existing multi-selection or activates a file.
"""


def row_key(row):
    if not isinstance(row, dict):
        return None
    return str(row.get('item_id') or row.get('path') or row.get('title') or '') or None


def repair_middle_selection(tree, row_data, remembered_key=None):
    """Return (usable current item, recovered).

    Prefer the existing current row, then a selected row, then the last row
    in the same folder, finally the first actionable row. If there is no
    actionable row, do nothing. Preserve extended selection rather than
    clearing it or silently adding a new item to a bulk operation.
    """
    # The watchdog calls us while the app is idle; avoid enumerating a large
    # folder on every tick when a healthy selected current already exists.
    current = tree.currentItem()
    if current is not None and row_data(current) is not None and current.isSelected():
        return current, False

    items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    items = [item for item in items if item is not None and row_data(item) is not None]
    if not items:
        return None, False

    selected = [item for item in tree.selectedItems() if item in items]
    if current in items:
        # ExtendedSelection allows Ctrl+Arrow to move the current cursor
        # without selecting it. Never undo that deliberate keyboard state.
        target = current
    elif selected:
        target = selected[0]
    else:
        target = next((item for item in items
                       if row_key(row_data(item)) == remembered_key), None)
        if target is None:
            target = items[0]

    changed = current is not target
    if changed:
        tree.setCurrentItem(target)
    # setCurrentItem() usually selects; an explicit fallback covers Qt's
    # extended-selection state after a model rebuild or focus loss.
    if not selected and not target.isSelected():
        target.setSelected(True)
        changed = True
    if changed:
        tree.scrollToItem(target)
        tree.viewport().update()
    return target, changed
