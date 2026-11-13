"""Identify the owner of a launch row before offering a context menu.

Important: `data['items']` includes runtime-merged bookmarks/apps. It is NOT
an authoritative list of editable Studio items. `authored_items` must come
from the original Launch DataJSON on disk, before runtime catalogs are merged.
"""
from pathlib import Path
from cascade_properties import authored_cascade_row


def resolve_context_target(row, authored_items):
    """Return (origin, path); origin is studio/file/folder/none.

    Do not assume a title, item_kind or item_id indicates ownership. Physical
    entries must carry a runtime path marker created by the directory browser
    or the SQLite file index. Bookmarks and installed apps stay read-only.
    """
    if not isinstance(row, dict):
        return 'none', None
    if row.get('_browser_bookmark') or row.get('_installed_app'):
        return 'none', None
    # Dynamic rows are never editable Studio items, even if someone chose an
    # item_id colliding with a physical pathname or an external catalog ID.
    file_path = row.get('_indexed_file') or row.get('_browse_file') or row.get('_file')
    if isinstance(file_path, str) and file_path.strip():
        if row.get('_browse_file') or row.get('_indexed_file'):
            return 'file', file_path
        if row.get('item_kind') == 'directory':
            return 'folder', file_path
        if row.get('item_kind') == 'command':
            return 'file', file_path
        return 'none', None
    if authored_cascade_row(row, authored_items):
        return 'studio', None
    return 'none', None


def resolve_search_context_target(row, authored_items, expand=None):
    """Allow an authored *physical directory* to use the search folder menu.

    Outside main search, authored items remain Studio-owned.  Do not infer
    filesystem authority from the display title or a generic Open action.
    Require an actual configured browse directory and verify it still exists.
    """
    origin, path = resolve_context_target(row, authored_items)
    if origin != 'studio':
        return origin, path
    authored = authored_cascade_row(row, authored_items)
    if not authored or authored.get('item_kind') != 'directory':
        return origin, path
    target = authored.get('launch_browse_target')
    if not isinstance(target, str) or not target.strip():
        return origin, path
    if expand is not None:
        try:
            target = expand(target)
        except (ValueError, OSError, KeyError):
            return origin, path
    if isinstance(target, str) and Path(target).is_dir():
        return 'folder', target
    return origin, path
