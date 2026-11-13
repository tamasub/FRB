"""Windows IME focus policy for the launcher search field.

Disable the currently active IME on *new search focus*, not on each keypress,
so users may deliberately switch back to Japanese while editing.  A failure
never interrupts ordinary search input and never affects other applications.
"""
import ctypes
import os
from ctypes import wintypes


def initialize_halfwidth_english(hwnd=None):
    """Set IME OFF + alphanumeric/halfwidth on Windows; return success flag."""
    if os.name != 'nt':
        return False
    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        imm32 = ctypes.WinDLL('imm32', use_last_error=True)
        user32.GetFocus.argtypes = []
        user32.GetFocus.restype = wintypes.HWND
        imm32.ImmGetContext.argtypes = [wintypes.HWND]
        imm32.ImmGetContext.restype = wintypes.HANDLE
        imm32.ImmGetConversionStatus.argtypes = [wintypes.HANDLE,
                                                 ctypes.POINTER(wintypes.DWORD),
                                                 ctypes.POINTER(wintypes.DWORD)]
        imm32.ImmGetConversionStatus.restype = wintypes.BOOL
        imm32.ImmSetConversionStatus.argtypes = [wintypes.HANDLE,
                                                 wintypes.DWORD, wintypes.DWORD]
        imm32.ImmSetConversionStatus.restype = wintypes.BOOL
        imm32.ImmSetOpenStatus.argtypes = [wintypes.HANDLE, wintypes.BOOL]
        imm32.ImmSetOpenStatus.restype = wintypes.BOOL
        imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
        imm32.ImmReleaseContext.restype = wintypes.BOOL
        window = user32.GetFocus() or hwnd
        if not window:
            return False
        context = imm32.ImmGetContext(window)
        if not context:
            return False
        try:
            conversion = wintypes.DWORD()
            sentence = wintypes.DWORD()
            if imm32.ImmGetConversionStatus(context, ctypes.byref(conversion),
                                            ctypes.byref(sentence)):
                # Clear NATIVE and FULLSHAPE, preserving the other IME flags.
                new_conversion = conversion.value & ~(0x0001 | 0x0008)
                imm32.ImmSetConversionStatus(context, new_conversion, sentence.value)
            return bool(imm32.ImmSetOpenStatus(context, False))
        finally:
            imm32.ImmReleaseContext(window, context)
    except (OSError, AttributeError, ValueError):
        return False


def initialize_japanese_hiragana(hwnd=None):
    """Turn Windows IME on in hiragana (native/fullwidth) mode.

    Intended for the explicit FIRST Space on a folder cascade.  Unlike the
    global launcher search's English-default behavior, this is never called
    on every keystroke, so users remain free to switch IME modes themselves.
    Return False when unavailable; regular QLineEdit input still works.
    """
    if os.name != 'nt' or not hwnd:
        return False
    try:
        imm32 = ctypes.WinDLL('imm32', use_last_error=True)
        imm32.ImmGetContext.argtypes = [wintypes.HWND]
        imm32.ImmGetContext.restype = wintypes.HANDLE
        imm32.ImmReleaseContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
        imm32.ImmReleaseContext.restype = wintypes.BOOL
        imm32.ImmGetConversionStatus.argtypes = [wintypes.HANDLE,
                                                 ctypes.POINTER(wintypes.DWORD),
                                                 ctypes.POINTER(wintypes.DWORD)]
        imm32.ImmGetConversionStatus.restype = wintypes.BOOL
        imm32.ImmSetConversionStatus.argtypes = [wintypes.HANDLE,
                                                 wintypes.DWORD, wintypes.DWORD]
        imm32.ImmSetConversionStatus.restype = wintypes.BOOL
        imm32.ImmSetOpenStatus.argtypes = [wintypes.HANDLE, wintypes.BOOL]
        imm32.ImmSetOpenStatus.restype = wintypes.BOOL
        context = imm32.ImmGetContext(hwnd)
        if not context:
            return False
        try:
            # Open first: some Windows IMEs reject conversion changes while off.
            opened = bool(imm32.ImmSetOpenStatus(context, True))
            conversion = wintypes.DWORD()
            sentence = wintypes.DWORD()
            # IME_CMODE_NATIVE (hiragana), FULLSHAPE (full-width), ROMAN.
            # Clear KATAKANA; preserve other existing conversion flags.
            if imm32.ImmGetConversionStatus(context, ctypes.byref(conversion),
                                            ctypes.byref(sentence)):
                flags = (conversion.value | 0x0001 | 0x0008 | 0x0010) & ~0x0002
                return opened and bool(imm32.ImmSetConversionStatus(
                    context, flags, sentence.value))
            return False
        finally:
            imm32.ImmReleaseContext(hwnd, context)
    except (OSError, AttributeError, ValueError, TypeError):
        return False
