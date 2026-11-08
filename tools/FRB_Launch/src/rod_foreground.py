"""Detect whether the real OS foreground window belongs to this application.

A Qt Tool overlay may stay topmost after another Windows application activates.
Qt activeWindow() is insufficient because the overlay itself never takes focus.
"""
import os
import sys


def foreground_owned_by_process(*, get_foreground=None, get_pid=None, own_pid=None):
    """Return False for an unknown foreground, never authorize a native click."""
    if own_pid is None:
        own_pid = os.getpid()
    if get_foreground is None or get_pid is None:
        if sys.platform != 'win32':
            # Qt is responsible for non-Windows focus state in caller.
            return None
        import ctypes
        from ctypes import wintypes
        api = ctypes.windll.user32
        api.GetForegroundWindow.restype = wintypes.HWND
        api.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        api.GetWindowThreadProcessId.restype = wintypes.DWORD
        get_foreground = api.GetForegroundWindow
        def get_pid(window):
            result = wintypes.DWORD(0)
            api.GetWindowThreadProcessId(window, ctypes.byref(result))
            return result.value
    try:
        window = get_foreground()
        return bool(window and get_pid(window) == own_pid)
    except (OSError, ValueError, RuntimeError):
        return False
