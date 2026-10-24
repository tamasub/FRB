"""Resolve *physical files only* for outbound Windows drag & drop.

Bookmarks, installed apps and authored command strings are not filesystem
objects. Never infer a file from a label or a command-line suffix.
"""
from pathlib import Path


def file_path_for_drag(row):
    if not isinstance(row, dict) or row.get('_browser_bookmark') or row.get('_installed_app'):
        return None
    if row.get('item_kind') == 'directory':
        return None
    # Only source-provided physical markers, not UI labels or shell commands.
    for key in ('_indexed_file', '_browse_file', '_file'):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip() or '\x00' in value:
            continue
        try:
            path = Path(value)
            if path.is_file():
                return str(path.resolve())
        except (OSError, ValueError):
            pass
    return None
