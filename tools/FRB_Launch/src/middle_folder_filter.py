"""Folder-pane filter and sort, reusing Launch's global Boolean search grammar.

No Qt dependencies: the current directory's already resolved rows remain the
source of truth. This is a visible-list filter, not a recursive disk index.
"""
from datetime import datetime
from pathlib import Path

from search_matching import matches_search_text

SORT_LABELS = {
    'name': '名前順',
    'name_desc': '名前降順',
    'type_asc': '種類昇順',
    'type_desc': '種類降順',
    'date_desc': '更新日降順',
    'date_asc': '更新日昇順',
    'size_desc': 'サイズ大きい順',
    'size_asc': 'サイズ小さい順',
}


def format_size(count):
    """Files detail column: integer KiB, displayed as KB like Explorer.

    Round nonempty partial kilobytes upward so a tiny file does not look
    empty; 0-byte files explicitly show 0 KB. Sort still uses raw bytes.
    """
    if count is None:
        return ''
    count = max(0, int(count))
    return f'{(count + 1023) // 1024:,} KB'


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


def file_type_fallback(row):
    """Stable fallback when Windows' registered type label is unavailable.

    Real Windows labels are supplied by QFileIconProvider.type() in the view.
    Qt-free output is useful to keep filtering/sorting testable headlessly.
    """
    if row.get('item_kind') in ('category', 'directory'):
        return 'ファイル フォルダー'
    suffix = Path(str(row.get('title', ''))).suffix
    return (suffix[1:].upper() + ' ファイル') if suffix else 'ファイル'


def sort_mode_for_header(column, previous='name'):
    """Return toggle mode for a clicked LOGICAL column (reorder-safe)."""
    modes = {
        0: ('name', 'name_desc'),
        1: ('date_desc', 'date_asc'),
        2: ('size_desc', 'size_asc'),
        3: ('type_asc', 'type_desc'),
    }
    pair = modes.get(column)
    if pair is None:  # The flexible blank/spacer column never sorts.
        return None
    return pair[1] if previous == pair[0] else pair[0]


def filter_sort_folder_rows(rows, query='', mode='name'):
    """Search one directory, populate all visible metadata and sort safely.

    Folders stay above files. Dates, sizes and types are present in *every*
    sorting mode, so changing sort never changes column contents or widths.
    The input rows are not mutated, and missing metadata sorts last.
    """
    mode = mode if mode in SORT_LABELS else 'name'
    result = []
    for original in rows:
        name = str(original.get('title', ''))
        if query.strip() and not matches_search_text(name, query):
            continue
        row = dict(original)
        is_folder = row.get('item_kind') in ('category', 'directory')
        mtime, size = _physical_metadata(row)
        try:
            date_text = datetime.fromtimestamp(mtime).strftime('%Y/%m/%d %H:%M') if mtime is not None else ''
        except (ValueError, OverflowError, OSError):
            date_text = ''
        row['_middle_date'] = date_text
        row['_middle_size'] = format_size(size) if not is_folder else ''
        row['_middle_type'] = file_type_fallback(row)
        row['_middle_mtime'] = mtime
        row['_middle_size_bytes'] = size
        # Legacy detail keys kept solely for older integrations/tests.
        row['_middle_detail_mode'] = ('date' if mode.startswith('date') else
                                      'size' if mode.startswith('size') else '')
        row['_middle_detail'] = (row['_middle_date'] if mode.startswith('date') else
                                 row['_middle_size'] if mode.startswith('size') else '')
        result.append(row)

    result.sort(key=lambda row: str(row.get('title', '')).casefold(),
                reverse=mode == 'name_desc')
    if mode.startswith('date') or mode.startswith('size'):
        field = '_middle_mtime' if mode.startswith('date') else '_middle_size_bytes'
        result.sort(key=lambda row: row[field] if row[field] is not None else 0,
                    reverse=mode.endswith('desc'))
        result.sort(key=lambda row: row[field] is None)
    elif mode.startswith('type'):
        result.sort(key=lambda row: row['_middle_type'].casefold(),
                    reverse=mode.endswith('desc'))
    result.sort(key=lambda row: row.get('item_kind') not in ('category', 'directory'))
    return result
