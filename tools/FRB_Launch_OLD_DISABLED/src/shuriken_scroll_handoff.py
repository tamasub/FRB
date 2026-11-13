"""Qt-independent placement policy for the Files List's post-flight cursor.

A shuriken scroll only moves the *viewport*. When the flight settles, move the
logical current row to the visible region without editing selectedItems().
The caller injects QItemSelectionModel.SelectionFlag.NoUpdate, so the policy
can be tested without a Windows desktop or changing the user's file targets.
"""


def _usable(item, row_data):
    return (item is not None and not item.isHidden() and not item.isDisabled()
            and row_data(item) is not None)


def _edge_item(tree, row_data, backwards=False):
    total = tree.topLevelItemCount()
    positions = range(total - 1, -1, -1) if backwards else range(total)
    for i in positions:
        item = tree.topLevelItem(i)
        if _usable(item, row_data):
            return item
    return None


def _viewport_middle_item(tree, row_data):
    viewport = tree.viewport()
    width, height = viewport.width(), viewport.height()
    if width <= 0 or height <= 0:
        return None
    x = width // 2
    middle = height // 2
    # Prefer the exact center; a row may not intersect this point when a
    # directory is very short or has a large trailing blank area.
    for delta in range(0, height // 2 + 5, 8):
        for y in (middle - delta, middle + delta) if delta else (middle,):
            if 0 <= y < height:
                item = tree.itemAt(x, y)
                if _usable(item, row_data):
                    return item
    return None


def handoff_current_at_scroll_stop(tree, row_data, no_update_flag):
    """Pick a current row at the stopped viewport, without selecting it.

    At top/bottom choose the first/last usable row; in between choose the row
    nearest the viewport's center. No cursor jump and no bulk selection edit.
    Return the row that became current, or None if nothing can be transferred.
    """
    bar = tree.verticalScrollBar()
    if bar is None:
        return None
    if bar.value() <= bar.minimum():
        item = _edge_item(tree, row_data)
    elif bar.value() >= bar.maximum():
        item = _edge_item(tree, row_data, backwards=True)
    else:
        item = _viewport_middle_item(tree, row_data)
    if item is None:
        return None
    if tree.currentItem() is not item:
        tree.setCurrentItem(item, 0, no_update_flag)
    return item
