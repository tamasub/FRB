"""Last-current contract for the main launcher; independent of Qt widgets.

Transient QMenu columns are intentionally represented by their opener: a
new summon starts with no open popup but with the same keyboard anchor.
"""

AREAS = frozenset(('search', 'pages', 'roots', 'breadcrumb', 'files', 'directory',
                   'sort', 'bookmarks', 'list'))
PANEL_AREAS = frozenset(('files', 'directory', 'bookmarks'))


def normalize_focus_state(value):
    if not isinstance(value, dict):
        return {'area': 'search'}
    area = value.get('area')
    if area not in AREAS:
        area = 'search'
    result = {'area': area}
    for name in ('page_id', 'item_id', 'left_id', 'middle_id', 'bookmarks_id'):
        if isinstance(value.get(name), str) and len(value[name]) <= 4096:
            result[name] = value[name]
    # Absolute filesystem location is independent of the Files shortcut root.
    # Do not persist or restore a partial / relative address.
    from directory_address import normalized_directory
    middle_path = normalized_directory(value.get('middle_path'))
    if middle_path and len(middle_path) <= 4096:
        result['middle_path'] = middle_path
    if value.get('mode') in ('classic', 'expanded'):
        result['mode'] = value['mode']
    path = value.get('path_ids')
    if isinstance(path, list):
        result['path_ids'] = [v for v in path[:64]
                              if isinstance(v, str) and len(v) <= 4096]
    return result


def focus_area_for_reopen(area, *, expanded, selection=False):
    """Never restore focus to an invisible widget or stale choice list."""
    if expanded:
        if selection:
            return 'roots'
        return area if area in ('search', 'pages', 'roots', 'files',
                                'directory', 'bookmarks') else 'search'
    return area if area in ('search', 'pages', 'list') else 'search'


def resolve_path_ids(parent, ids, get_children):
    """Resolve paths through fresh data; stop safely at the first missing ID."""
    resolved = []
    for item_id in ids:
        try:
            row = next((r for r in get_children(parent)
                        if r.get('item_id') == item_id and
                        r.get('item_kind') in ('category', 'directory')), None)
        except (OSError, ValueError, PermissionError):
            break
        if row is None:
            break
        resolved.append(row)
        parent = row
    return resolved
