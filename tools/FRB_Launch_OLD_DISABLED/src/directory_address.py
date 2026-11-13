"""Explorer-like absolute Windows directory address contract (no Qt dependency).

The Files launch root is a convenience shortcut, *not* the navigation ceiling.
"""
import ntpath


def normalized_directory(path):
    """Return absolute drive/UNC Windows path, or None for unsafe/relative input."""
    if not isinstance(path, str):
        return None
    text = path.strip().strip('"').strip()
    if not text or '\x00' in text:
        return None
    # Explorer-style addresses use backslashes, even when an input used /.
    text = ntpath.normpath(text.replace('/', '\\'))
    drive, tail = ntpath.splitdrive(text)
    if not drive or not tail.startswith('\\'):
        return None  # reject 'C:foo', '\\foo', and bare drive-relative paths
    return text


def pending_directory_change(candidate, displayed):
    """Whether a candidate absolute path differs from the displayed folder.

    Windows directory comparisons are case-insensitive. Relative and empty
    entries are not actionable. In particular, an untouched current-path edit
    must never display the confirmation arrow.
    """
    candidate = normalized_directory(candidate)
    if not candidate:
        return False
    shown = normalized_directory(displayed)
    return shown is None or ntpath.normcase(candidate) != ntpath.normcase(shown)


def breadcrumb_segments(path):
    """Absolute ancestor segments; labels and targets are both real filesystem paths.

    F:\\FRB\\tools -> [('F:\\', 'F:\\'), ('FRB', 'F:\\FRB'), ...]
    UNC shares are treated as a root, never traversed above the share.
    """
    path = normalized_directory(path)
    if path is None:
        return []
    drive, remainder = ntpath.splitdrive(path)
    root = drive + '\\'
    pieces = [(root, root)]
    current = root
    for name in remainder.split('\\'):
        if name:
            current = ntpath.join(current, name)
            pieces.append((name, current))
    return pieces


def directory_row(path):
    """Synthetic row understood by Launcher's *existing* displayed_children()."""
    path = normalized_directory(path)
    if path is None:
        raise ValueError('directory_row requires an absolute drive/UNC path')
    return {'item_id': path, 'title': ntpath.basename(path) or path,
            'description': path, 'item_kind': 'directory',
            'launch_browse_target': path, 'icon_key': 'folder.yellow',
            '_address_synthetic': True}


def row_directory(row, expand=lambda s: s):
    if not row or row.get('item_kind') != 'directory':
        return None
    raw = row.get('launch_browse_target')
    try:
        return normalized_directory(expand(raw)) if isinstance(raw, str) else None
    except (TypeError, ValueError, OSError):
        return None


def compact_segments(segments, available, measure):
    """Prefer current folder and nearby ancestors, collapse distant parents to ….

    `measure` returns rendered segment width (including padding). Kept pure for
    deterministic testing and responsive layouts.
    """
    if not segments:
        return []
    width = max(0, int(available))
    gap = measure(' › ')
    def needed(parts):
        return sum(measure(label) for label, _ in parts) + max(0, len(parts)-1) * gap
    if needed(segments) <= width or len(segments) < 3:
        return segments
    root, last = segments[0], segments[-1]
    collapsed = ('…', None)
    result = [root, collapsed, last]
    # Fit the newest ancestors first, but INSERT each older ancestor before
    # the previously retained ones. Appending before `last` reversed the path
    # whenever two or more parents fit in a narrowed window.
    for candidate in reversed(segments[1:-1]):
        trial = result[:2] + [candidate] + result[2:]
        if needed(trial) > width:
            break
        result = trial
    return result
