"""Pure selection-scoping helper, independent of the Qt list implementation."""


def update_visible_checks(checked_ids, visible_ids, selected):
    """Check or uncheck *only* filtered/visible choices; preserve hidden choices."""
    result = set(checked_ids)
    if selected:
        result.update(visible_ids)
    else:
        result.difference_update(visible_ids)
    return result
