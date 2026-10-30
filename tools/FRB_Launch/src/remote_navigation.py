"""Pure, side-effect-free rules for the optional FRB Launch Remote.

No keyboard injection, OS APIs or Qt dependency.  The remote sends semantic
commands; Launcher owns and executes the actual navigation state changes.
"""

EXPANDED_AREAS = ('search', 'pages', 'roots', 'breadcrumb', 'files', 'directory', 'sort', 'bookmarks')
WEB_AREAS = ('search', 'pages', 'roots', 'web_tabs', 'web_body', 'bookmarks')
CLASSIC_AREAS = ('search', 'pages', 'list')


def next_area(area, *, expanded=True, web=False):
    order = WEB_AREAS if expanded and web else (EXPANDED_AREAS if expanded else CLASSIC_AREAS)
    return order[(order.index(area) + 1) % len(order)] if area in order else order[0]


def previous_area(area, *, expanded=True, web=False):
    """Shift+Tab order (stable, independent of Qt keyboard focus)."""
    order = WEB_AREAS if expanded and web else (EXPANDED_AREAS if expanded else CLASSIC_AREAS)
    return order[(order.index(area) - 1) % len(order)] if area in order else order[-1]


def starting_area(previous, *, expanded=True, web=False):
    order = WEB_AREAS if expanded and web else (EXPANDED_AREAS if expanded else CLASSIC_AREAS)
    # Opening a remote is primarily for browsing, not for typing.
    return previous if previous in order and previous != 'search' else (
        'web_body' if expanded and web else ('directory' if expanded else 'list'))


def popup_position(x, y, width, height, left, top, right, bottom, offset=14):
    """Top-left of a popup near the pointer, bounded by the active screen."""
    width, height = max(0, width), max(0, height)
    target_x, target_y = x + offset, y + offset
    if target_x + width > right:
        target_x = x - offset - width
    if target_y + height > bottom:
        target_y = y - offset - height
    return (max(left, min(target_x, max(left, right - width))),
            max(top, min(target_y, max(top, bottom - height))))


def popup_at_hotspot(x, y, width, height, left, top, right, bottom, hot_x, hot_y):
    """Put a remote's wheel pad under the mouse whenever screen room permits."""
    return (max(left, min(x - hot_x, max(left, right - width))),
            max(top, min(y - hot_y, max(top, bottom - height))))
