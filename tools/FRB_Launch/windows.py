"""Small Windows API boundary. No hooks or administrative rights required."""
import ctypes as c
from ctypes import wintypes as w
import os
import time

IS_WINDOWS = os.name == 'nt'
if IS_WINDOWS:
    user = c.WinDLL('user32', use_last_error=True)
    user.GetForegroundWindow.restype = w.HWND
    user.SetForegroundWindow.argtypes = [w.HWND]
    user.IsWindow.argtypes = [w.HWND]
    user.RegisterHotKey.argtypes = [w.HWND, c.c_int, w.UINT, w.UINT]
    user.UnregisterHotKey.argtypes = [w.HWND, c.c_int]
    user.VkKeyScanW.argtypes = [w.WCHAR]
    user.VkKeyScanW.restype = c.c_short
    user.GetAsyncKeyState.argtypes = [c.c_int]
    user.GetAsyncKeyState.restype = c.c_short
    user.keybd_event.argtypes = [w.BYTE,w.BYTE,w.DWORD,c.c_size_t]


def foreground():
    return user.GetForegroundWindow() if IS_WINDOWS else 0


def restore(hwnd):
    if not IS_WINDOWS:
        raise RuntimeError('文字送信はWindowsで利用できます')
    if not hwnd or not user.IsWindow(hwnd):
        raise RuntimeError('送信先が見つかりません。入力欄からショートカットで呼び出してください')
    user.SetForegroundWindow(hwnd)
    time.sleep(.12)
    if foreground() != hwnd:
        raise RuntimeError('送信先へ戻れませんでした。入力欄から再度呼び出してください')
    # Release-triggered hotkeys can still have modifiers physically held.
    deadline = time.monotonic() + 2
    while any(user.GetAsyncKeyState(k) & 0x8000 for k in (0x10,0x11,0x12,0x7B)):
        if time.monotonic() > deadline:
            raise RuntimeError('修飾キーを離してから再実行してください')
        time.sleep(.015)


def paste(hwnd):
    restore(hwnd)
    for key, flag in [(0x11,0),(0x56,0),(0x56,2),(0x11,2)]:
        user.keybd_event(key,0,flag,0)


def hotkey(hwnd, text):
    if not IS_WINDOWS:
        return
    parts = text.split('+'); mods = 0x4000
    for part in parts[:-1]:
        if part.lower() not in {'ctrl','shift','alt','win'}:
            raise ValueError('不明なショートカット修飾キー')
        mods |= {'ctrl':2,'shift':4,'alt':1,'win':8}[part.lower()]
    key = parts[-1]
    if len(key) != 1:
        raise ValueError('呼び出しキーの末尾は1文字にしてください')
    scan = user.VkKeyScanW(key)
    if scan == -1 or not user.RegisterHotKey(hwnd,1,mods,scan & 255):
        raise RuntimeError(f'{text}を登録できません。他のアプリとの重複を確認してください')


def unhotkey(hwnd):
    if IS_WINDOWS:
        user.UnregisterHotKey(hwnd,1)
