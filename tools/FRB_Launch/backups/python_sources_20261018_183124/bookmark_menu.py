"""Presentation-only shortcut for one-folder bookmark menus.

Browser-owned structure and the transient bookmark items are left unchanged.
Only display navigation omits a folder level when that level has exactly one
visible child and that child is another *browser bookmark folder*.
"""


def visible_bookmark_children(parent, children_of):
    """Return the first useful group of entries under ``parent``.

    Keep a category when it has siblings, when it is empty, or when the only
    entry is a URL.  This function deliberately does not alter IDs/parents,
    which are also used for global search and browser profile routing.
    """
    children = children_of(parent)
    if not (parent.get('launch_source') == 'browser_bookmarks'
            or parent.get('_browser_bookmark')):
        return children

    visited = {parent.get('item_id')}
    while len(children) == 1:
        only = children[0]
        if not (only.get('_browser_bookmark') and only.get('item_kind') == 'category'):
            break
        identity = only.get('item_id')
        if identity in visited:
            break
        next_children = children_of(only)
        if not next_children:  # Do not make an empty folder vanish.
            break
        visited.add(identity)
        children = next_children
    return children
