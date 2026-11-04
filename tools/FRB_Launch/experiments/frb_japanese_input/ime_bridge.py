"""FRB Japanese Input v0.6: experimental Windows IME keyboard bridge.

This module does NOT implement a conversion engine, inspect the IME candidate
list, or guarantee conversion. It emits physical-like romaji key strokes to
the active editor so a user-enabled Windows IME can perform composition.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

# Explicit romaji, no Unicode packet insertion: VK_PACKET bypasses much of
# the normal IME key composition path. Tested against model contracts only;
# actual Microsoft IME behavior must be validated on Windows.
_BASE = {
    'あ':'a','い':'i','う':'u','え':'e','お':'o',
    'か':'ka','き':'ki','く':'ku','け':'ke','こ':'ko',
    'さ':'sa','し':'shi','す':'su','せ':'se','そ':'so',
    'た':'ta','ち':'chi','つ':'tsu','て':'te','と':'to',
    'な':'na','に':'ni','ぬ':'nu','ね':'ne','の':'no',
    'は':'ha','ひ':'hi','ふ':'fu','へ':'he','ほ':'ho',
    'ま':'ma','み':'mi','む':'mu','め':'me','も':'mo',
    'や':'ya','ゆ':'yu','よ':'yo',
    'ら':'ra','り':'ri','る':'ru','れ':'re','ろ':'ro',
    'わ':'wa','を':'wo','ん':"nn",'ー':'-',
    'が':'ga','ぎ':'gi','ぐ':'gu','げ':'ge','ご':'go',
    'ざ':'za','じ':'ji','ず':'zu','ぜ':'ze','ぞ':'zo',
    'だ':'da','ぢ':'di','づ':'du','で':'de','ど':'do',
    'ば':'ba','び':'bi','ぶ':'bu','べ':'be','ぼ':'bo',
    'ぱ':'pa','ぴ':'pi','ぷ':'pu','ぺ':'pe','ぽ':'po',
    'ゔ':'vu',
    'ぁ':'xa','ぃ':'xi','ぅ':'xu','ぇ':'xe','ぉ':'xo',
    'っ':'xtsu','ゃ':'xya','ゅ':'xyu','ょ':'xyo','ゎ':'xwa',
    '、':',','。':'.','？':'?','！':'!',
}


def romaji_for(char: str) -> str:
    """Return physical keyboard sequence or refuse unsupported characters."""
    if char not in _BASE:
        raise ValueError(f"IME送信未対応の文字: {char}")
    return _BASE[char]


def plan_preedit_transition(before: str, after: str) -> list[str]:
    """Make a small edit to existing preedit instead of retyping the whole line.

    Output tokens: BACKSPACE, or single ASCII keystroke. Requires a live,
    unchanged IME composition at the target's input focus.
    """
    common = 0
    for a, b in zip(before, after):
        if a != b:
            break
        common += 1
    suffix = after[common:]
    # Validate the complete plan before sending ANY key to the target.
    typing = [key for char in suffix for key in romaji_for(char)]
    return ['BACKSPACE'] * (len(before) - common) + typing


@dataclass
class ExternalImeSession:
    """Lock to one foreground editor until the user explicitly commits.

    Sender implements send_tokens(sequence), foreground_window(), same_process.
    """
    sender: object
    target: int | None = None
    synced_preedit: str = ''

    def _current_target(self) -> int:
        hwnd = self.sender.foreground_window()
        if not hwnd or self.sender.is_our_process(hwnd):
            raise RuntimeError('送信先のエディタをクリックしてください')
        if self.target is not None and hwnd != self.target:
            raise RuntimeError('送信先が変わりました。確定するかIME送信をOFFにしてください')
        return hwnd

    def sync(self, new_preedit: str) -> None:
        tokens = plan_preedit_transition(self.synced_preedit, new_preedit)
        if not tokens:
            return
        hwnd = self._current_target()
        self.sender.send_tokens(tokens)
        self.target = hwnd
        self.synced_preedit = new_preedit

    def commit(self) -> None:
        if not self.synced_preedit:
            return
        self._current_target()
        self.sender.send_tokens(['ENTER'])
        self.target = None
        self.synced_preedit = ''

    def reset(self, cancel_external: bool = False) -> None:
        if cancel_external and self.synced_preedit:
            self._current_target()
            self.sender.send_tokens(['ESCAPE'])
        self.target = None
        self.synced_preedit = ''


class Win32KeyboardSender:
    """ctypes WinAPI adapter. Windows only, no third-party dependencies."""
    def __init__(self) -> None:
        if sys.platform != 'win32':
            raise RuntimeError('IME送信はWindowsのみ対応')
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        U_PTR = ctypes.c_size_t

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG),
                        ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                        ('time', wintypes.DWORD), ('dwExtraInfo', U_PTR)]

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD),
                        ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD),
                        ('dwExtraInfo', U_PTR)]

        class HARDWAREINPUT(ctypes.Structure):
            _fields_ = [('uMsg', wintypes.DWORD), ('wParamL', wintypes.WORD),
                        ('wParamH', wintypes.WORD)]

        class INPUT_UNION(ctypes.Union):
            _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]

        class INPUT(ctypes.Structure):
            _fields_ = [('type', wintypes.DWORD), ('payload', INPUT_UNION)]

        self.INPUT = INPUT
        self.KEYBDINPUT = KEYBDINPUT
        self.user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
        self.user32.SendInput.restype = wintypes.UINT
        self.user32.VkKeyScanW.argtypes = [wintypes.WCHAR]
        self.user32.VkKeyScanW.restype = ctypes.c_short
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
        self.user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
        self.user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
        self.user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        self.user32.SetWindowPos.restype = wintypes.BOOL
        self._old_exstyles: dict[int, int] = {}

    def foreground_window(self) -> int:
        return int(self.user32.GetForegroundWindow() or 0)

    def is_our_process(self, hwnd: int) -> bool:
        from ctypes import wintypes
        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, self.ctypes.byref(pid))
        return pid.value == os.getpid()

    def set_noactivate(self, hwnd: int, enabled: bool) -> None:
        WS_EX_NOACTIVATE = 0x08000000
        GWL_EXSTYLE = -20
        SWP_FLAGS = 0x0001 | 0x0002 | 0x0010 | 0x0020  # NOMOVE,NOSIZE,NOACTIVATE,FRAMECHANGED
        old = int(self.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE))
        if enabled:
            self._old_exstyles[hwnd] = old
            new = old | WS_EX_NOACTIVATE
        else:
            new = self._old_exstyles.pop(hwnd, old & ~WS_EX_NOACTIVATE)
        if new != old:
            self.ctypes.set_last_error(0)
            result = self.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new)
            if result == 0 and self.ctypes.get_last_error():
                raise OSError(self.ctypes.get_last_error(), 'SetWindowLongPtrW failed')
            if not self.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_FLAGS):
                raise OSError(self.ctypes.get_last_error(), 'SetWindowPos failed')

    def send_tokens(self, tokens: list[str]) -> None:
        KEYUP = 0x0002
        SHIFT = 0x10
        vkeys = {'BACKSPACE': 0x08, 'ENTER': 0x0D, 'ESCAPE': 0x1B}
        out = []

        def event(vk: int, release=False):
            out.append(self.INPUT(1, self.INPUT._fields_[1][1](
                ki=self.KEYBDINPUT(vk, 0, KEYUP if release else 0, 0, 0))))

        for token in tokens:
            if token in vkeys:
                vk, mods = vkeys[token], 0
            elif len(token) == 1 and token.isascii():
                scan = int(self.user32.VkKeyScanW(token))
                if scan == -1:
                    raise ValueError(f'Cannot map key: {token!r}')
                vk, mods = scan & 0xFF, (scan >> 8) & 0xFF
                if mods & ~1:
                    raise ValueError(f'Unsupported keyboard modifier: {token!r}')
            else:
                raise ValueError(f'Unknown keystroke: {token!r}')
            if mods & 1:
                event(SHIFT)
            event(vk)
            event(vk, True)
            if mods & 1:
                event(SHIFT, True)

        if not out:
            return
        arr = (self.INPUT * len(out))(*out)
        count = self.user32.SendInput(len(out), arr, self.ctypes.sizeof(self.INPUT))
        if count != len(out):
            raise OSError(self.ctypes.get_last_error(),
                          f'SendInput injected {count}/{len(out)} events')
