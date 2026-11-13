"""Small Windows API boundary. No hooks or administrative rights required."""
import ctypes as c
from ctypes import wintypes as w
import os
import time

IS_WINDOWS = os.name == 'nt'
if IS_WINDOWS:
    user = c.WinDLL('user32', use_last_error=True)
    user.GetForegroundWindow.restype = w.HWND
    user.GetClassNameW.argtypes = [w.HWND, w.LPWSTR, c.c_int]
    user.GetClassNameW.restype = c.c_int
    user.GetParent.argtypes = [w.HWND]
    user.GetParent.restype = w.HWND
    user.SetForegroundWindow.argtypes = [w.HWND]
    user.SetForegroundWindow.restype = w.BOOL
    user.AllowSetForegroundWindow.argtypes = [w.DWORD]
    user.AllowSetForegroundWindow.restype = w.BOOL
    user.GetWindowThreadProcessId.argtypes = [w.HWND, c.POINTER(w.DWORD)]
    user.GetWindowThreadProcessId.restype = w.DWORD
    user.AttachThreadInput.argtypes = [w.DWORD, w.DWORD, w.BOOL]
    user.AttachThreadInput.restype = w.BOOL
    user.BringWindowToTop.argtypes = [w.HWND]
    user.BringWindowToTop.restype = w.BOOL
    user.SetWindowPos.argtypes = [w.HWND, w.HWND, c.c_int, c.c_int, c.c_int, c.c_int, w.UINT]
    user.SetWindowPos.restype = w.BOOL
    user.GetLastInputInfo.argtypes = [c.c_void_p]
    user.GetLastInputInfo.restype = w.BOOL
    kernel = c.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentThreadId.restype = w.DWORD
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


def desktop_shell_foreground():
    """Return the foreground HWND only if it is the Windows desktop shell.

    During a verified desktop double-click, Explorer may become foreground
    *after* the mouse hook's callback. Trust only the desktop host class,
    never an arbitrary new foreground app (e.g. Chrome).
    """
    hwnd = foreground()
    if not IS_WINDOWS or not hwnd:
        return 0
    name = c.create_unicode_buffer(128)
    if not user.GetClassNameW(hwnd, name, len(name)):
        return 0
    return hwnd if name.value in ('Progman', 'WorkerW') else 0


def verified_desktop_view_foreground(desktop_view):
    """Accept only the clicked desktop view itself or one of its shell parents.

    Explorer's desktop can surface its SysListView32 or SHELLDLL_DefView
    HWND rather than Progman/WorkerW as foreground while a click settles.
    The view comes from the verified desktop MSAA path, never arbitrary input.
    """
    current = foreground()
    if not IS_WINDOWS or not current or not desktop_view or not user.IsWindow(desktop_view):
        return 0
    candidate = desktop_view
    for _ in range(8):
        if candidate == current:
            return current
        candidate = user.GetParent(candidate)
        if not candidate:
            break
    return 0


def activate_keyboard_window(hwnd, expected_foreground=None, input_window=None):
    """Activate a launcher summoned by a desktop mouse hook.

    Qt's activateWindow() can leave an always-on-top Tool visible but NOT
    keyboard-active when Explorer owns the foreground. Attach temporarily to
    that input queue and ask Windows to activate our window. Never attach to
    a different application that became foreground after the summon request.
    This is not a global keyboard hook and does not synthesize key presses.
    """
    if not IS_WINDOWS:
        return False
    if not hwnd or not user.IsWindow(hwnd):
        return False
    current = foreground()
    if current == hwnd:
        return True
    if expected_foreground is not None:
        allowed = (expected_foreground if isinstance(expected_foreground,
                   (tuple, list, set, frozenset)) else (expected_foreground,))
        if current not in allowed:
            return False  # Another app got focus: never steal it back.
    if not current:
        return False

    user.SetForegroundWindow(hwnd)
    if foreground() == hwnd:
        return True

    # SetForegroundWindow from a background mouse-hook process may be denied.
    # Try foreground input queue first, then the actual desktop input queue
    # when a VERIFIED desktop double-click supplied its view HWND.  Chrome can
    # remain GetForegroundWindow() even after Explorer received that click.
    own_thread = kernel.GetCurrentThreadId()
    if not own_thread:
        return False
    sources = [current]
    if input_window and input_window != current and user.IsWindow(input_window):
        sources.append(input_window)
    attempted_threads = set()
    for source in sources:
        source_thread = user.GetWindowThreadProcessId(source, None)
        if not source_thread or source_thread == own_thread or source_thread in attempted_threads:
            continue
        attempted_threads.add(source_thread)
        if not user.AttachThreadInput(own_thread, source_thread, True):
            continue
        try:
            # Do not steal focus if the user changed to another app.
            if foreground() != current:
                return False
            user.BringWindowToTop(hwnd)
            user.SetForegroundWindow(hwnd)
            if foreground() == hwnd:
                return True
        finally:
            user.AttachThreadInput(own_thread, source_thread, False)
    return False


class LastInputInfo(c.Structure):
    _fields_ = [('cbSize', w.UINT), ('dwTime', w.DWORD)]


def desktop_click_still_last_input(mouse_tick, tolerance_ms=48):
    """Only retry a verified wallpaper gesture if no newer user input occurred.

    LL mouse-hook timestamps and LASTINPUTINFO.dwTime share the Win32 tick
    domain.  A small tolerance permits a delayed release/message, but a later
    click or keypress cancels the request instead of stealing focus.
    """
    if not IS_WINDOWS or mouse_tick is None:
        return False
    info = LastInputInfo()
    info.cbSize = c.sizeof(LastInputInfo)
    if not user.GetLastInputInfo(c.byref(info)):
        return False  # Fail closed when the OS state is unavailable.
    return ((int(info.dwTime) - int(mouse_tick)) & 0xffffffff) <= tolerance_ms


def raise_normal_window(hwnd):
    """Explicit user-requested Z-order repair, NOT an always-on-top switch.

    Qt.raise_()/activateWindow() may finish while Explorer is processing the
    desktop double-click.  The delayed native HWND_TOP request puts the normal
    Launcher above other non-topmost apps without changing its window style,
    focus, geometry, or future behavior when Chrome is clicked again.
    """
    if not IS_WINDOWS or not hwnd or not user.IsWindow(hwnd):
        return False
    hwnd_top = 0
    swp_no_size = 0x0001
    swp_no_move = 0x0002
    swp_no_activate = 0x0010
    return bool(user.SetWindowPos(hwnd, hwnd_top, 0, 0, 0, 0,
                                  swp_no_size | swp_no_move | swp_no_activate))


def set_window_topmost(hwnd, enabled):
    """Temporarily drop/restore a launcher's topmost z-order without hiding it.

    This is for provider-owned Copy Link dialogs, not a global change to the
    launcher style or a forced activation of an external application.
    No size/position/foreground changes; native Win32 is deliberate because
    Qt.setWindowFlags() would hide and recreate the visible tool window.
    """
    if not IS_WINDOWS or not hwnd or not user.IsWindow(hwnd):
        return False
    hwnd_topmost = -1
    hwnd_notopmost = -2
    swp_no_size = 0x0001
    swp_no_move = 0x0002
    swp_no_activate = 0x0010
    return bool(user.SetWindowPos(hwnd, hwnd_topmost if enabled else hwnd_notopmost,
                                  0, 0, 0, 0,
                                  swp_no_size | swp_no_move | swp_no_activate))


def allow_child_foreground(pid):
    """Let a just-started GUI process activate its own splash/window.

    Must be requested while this launcher is foreground; Windows can decline
    (and revoke permission when the user interacts with another application).
    Never force another process to the top or make it permanently topmost.
    """
    if not IS_WINDOWS or not pid or int(pid) <= 0:
        return False
    return bool(user.AllowSetForegroundWindow(int(pid)))


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


def hotkey(hwnd, text, hotkey_id=1):
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
    if scan == -1 or not user.RegisterHotKey(hwnd,hotkey_id,mods,scan & 255):
        raise RuntimeError(f'{text}を登録できません。他のアプリとの重複を確認してください')


def unhotkey(hwnd, hotkey_id=1):
    if IS_WINDOWS:
        user.UnregisterHotKey(hwnd,hotkey_id)


def chrome_path():
    """Find installed Chrome without relying on the default browser."""
    import shutil
    candidates=[]
    if IS_WINDOWS:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
            for view in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
                try:
                    with winreg.OpenKey(hive,r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",0,winreg.KEY_READ|view) as key:
                        candidates.append(winreg.QueryValueEx(key,None)[0].strip('"'))
                except OSError:pass
    for name in ('LOCALAPPDATA','PROGRAMFILES','PROGRAMFILES(X86)'):
        if os.environ.get(name):candidates.append(os.path.join(os.environ[name],'Google','Chrome','Application','chrome.exe'))
    found=shutil.which('chrome.exe')
    if found:candidates.append(found)
    return next((p for p in candidates if os.path.isfile(p)),None)


def open_chrome(url):
    import subprocess
    if not IS_WINDOWS:raise RuntimeError('起動操作はWindowsで利用できます')
    if not url.lower().startswith(('https://','http://')):raise ValueError('Chromeにはhttp/httpsのURLを指定してください')
    program=chrome_path()
    if not program:raise RuntimeError('Google Chromeが見つかりません。Chromeをインストールしてください')
    subprocess.Popen([program,url])


def edge_path():
    """Find installed Edge without relying on the Windows default browser."""
    import shutil
    candidates=[]
    if IS_WINDOWS:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
            for view in (winreg.KEY_WOW64_64KEY,winreg.KEY_WOW64_32KEY):
                try:
                    with winreg.OpenKey(hive,r"Software\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",0,winreg.KEY_READ|view) as key:
                        candidates.append(winreg.QueryValueEx(key,None)[0].strip('"'))
                except OSError:pass
    for name in ('LOCALAPPDATA','PROGRAMFILES','PROGRAMFILES(X86)'):
        if os.environ.get(name):
            candidates.append(os.path.join(os.environ[name],'Microsoft','Edge','Application','msedge.exe'))
    found=shutil.which('msedge.exe')
    if found:candidates.append(found)
    return next((p for p in candidates if os.path.isfile(p)),None)


def open_browser(url, browser, profile=''):
    """Open a bookmark with its originating browser and profile."""
    import re
    import subprocess
    if not IS_WINDOWS:raise RuntimeError('ブラウザ起動はWindowsで利用できます')
    if not url.lower().startswith(('https://','http://')):
        raise ValueError('URLはhttp/httpsのみ対応しています')
    if browser not in ('chrome','edge'):raise ValueError('対象ブラウザが不明です')
    program=chrome_path() if browser=='chrome' else edge_path()
    if not program:raise RuntimeError(('Chrome' if browser=='chrome' else 'Edge')+'が見つかりません')
    args=[program]
    if profile:
        if not re.fullmatch(r'(?:Default|Profile [0-9]+)',profile):
            raise ValueError('不正なブラウザプロフィールです')
        args.append('--profile-directory='+profile)
    args.append(url)
    subprocess.Popen(args)
