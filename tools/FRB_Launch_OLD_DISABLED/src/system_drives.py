"""Windows 'This PC' drive discovery for the expanded Files browser.

This module has no Qt dependency.  It intentionally provides *physical/mounted*
Windows drive letters instead of guessing volume labels from the Launch JSON.
"""
import ctypes
import ntpath
import os
from ctypes import wintypes

SHELL_THIS_PC = 'shell:mycomputerfolder'


def is_this_pc_shortcut(row):
    """Recognize the system shell target, not an editable title or item_id."""
    if not isinstance(row, dict):
        return False
    return any(str(step.get('launch_target', '')).strip().casefold() == SHELL_THIS_PC
               for step in row.get('launch_actions', ()) if isinstance(step, dict))


def drive_display_name(root, volume_label=''):
    """Explorer-like volume text, retaining its unambiguous drive letter."""
    drive, _ = ntpath.splitdrive(str(root).replace('/', '\\'))
    letter = drive.rstrip(':').upper()
    if len(letter) != 1 or not letter.isalpha():
        raise ValueError('Expected a drive letter root')
    return f'{volume_label.strip() or "ローカル ディスク"} ({letter}:)'


def windows_drive_roots():
    """Enumerate mounted Win32 drive roots; return [] outside Windows."""
    if os.name != 'nt':
        return []
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    getter = kernel32.GetLogicalDriveStringsW
    getter.argtypes = [wintypes.DWORD, wintypes.LPWSTR]
    getter.restype = wintypes.DWORD
    required = getter(0, None)
    if not required:
        return []
    buffer = ctypes.create_unicode_buffer(required + 1)
    written = getter(len(buffer), buffer)
    if not written or written >= len(buffer):
        return []
    return sorted((x for x in buffer[:written].split('\0') if x), key=str.casefold)


def windows_volume_label(root):
    """Read a volume name if available; inaccessible drives remain browseable."""
    if os.name != 'nt':
        return ''
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    getter = kernel32.GetVolumeInformationW
    getter.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD,
                       ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                       ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
    getter.restype = wintypes.BOOL
    label = ctypes.create_unicode_buffer(256)
    try:
        success = getter(root, label, len(label), None, None, None, None, 0)
    except OSError:
        return ''
    return label.value if success else ''


def drive_rows(roots=None, get_label=None):
    """Create real filesystem rows compatible with the existing browser.

    The caller can inject roots/labels for deterministic contract tests.
    """
    if roots is None:
        roots = windows_drive_roots()
    if get_label is None:
        get_label = windows_volume_label
    result = []
    for root in roots:
        drive, tail = ntpath.splitdrive(str(root).replace('/', '\\'))
        if len(drive) != 2 or not drive.endswith(':') or not tail.startswith('\\'):
            continue
        root = drive.upper() + '\\'
        label = get_label(root)
        result.append({
            'item_id': root, 'title': drive_display_name(root, label),
            'description': root, 'item_kind': 'directory',
            'launch_browse_target': root,
            'launch_actions': [{'launch_action_type': 'Open', 'launch_target': root}],
            'icon_key': 'folder.yellow', '_file': root, '_system_drive': True,
        })
    return result


def pc_preview_row(row):
    """Convert just This PC to a browseable category in expanded view only."""
    if not is_this_pc_shortcut(row):
        return row
    return dict(row, item_kind='category', _system_drives_root=True)
