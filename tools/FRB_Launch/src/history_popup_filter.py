"""In-memory keyword filtering for the search-history popup.

History filtering is deliberately separate from Launcher search: no SQLite,
rendering of result lists, or writes to saved history are performed here.
"""
import unicodedata


def matches_history_filter(value, query):
    """Case/width-insensitive AND for space-separated fragments.

    Keep the caller's actual keyword unchanged for execution/dragging. A
    category-name match may expose every item in that category.
    """
    terms = unicodedata.normalize('NFKC', str(query or '')).casefold().split()
    if not terms:
        return True
    normalized = unicodedata.normalize('NFKC', str(value or '')).casefold()
    return all(term in normalized for term in terms)
