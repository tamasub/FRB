"""Folder-pane filter and sort, reusing Launch's global Boolean search grammar.

No Qt dependencies: the current directory's already resolved rows remain the
source of truth. This is a visible-list filter, not a recursive disk index.
"""
from datetime import datetime
from pathlib import Path

from search_matching import matches_search_text

SORT_LABELS = {
    'name': '名前順',
    'date_desc': '更新日降順',
    'date_asc': '更新日昇順',
    'size_desc': 'サイズ大きい順',
    'size_asc': 'サイズ小さい順',
}


def format_size(count):
    """Human-readable file size, exact byte count for small files."""
    if count is None:
        return ''
    if count < 1024:
        return f'{count} B'
    for unit, divisor in (('KB', 1024), ('MB', 1024**2), ('GB', 1024**3), ('TB', 1024**4)):
        if count < divisor * 1024 or unit == 'TB':
            return f'{count / divisor:.1f} {unit}'
    return f'{count} B'


def _physical_metadata(row):
    # Browse-generated physical file markers, never the authored JSON name.
    path = row.get('_browse_file') or row.get('_file') or row.get('_indexed_file')
    if not isinstance(path, str) or not path:
        return None, None
    try:
        stat = Path(path).stat()
        return stat.st_mtime, (stat.st_size if Path(path).is_file() else None)
    except (OSError, ValueError):
        return None, None


def filter_sort_folder_rows(rows, query='', mode='name'):
    """Return new display rows; do not mutate Launch's backing row dictionaries.

    Display folders before files; within each class use the selected ordering.
    Missing dates/sizes sort last. The existing browser-provided row actions
    and original paths are carried through without modification.
    """
    mode = mode if mode in SORT_LABELS else 'name'
    results = []
    for original in rows:
        name = str(original.get('title', ''))
        if query.strip() and not matches_search_text(name, query):
            continue
        row = dict(original)
        is_folder = row.get('item_kind') in ('category', 'directory')
        mtime, size = _physical_metadata(row) if mode != 'name' else (None, None)
        detail = ''
        if mode.startswith('date') and mtime is not None:
            try:
                detail = datetime.fromtimestamp(mtime).strftime('%Y/%m/%d %H:%M')
            except (ValueError, OverflowError, OSError):
                pass
        elif mode.startswith('size') and not is_folder:
            detail = format_size(size)
        row['_middle_detail'] = detail
        row['_middle_detail_mode'] = ('date' if mode.startswith('date') else
                                      'size' if mode.startswith('size') else '')
        # A missing metadata value goes to the end of the category, irrespective
        # of ascending/descending sort direction.
        if mode.startswith('date'):
            measure = mtime
        elif mode.startswith('size'):
            measure = size
        else:
            measure = None
        results.append((row, is_folder, measure))
    # Stable filename tiebreaker, case-insensitive and independent of filesystem ordering.
    results.sort(key=lambda item: str(item[0].get('title', '')).casefold())
    if mode != 'name':
        reverse = mode.endswith('desc')
        # First sort numeric values; then put missing at end (stable sorts).
        results.sort(key=lambda item: item[2] if item[2] is not None else 0,
                     reverse=reverse)
        results.sort(key=lambda item: item[2] is None)
    results.sort(key=lambda item: not item[1])
    return [row for row, _, _ in results]
