"""Content-sized in-window popup geometry shared by search and breadcrumb history.

No Qt import is needed here.  The view passes its rendered row size hints,
so Windows DPI/font changes are respected without resizing the window itself.
"""


def popup_available_height(window_height, popup_top, footer_top=None):
    """Keep the popup above the footer, even after a launcher resize."""
    bottom = max(0, int(window_height) - 12)
    if footer_top is not None and int(footer_top) > popup_top:
        bottom = min(bottom, int(footer_top) - 4)
    return max(1, bottom - int(popup_top))


def popup_tree_height(tree, rows, minimum_row_height, chrome_height, available_height):
    """Grow to the last displayed item, then scroll only when space runs out.

    `rows` contains only EXPANDED tree children. `sizeHintForIndex` picks up
    per-row Qt/font metrics, while the minimum covers stylesheet row padding.
    """
    content_height = 0
    for row in rows:
        size = tree.sizeHintForIndex(tree.indexFromItem(row))
        content_height += max(int(minimum_row_height), size.height())
    desired = int(chrome_height) + content_height
    return max(1, min(desired, int(available_height)))
