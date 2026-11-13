"""Flatten bookmarked URL leaves for a no-popup horizontal bookmark strip.

Folder definitions remain untouched.  This only creates display descriptors,
retaining the original URL row as the action target.  Cycles and very large
imported browser catalogs are bounded for a responsive UI.
"""


def flatten_bookmark_rows(roots, children_of, *, limit=1200, max_depth=20):
    """Return ``(row, folder_path)`` pairs in authored depth-first order."""
    result = []
    if not callable(children_of):
        return result
    pending = [(row, (), frozenset(), 0) for row in reversed(list(roots or []))]
    while pending and len(result) < limit:
        row, parents, ancestors, depth = pending.pop()
        if not isinstance(row, dict) or row.get('_bookmark_group_header'):
            continue
        title = str(row.get('title') or '').strip()
        if not title:
            continue
        identity = row.get('item_id')
        identity = str(identity) if identity is not None else str(id(row))
        if identity in ancestors:
            continue
        if row.get('item_kind') in ('category', 'directory'):
            if depth >= max_depth:
                continue
            try:
                children = children_of(row) or []
            except (KeyError, ValueError, TypeError, OSError):
                children = []
            seen = ancestors | {identity}
            pending.extend((child, parents + (title,), seen, depth + 1)
                           for child in reversed(children))
        else:
            result.append((row, parents))
    return result
