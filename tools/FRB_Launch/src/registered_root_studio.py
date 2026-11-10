"""Authorize a configured Files Exp physical root as a Studio item.

Do not treat subdirectories, drive enumeration or runtime search hits as
editable merely because they have a path or a coincidentally matching title.
"""
import ntpath


def _windows_key(path):
    return ntpath.normcase(ntpath.normpath(str(path)))


def verified_registered_root(root, pages, authored_items, expand):
    """Return the canonical *authored* directory row if identity/path match."""
    if not isinstance(root, dict) or root.get('pc'):
        return None
    page_id, item_id = str(root.get('page_id') or ''), str(root.get('item_id') or '')
    path = root.get('path')
    if not page_id or not item_id or not isinstance(path, str) or not path:
        return None
    if not any(isinstance(page, dict) and page.get('enabled', True)
               and str(page.get('page_id')) == page_id for page in (pages or ())):
        return None
    for row in (authored_items or ()):
        if not isinstance(row, dict) or not row.get('enabled', True):
            continue
        if (str(row.get('page_id') or '') != page_id
                or str(row.get('item_id') or '') != item_id
                or row.get('item_kind') != 'directory'
                or row.get('_browser_bookmark') or row.get('_installed_app')):
            continue
        configured_path = row.get('launch_browse_target')
        if not isinstance(configured_path, str) or not configured_path.strip():
            return None
        try:
            actual_path = expand(configured_path)
        except (OSError, ValueError, TypeError, KeyError):
            return None
        return row if isinstance(actual_path, str) and _windows_key(actual_path) == _windows_key(path) else None
    return None
