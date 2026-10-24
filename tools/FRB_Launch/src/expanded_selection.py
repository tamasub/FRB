"""Real-path selection rules for the expanded Files column (no GUI dependency)."""
from pathlib import Path
from context_menu_resolver import resolve_context_target


def physical_paths(rows, authored_items=()):
    """Return unique, existing physical paths; reject authored commands/bookmarks."""
    result, seen = [], set()
    for row in rows:
        kind, value = resolve_context_target(row, authored_items)
        if kind not in ('file', 'folder') or not value:
            continue
        try:
            original = Path(value)
            if original.is_symlink():
                continue
            path = original.resolve(strict=True)
            if not (path.is_file() or path.is_dir()):
                continue
        except (OSError, ValueError):
            continue
        key = str(path).casefold()
        if key not in seen:
            result.append(path)
            seen.add(key)
    return result


def context_paths(clicked, selected_rows, authored_items=()):
    """Right click inside selection keeps batch; outside switches to one target."""
    choices = selected_rows if clicked in selected_rows else [clicked]
    return physical_paths(choices, authored_items)
