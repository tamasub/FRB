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


def expanded_bookmark_rows(parent, children_of):
    """Group only *top-level* browser folders in Three-layer's third pane.

    Decide whether headings are necessary BEFORE applying the existing
    singleton-folder shortcut.  Previously the shortcut descended past a
    lone top-level folder and then grouped its nested folders as headings,
    unintentionally turning real Chrome/Edge folders into non-actionable text.

    One top-level folder: retain the existing direct-child display shortcut.
    Two or more top-level folders: their contents receive separate headings.
    All descendants, browser profiles and original data remain untouched.
    """
    rows = visible_bookmark_children(parent, children_of)
    if not (parent.get('launch_source') == 'browser_bookmarks'
            or parent.get('_browser_bookmark')):
        return rows

    top_level = children_of(parent)
    top_folders = [row for row in top_level
                   if (row.get('_browser_bookmark')
                       and row.get('item_kind') == 'category')]
    if len(top_folders) < 2:
        return rows

    expanded = []
    for row in top_level:
        if row not in top_folders or not children_of(row):
            # Preserve URLs and empty/manually-defined folders.
            expanded.append(row)
            continue
        expanded.append({'title': row.get('title', ''),
                         '_bookmark_group_header': True})
        expanded.extend(visible_bookmark_children(row, children_of))
    return expanded
