"""Select Windows file-icon lookup without probing cloud file contents.

Qt's QFileIconProvider can request a file-type icon from a synthetic QFileInfo
(e.g. ``sample.xlsx``).  Prefer that for ordinary files: Box, OneDrive and
SharePoint placeholders need not report ``is_file()`` consistently, and icon
lookup must never require downloading their contents.

Individual icon-bearing files (.lnk/.exe/.ico) and installed applications still
use their actual paths; folder/drive behavior is left to the existing caller.
"""
from pathlib import PureWindowsPath


PATH_ICON_EXTENSIONS = frozenset({'.exe', '.lnk', '.ico', '.url', '.appref-ms'})


def icon_lookup(row):
    """Return (source, value) where source is 'type', 'path', or 'default'.

    This is a presentation choice only.  It does not claim the target is
    available, and must not affect open/copy/delete/browse behavior.
    """
    path = row.get('_icon_file') or row.get('_file')
    if not path:
        return ('default', row.get('icon_key', 'command'))

    # The installed-app catalog and drive roots have meaningful per-path icons.
    if row.get('_icon_file') or row.get('_system_drive'):
        return ('path', path)

    # Normal files can use their registered file-type icon, without touching
    # the path.  Keep folder and authored-menu icon decisions unchanged.
    if row.get('icon_key') == 'file' and row.get('item_kind') != 'directory':
        extension = PureWindowsPath(str(path)).suffix.casefold()
        if extension and extension not in PATH_ICON_EXTENSIONS:
            return ('type', extension)

    return ('path', path)
