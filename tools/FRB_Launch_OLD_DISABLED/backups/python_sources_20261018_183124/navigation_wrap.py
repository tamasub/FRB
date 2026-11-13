"""Shared Up/Down navigation for FRB Launch's selectable lists.

This module deliberately knows nothing about Qt or any particular menu.
"""


def next_wrapped(items, current, direction):
    """Choose the adjacent entry, wrapping at both ends.

    ``items`` must contain *selectable* entries in visual order.  When there
    is no current entry, Down selects the first and Up selects the last.
    Empty lists produce ``None``; a one-item list keeps that item selected.
    """
    if not items:
        return None
    step = 1 if direction > 0 else -1
    try:
        position = items.index(current)
    except ValueError:
        return items[0] if step > 0 else items[-1]
    return items[(position + step) % len(items)]


def next_page_ring_target(items, current, direction, *, on_tab=False):
    """Navigate the *root page* as one ring: Page tab + visible menu rows.

    The current Page tab is a single keyboard stop, not a request to cycle
    through all Page tabs. Left/Right on the tab bar still switches pages.
    Search results and submenus deliberately use ``next_wrapped`` instead.

    Returns ("tab", None) or ("row", row).  With zero rows, stay on the tab.
    """
    if not items:
        return "tab", None
    step = 1 if direction > 0 else -1
    if on_tab:
        return "row", items[0] if step > 0 else items[-1]
    try:
        position = items.index(current)
    except ValueError:
        return "row", items[0] if step > 0 else items[-1]
    if (step > 0 and position == len(items) - 1) or (step < 0 and position == 0):
        return "tab", None
    return "row", items[position + step]


def move_tree_selection(tree, direction, *, usable=None):
    """Apply the same wrap rule to Qt trees, scrolling the destination into view.

    The generic callback permits popup trees to ignore rows whose backing
    QAction is disabled without coupling this helper to QAction or Qt.
    """
    if usable is None:
        usable = lambda item: not item.isHidden() and not item.isDisabled()
    items = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())
             if usable(tree.topLevelItem(i))]
    target = next_wrapped(items, tree.currentItem(), direction)
    if target is not None:
        tree.setCurrentItem(target)
        tree.scrollToItem(target)
    return target
