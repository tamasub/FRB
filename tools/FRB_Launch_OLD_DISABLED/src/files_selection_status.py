"""Explorer-style selected-item summary for the Files directory list.

Qt-free, and intentionally based on metadata already collected when the file
list was populated. Never recursively scan directories to calculate sizes.
"""


def _display_size(num_bytes):
    """Compact binary-unit size (as in Explorer's approximate KB/MB display)."""
    value = max(0, int(num_bytes))
    if value < 1024:
        return f'{value:,} B'
    for unit in ('KB', 'MB', 'GB', 'TB', 'PB'):
        value /= 1024
        if value < 1024 or unit == 'PB':
            return f'{value:,.2f}'.rstrip('0').rstrip('.') + f' {unit}'
    raise AssertionError('unreachable')


def files_selected_summary(rows):
    """Summarize actually selected rows. Directory contents are not counted.

    All rows come from the displayed Files second column; an unselected
    remembered/current row is not included. Missing file metadata is *not*
    treated as a known zero-byte file.
    """
    rows = [row for row in rows if isinstance(row, dict)]
    if not rows:
        return ''
    total_bytes = 0
    known_files = 0
    for row in rows:
        if row.get('item_kind') in ('category', 'directory'):
            continue
        size = row.get('_middle_size_bytes')
        if size is None:
            continue
        try:
            total_bytes += max(0, int(size))
        except (TypeError, ValueError, OverflowError):
            continue
        known_files += 1
    selected = f'{len(rows):,} 個の項目を選択'
    return selected + (f'  {_display_size(total_bytes)}' if known_files else '')
