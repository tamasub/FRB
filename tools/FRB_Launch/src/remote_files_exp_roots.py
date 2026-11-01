"""Read-only, Qt-free data helpers for Remote Files Exp's registered roots.

The first column of the *rendered* Files workspace is the authoritative list;
this helper must not deserialize, change, or duplicate Launch's DataJSON.
"""

import os


def registered_folder_roots(rows, expand):
    """Keep the displayed first-column order, label, and each directory path.

    This-PC is a virtual group; its actual drives are enumerated only if opened.
    Ignore non-directory commands, even when they happen to carry a target.
    """
    roots = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        label = str(row.get('title') or '').strip()
        if row.get('_system_drives_root'):
            roots.append({'label': label or 'PC', 'path': None, 'pc': True})
        elif row.get('item_kind') == 'directory':
            raw = row.get('launch_browse_target')
            if not isinstance(raw, str) or not raw.strip():
                continue
            try:
                path = expand(raw)
            except (OSError, ValueError, TypeError, KeyError):
                continue
            if isinstance(path, str) and path.strip():
                roots.append({'label': label or path, 'path': path, 'pc': False})
    return roots


def subdirectories(path):
    """Enumerate one level only when a branch is opened; safely skip errors.

    Do not traverse symlink directories to avoid following an accidental loop.
    """
    result = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        result.append((entry.name, entry.path))
                except (OSError, ValueError):
                    continue
    except (OSError, ValueError):
        return []
    return sorted(result, key=lambda part: part[0].casefold())
