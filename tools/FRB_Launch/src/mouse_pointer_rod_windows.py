"""Mouse Pointer Rod / Windows experiment: one native left click.

This adapter is deliberately separate from the default Qt Files row adapter.
It sends mouse BUTTON events only; MousePointerRodPad temporarily positions
and restores the real cursor with Qt's DPI-aware QCursor API.

No synthetic event is ever emitted unless Windows mode is explicitly enabled.
A SendInput success only means insertion into the input stream, not that a
higher-integrity target/Citrix session will accept the click.
"""

import ctypes
from ctypes import wintypes
import sys
import time

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
INPUT_MOUSE = 0


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG), ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [('mi', _MOUSEINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('data', _INPUT_UNION)]


def send_left_click():
    """Insert one native left press/release, or raise if it cannot be sent.

    A physical pad double-click invokes this function twice: the first click
    and the double-click release are already two separate user gestures.
    """
    if sys.platform != 'win32':
        raise OSError('Windows以外では利用できません')
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(_INPUT), ctypes.c_int)
    user32.SendInput.restype = wintypes.UINT
    data = (_INPUT * 2)(
        _INPUT(type=INPUT_MOUSE,
               data=_INPUT_UNION(mi=_MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTDOWN))),
        _INPUT(type=INPUT_MOUSE,
               data=_INPUT_UNION(mi=_MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTUP))),
    )
    inserted = user32.SendInput(len(data), data, ctypes.sizeof(_INPUT))
    if inserted != len(data):
        error = ctypes.get_last_error()
        raise OSError(error, 'SendInputが拒否されました（権限差・Citrix等の可能性）')
    return True


def click_at(target, *, cursor, double=False, defer_restore=None):
    """DPI-aware cursor warp, native click/double click, position restore.

    The caller passes Qt's QCursor rather than Win32 raw screen pixels because
    a per-monitor-DPI-aware Qt application uses logical global coordinates.
    The target is validated by the caller (on screen and not on the Remote).
    For a QMenu in this SAME Qt event thread, the caller may defer restoration
    until the native press/release has actually been processed. The ordinary
    (non-menu) path still restores immediately for backwards compatibility.
    """
    original = cursor.pos()
    try:
        cursor.setPos(target)
        if (cursor.pos() - target).manhattanLength() > 2:
            raise OSError('OSカーソルを差し棒の先端へ移動できませんでした')
        send_left_click()
        if double:
            # Keep the cursor on the SAME target and in the SAME window for
            # both clicks.  Brief interval stays below Windows dbl-click time.
            time.sleep(0.055)
            send_left_click()
        return True
    finally:
        if defer_restore is None:
            cursor.setPos(original)
        else:
            try:
                defer_restore(original, target)
            except Exception:
                # A failed scheduler must NEVER strand the physical cursor.
                cursor.setPos(original)
                raise


def restore_cursor_if_unchanged(cursor, original, target, tolerance=8):
    """Restore after queued Qt menu events unless the user moved the mouse.

    This belongs to the native Windows adapter, not the rod drawing/pad layer.
    """
    if (cursor.pos() - target).manhattanLength() <= tolerance:
        cursor.setPos(original)
        return True
    return False
