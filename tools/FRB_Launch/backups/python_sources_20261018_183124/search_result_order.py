"""Deterministic sorting by the two *visible* FRB Launch search columns.

Does not depend on Qt's sortingEnabled flag or internal row metadata.
"""


def display_columns(row, hierarchy='', *, selection=False):
    details = row.get('description', '') or (
        str(row.get('value', '')) if selection or row.get('_search_selection_owner') else ''
    )
    if row.get('_browser_bookmark'):
        details = ''  # Bookmark URL is available only via tooltip.
    description = details + ('  ·  ' + hierarchy if hierarchy else '')
    folder = row.get('item_kind') in {'category', 'directory'}
    return row['title'] + ('  ›' if folder else ''), description


def sort_search_pairs(pairs, column, descending=False, *, selection=False):
    """Return ordered row/hierarchy pairs without mutating input (sort is stable)."""
    if column not in (0, 1):
        return list(pairs)
    return sorted(pairs, key=lambda pair: display_columns(
        pair[0], pair[1], selection=selection)[column].casefold(),
        reverse=descending)
