"""Path-based Files column handoff for Left-arrow navigation (no Qt/history).

The first column is a set of *current* folder shortcuts, not a record of how
we arrived at the directory.  Use Windows path identity, then virtual row IDs.
"""
import ntpath

from directory_address import row_directory


def matching_first_row(current, first_rows, expand=lambda value: value):
    """Index of the first-column row representing the displayed folder.

    Physical folder comparisons ignore Windows case, separators, and trailing
    separators. Virtual folder/category rows fall back to their stable item ID.
    """
    if not current:
        return None
    current_path = row_directory(current, expand)
    current_id = current.get('item_id')
    for i, row in enumerate(first_rows):
        if not row or row.get('item_kind') not in ('directory', 'category'):
            continue
        row_path = row_directory(row, expand)
        if current_path and row_path:
            if ntpath.normcase(ntpath.normpath(current_path)) == ntpath.normcase(ntpath.normpath(row_path)):
                return i
        elif not current_path and current_id is not None and current_id == row.get('item_id'):
            return i
    return None


def has_first_row_ancestor(current_path, first_rows, expand=lambda value: value):
    """Is the current directory below ANY first-column physical shortcut?

    This allows a direct address/favorite navigation to unwind toward a root,
    without retaining a history of which shortcut was visited previously.
    """
    if not current_path:
        return False
    current_key = ntpath.normcase(ntpath.normpath(current_path))
    for row in first_rows:
        root = row_directory(row, expand)
        if not root:
            continue
        root_key = ntpath.normcase(ntpath.normpath(root))
        if current_key.startswith(root_key.rstrip('\\') + '\\'):
            return True
    return False
