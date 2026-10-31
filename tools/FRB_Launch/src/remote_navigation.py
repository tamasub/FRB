"""Pure, side-effect-free rules for the optional FRB Launch Remote.

No keyboard injection, OS APIs or Qt dependency.  The remote sends semantic
commands; Launcher owns and executes the actual navigation state changes.
"""

# Two workspaces are explicit focus stops, regardless of which is selected.
# URL tab BUTTONS are never focus stops: each open page is one stop instead.
EXPANDED_AREAS = ('search', 'pages', 'workspace_files', 'workspace_browser',
                  'files', 'directory', 'breadcrumb', 'roots')
WEB_AREAS = ('search', 'pages', 'workspace_files', 'workspace_browser',
             'bookmarks', 'web_body:0')
CLASSIC_AREAS = ('search', 'pages', 'list')


def navigation_order(*, expanded=True, web=False, web_tab_count=1, bookmarks_visible=True):
    if not expanded:
        return CLASSIC_AREAS
    if web:
        bodies = tuple(f'web_body:{i}' for i in range(max(0, web_tab_count)))
        return ('search', 'pages', 'workspace_files', 'workspace_browser') + (
            ('bookmarks',) if bookmarks_visible else ()) + bodies
    return EXPANDED_AREAS


def normalize_area(area, order, *, current_tab=0):
    # Old v41 'web_tabs'/'web_body' labels may persist in last-current data.
    if area in ('web_body', 'web_tabs'):
        target = f'web_body:{max(0, current_tab)}'
        return target if target in order else ('bookmarks' if 'bookmarks' in order else order[0])
    return area


def next_area(area, *, expanded=True, web=False, web_tab_count=1, current_tab=0, bookmarks_visible=True):
    order = navigation_order(expanded=expanded, web=web, web_tab_count=web_tab_count,
                             bookmarks_visible=bookmarks_visible)
    area = normalize_area(area, order, current_tab=current_tab)
    return order[(order.index(area) + 1) % len(order)] if area in order else order[0]


def previous_area(area, *, expanded=True, web=False, web_tab_count=1, current_tab=0, bookmarks_visible=True):
    """Shift+Tab uses the same dynamic ring in reverse order."""
    order = navigation_order(expanded=expanded, web=web, web_tab_count=web_tab_count,
                             bookmarks_visible=bookmarks_visible)
    area = normalize_area(area, order, current_tab=current_tab)
    return order[(order.index(area) - 1) % len(order)] if area in order else order[-1]


def starting_area(previous, *, expanded=True, web=False, web_tab_count=1, current_tab=0, bookmarks_visible=True):
    order = navigation_order(expanded=expanded, web=web, web_tab_count=web_tab_count,
                             bookmarks_visible=bookmarks_visible)
    previous = normalize_area(previous, order, current_tab=current_tab)
    if previous in order and previous != 'search':
        return previous
    return (('bookmarks' if bookmarks_visible else
             (f'web_body:0' if web_tab_count else 'workspace_browser'))
            if expanded and web else ('directory' if expanded else 'list'))


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
