"""Selection contract for editing authored FRB Launch cascade entries.

Generated filesystem/bookmark/application rows are not persisted Studio items.
A context menu should never invent a Studio editing target for them.
"""


def authored_cascade_row(row, authored_items):
    """Return the canonical editable row, or None for a generated/utility row."""
    if not isinstance(row, dict):
        return None
    item_id = row.get('item_id')
    if not isinstance(item_id, str) or not item_id:
        return None
    # The actual source of truth is the DataJSON, not a virtual menu row.
    for item in authored_items:
        if isinstance(item, dict) and item.get('item_id') == item_id:
            return item
    return None
