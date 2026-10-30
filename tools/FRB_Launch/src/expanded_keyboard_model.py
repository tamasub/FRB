"""Pure navigation rules for FRB Launch's expanded (three-layer) view.

Arrow keys express hierarchy; Tab/Shift+Tab express focus-area changes.
Keep these rules separate from Qt controls so they can be contract-tested.
"""

FOCUS_ORDER = ('search', 'pages', 'roots', 'breadcrumb', 'files', 'directory', 'sort', 'bookmarks')
WEB_FOCUS_ORDER = ('search', 'pages', 'roots', 'web_tabs', 'web_body', 'bookmarks')


def tab_target(current, *, backward=False, order=FOCUS_ORDER):
    """Next focus area, wrapping only at the end of the focus ring."""
    if not order:
        return None
    if current not in order:
        return order[-1] if backward else order[0]
    return order[(order.index(current) + (-1 if backward else 1)) % len(order)]


def root_step(index, direction, count):
    """Horizontal root-button traversal with a bounded first/last element."""
    if count <= 0:
        return None
    if index is None or not (0 <= index < count):
        return count - 1 if direction < 0 else 0
    return max(0, min(count - 1, index + direction))


def middle_back_target(depth):
    """Go up the directory stack, or return focus to Files at its root."""
    return 'parent' if depth > 1 else 'files'


def row_right_action(panel, is_folder):
    """Map the Right arrow to navigation, not an accidental Enter action."""
    if panel == 'files':
        return 'enter_directory_panel' if is_folder else 'execute'
    if panel == 'directory':
        return 'descend' if is_folder else 'execute'
    if panel == 'bookmarks':
        return 'cascade' if is_folder else 'execute'
    raise ValueError(f'unknown expanded panel: {panel}')
