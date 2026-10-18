"""Recognize an empty-desktop double click without blocking Explorer mouse input.

The WH_MOUSE_LL hook gathers click pairs only. Win32 desktop window lookup and
MSAA icon rejection run on the Qt event loop. Unknown targets fail closed.
"""
from dataclasses import dataclass
import ctypes as c
from ctypes import wintypes as w
import os


@dataclass(frozen=True)
class Click:
    x: int
    y: int
    tick: int
    view: int


class ClickPair:
    """Track one candidate pair; accepts only same-view and OS-size/time doubles."""
    def __init__(self, interval_ms, width_px, height_px):
        self.interval_ms = interval_ms
        self.width_px = max(1, width_px)
        self.height_px = max(1, height_px)
        self.previous = None

    def push(self, point):
        if not point.view:
            self.previous = None
            return False
        prev = self.previous
        if (prev and point.view == prev.view
                and 0 <= (point.tick - prev.tick) % (1 << 32) <= self.interval_ms
                and abs(point.x - prev.x) <= self.width_px // 2
                and abs(point.y - prev.y) <= self.height_px // 2):
            self.previous = None
            return True
        self.previous = point
        return False


# Windows VARIANT has an 8-byte header and a union holding up to 2 pointers.
# Size is 24 bytes on Win64 (not 16!), 16 bytes on Win32.
class RecordData(c.Structure):
    _fields_ = [('record', c.c_void_p), ('info', c.c_void_p)]


class VariantData(c.Union):
    _fields_ = [('integer', c.c_long), ('pointer', c.c_void_p),
                ('longlong', c.c_longlong), ('record', RecordData)]


class Variant(c.Structure):
    _fields_ = [('vt', c.c_ushort), ('r1', c.c_ushort), ('r2', c.c_ushort),
                ('r3', c.c_ushort), ('data', VariantData)]


class OutsideClickGuard:
    """Avoid re-opening a launcher during an outside desktop double click.

    Mouse timestamps from the low-level hook are 32-bit milliseconds and may
    wrap. A close triggered by mouse DOWN must suppress the same click's UP
    and any second click of the pair, without suppressing later gestures.
    """

    def __init__(self, interval_ms):
        self.interval_ms = interval_ms
        self.last_outside_tick = None

    def closed_on(self, tick):
        self.last_outside_tick = tick

    def blocks_open(self, tick):
        if self.last_outside_tick is None:
            return False
        return ((tick - self.last_outside_tick) & 0xFFFFFFFF) <= self.interval_ms


class LowLevelMouseInfo(c.Structure):
    _fields_ = [('pt', w.POINT), ('mouseData', w.DWORD), ('flags', w.DWORD),
                ('time', w.DWORD), ('extra', c.c_size_t)]


class DesktopDoubleClick:
    """Windows-only lifecycle helper. Instantiate after QApplication exists."""
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_RBUTTONDOWN = 0x0204
    WH_MOUSE_LL = 14
    VT_I4 = 3
    ROLE_SYSTEM_WINDOW = 0x09
    ROLE_SYSTEM_CLIENT = 0x0A
    ROLE_SYSTEM_PANE = 0x10
    ROLE_SYSTEM_LIST = 0x21
    ROLE_SYSTEM_LISTITEM = 0x22
    RPC_E_CHANGED_MODE = -2147417850  # COM is already initialized as MTA.

    def __init__(self, on_double_click, logger=None, on_outside_click=None,
                 is_launcher_visible=None):
        self.on_double_click = on_double_click
        self.on_outside_click = on_outside_click
        self.is_launcher_visible = is_launcher_visible
        self.logger = logger
        self.process_id = os.getpid()
        self.hook = None
        self.callback = None
        self.ole_initialized = False
        self.desktop_view = 0
        if os.name != 'nt':
            return
        self.user = c.WinDLL('user32', use_last_error=True)
        self.kernel = c.WinDLL('kernel32', use_last_error=True)
        self.ole32 = c.OleDLL('ole32')
        self.oleaut32 = c.OleDLL('oleaut32')  # VARIANT helpers live in OLE Automation.
        self.oleacc = c.OleDLL('oleacc')
        self._declare_functions()
        interval = self.user.GetDoubleClickTime()
        width = self.user.GetSystemMetrics(36)  # SM_CXDOUBLECLK
        height = self.user.GetSystemMetrics(37)  # SM_CYDOUBLECLK
        self.pair = ClickPair(interval, width, height)
        self.raw_pair = ClickPair(interval, width, height)  # Diagnostic only.
        self.outside_guard = OutsideClickGuard(interval)
        if self.logger:
            self.logger.info("DESKTOP_CLICK_CONFIG interval=%s dx=%s dy=%s", interval, width, height)

    def _declare_functions(self):
        u = self.user
        u.GetDoubleClickTime.restype = w.UINT
        u.GetSystemMetrics.argtypes = [c.c_int]
        u.GetSystemMetrics.restype = c.c_int
        u.WindowFromPoint.argtypes = [w.POINT]
        u.WindowFromPoint.restype = w.HWND
        u.GetWindowThreadProcessId.argtypes = [w.HWND, c.POINTER(w.DWORD)]
        u.GetWindowThreadProcessId.restype = w.DWORD
        u.GetClassNameW.argtypes = [w.HWND, c.c_wchar_p, c.c_int]
        u.GetClassNameW.restype = c.c_int
        u.GetParent.argtypes = [w.HWND]
        u.GetParent.restype = w.HWND
        u.FindWindowW.argtypes = [c.c_wchar_p, c.c_wchar_p]
        u.FindWindowW.restype = w.HWND
        u.FindWindowExW.argtypes = [w.HWND, w.HWND, c.c_wchar_p, c.c_wchar_p]
        u.FindWindowExW.restype = w.HWND
        u.SetWindowsHookExW.argtypes = [c.c_int, c.c_void_p, w.HINSTANCE, w.DWORD]
        u.SetWindowsHookExW.restype = w.HHOOK
        u.UnhookWindowsHookEx.argtypes = [w.HHOOK]
        u.UnhookWindowsHookEx.restype = w.BOOL
        u.CallNextHookEx.argtypes = [w.HHOOK, c.c_int, c.c_size_t, c.c_ssize_t]
        u.CallNextHookEx.restype = c.c_ssize_t
        self.kernel.GetModuleHandleW.argtypes = [c.c_wchar_p]
        self.kernel.GetModuleHandleW.restype = w.HMODULE
        self.ole32.OleInitialize.argtypes = [c.c_void_p]
        self.ole32.OleInitialize.restype = c.c_long
        self.ole32.OleUninitialize.argtypes = []
        self.oleacc.AccessibleObjectFromPoint.argtypes = [w.POINT, c.POINTER(c.c_void_p), c.POINTER(Variant)]
        self.oleacc.AccessibleObjectFromPoint.restype = c.c_long
        self.oleaut32.VariantClear.argtypes = [c.POINTER(Variant)]
        self.oleaut32.VariantClear.restype = c.c_long

    def _class(self, hwnd):
        if not hwnd:
            return ''
        buf = c.create_unicode_buffer(256)
        return buf.value if self.user.GetClassNameW(hwnd, buf, len(buf)) else ''

    def _desktop_listview(self, hwnd):
        """Verify Explorer's real icon list, not an Explorer-folder list."""
        if self._class(hwnd) != 'SysListView32':
            return False
        parent = self.user.GetParent(hwnd)
        if self._class(parent) != 'SHELLDLL_DefView':
            return False
        # Win11 24H2 and wallpaper software can introduce intermediate WorkerW.
        # Require that the chain reaches the actual desktop shell host.
        ancestor = self.user.GetParent(parent)
        for _ in range(6):
            kind = self._class(ancestor)
            if kind in ('Progman', 'WorkerW'):
                return True
            if not ancestor or kind not in ('SHELLDLL_DefView', 'WorkerW'):
                break
            ancestor = self.user.GetParent(ancestor)
        return False

    def _scan_desktop_view(self):
        """Find desktop FolderView under either Progman or a WorkerW shell host."""
        hosts = []
        progman = self.user.FindWindowW('Progman', None)
        if progman:
            hosts.append(progman)
        worker = self.user.FindWindowExW(None, None, 'WorkerW', None)
        for _ in range(64):
            if not worker:
                break
            hosts.append(worker)
            worker = self.user.FindWindowExW(None, worker, 'WorkerW', None)
        # Some Windows 11 desktop layouts put a WorkerW inside Progman.
        if progman:
            worker = self.user.FindWindowExW(progman, None, 'WorkerW', None)
            for _ in range(32):
                if not worker:
                    break
                hosts.append(worker)
                worker = self.user.FindWindowExW(progman, worker, 'WorkerW', None)
        for host in hosts:
            shell = self.user.FindWindowExW(host, None, 'SHELLDLL_DefView', None)
            if not shell:
                continue
            view = self.user.FindWindowExW(shell, None, 'SysListView32', None)
            if view and self._desktop_listview(view):
                return int(view)
        return 0

    def _view_at(self, hwnd):
        """Match the hit HWND to the actual desktop, tolerating shell host hits.

        WindowFromPoint may yield the icon list, its view or a transparent
        WorkerW/Progman host depending on Win11 configuration. Explorer folder
        views are never accepted. Icon-vs-wallpaper is checked separately.
        """
        if not hwnd:
            return 0
        if self._desktop_listview(hwnd):
            return int(hwnd)
        if not self.desktop_view or not self._desktop_listview(self.desktop_view):
            self.desktop_view = self._scan_desktop_view()
        view = self.desktop_view
        if not view:
            return 0
        current = view
        for _ in range(7):
            if current == hwnd:
                return view
            current = self.user.GetParent(current)
            if not current:
                break
        return 0

    @staticmethod
    def _vtable_entry(interface, slot):
        return c.cast(interface, c.POINTER(c.POINTER(c.c_void_p))).contents[slot]

    @classmethod
    def _wallpaper_role(cls, role_hr, role, child_id):
        return (role_hr == 0 and role in (
            cls.ROLE_SYSTEM_CLIENT, cls.ROLE_SYSTEM_LIST,
            cls.ROLE_SYSTEM_PANE, cls.ROLE_SYSTEM_WINDOW
        ) and child_id in (0, None))

    def _empty_wallpaper(self, x, y, view):
        """MSAA must identify the *background*, not an icon or unknown object."""
        point = w.POINT(x, y)
        hwnd = self.user.WindowFromPoint(point)
        if self._view_at(hwnd) != view:
            if self.logger:
                self.logger.info('DESKTOP_VERIFY_CHANGED hit=%s class=%s', hwnd, self._class(hwnd))
            return False
        accessible = c.c_void_p()
        child = Variant()
        hr = self.oleacc.AccessibleObjectFromPoint(point, c.byref(accessible), c.byref(child))
        if hr != 0 or not accessible.value:
            if self.logger:
                self.logger.warning('DESKTOP_MSAA_FAILED hr=%s view=%s', hr, view)
            return False
        try:
            # IAccessible extends IDispatch (7 entries); get_accRole is at 13.
            get_role = c.WINFUNCTYPE(c.c_long, c.c_void_p, Variant, c.POINTER(Variant))(
                self._vtable_entry(accessible, 13))
            role = Variant()
            try:
                role_hr = get_role(accessible, child, c.byref(role))
                kind = int(role.data.integer) if role.vt == self.VT_I4 else None
                child_id = int(child.data.integer) if child.vt == self.VT_I4 else None
                empty = self._wallpaper_role(role_hr, kind, child_id)
                if self.logger:
                    self.logger.info('DESKTOP_MSAA_ROLE role=%s child=%s role_hr=%s empty=%s',
                                     kind, child_id, role_hr, empty)
                return empty
            finally:
                self.oleaut32.VariantClear(c.byref(role))
        finally:
            self.oleaut32.VariantClear(c.byref(child))
            release = c.WINFUNCTYPE(c.c_ulong, c.c_void_p)(self._vtable_entry(accessible, 2))
            release(accessible)

    def _verify_and_open(self, click):
        try:
            if self._empty_wallpaper(click.x, click.y, click.view):
                if self.logger:
                    self.logger.info("DESKTOP_OPEN_REQUEST view=%s", click.view)
                self.on_double_click()
        except Exception:
            if self.logger:
                self.logger.exception('Desktop double-click verification failed')

    @staticmethod
    def _external_pid(target_pid, own_pid):
        """An unknown Win32 target must not trigger a forced dismissal."""
        return bool(target_pid and target_pid != own_pid)

    def _outside_own_process(self, point):
        """Win32 hit-test instead of Qt focus: Tool/always-on-top may stay active."""
        hwnd = self.user.WindowFromPoint(point)
        if not hwnd:
            return False
        pid = w.DWORD()
        if not self.user.GetWindowThreadProcessId(hwnd, c.byref(pid)):
            return False
        # All our top-level menus and controls share this process id.
        return self._external_pid(pid.value, self.process_id)

    def _mouse(self, code, message, param):
        try:
            if code >= 0 and message in (
                    self.WM_LBUTTONDOWN, self.WM_RBUTTONDOWN, self.WM_LBUTTONUP):
                info = c.cast(param, c.POINTER(LowLevelMouseInfo)).contents
                if message in (self.WM_LBUTTONDOWN, self.WM_RBUTTONDOWN):
                    if (self.on_outside_click is not None
                            and self.is_launcher_visible is not None
                            and self.is_launcher_visible()
                            and self._outside_own_process(info.pt)):
                        # Use the visibility state at mouse DOWN: the desktop
                        # opening gesture itself must never close the new window.
                        self.outside_guard.closed_on(info.time)
                        self.pair.previous = None
                        self.raw_pair.previous = None
                        if self.logger:
                            self.logger.info('OUTSIDE_CLICK_DETECTED x=%s y=%s',
                                             info.pt.x, info.pt.y)
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, self.on_outside_click)
                elif self.outside_guard.blocks_open(info.time):
                    # The second UP of a double-click outside an open launcher
                    # must not reopen it immediately after it was dismissed.
                    self.pair.previous = None
                    self.raw_pair.previous = None
                else:
                    hwnd = self.user.WindowFromPoint(info.pt)
                    view = self._view_at(hwnd)
                    click = Click(info.pt.x, info.pt.y, info.time, view)
                    if self.raw_pair.push(Click(info.pt.x, info.pt.y, info.time, int(hwnd or 0))):
                        if not view and self.logger:
                            self.logger.info('DESKTOP_PAIR_IGNORED hit_class=%s parent_class=%s known_view=%s',
                                self._class(hwnd), self._class(self.user.GetParent(hwnd)), self.desktop_view)
                    if self.pair.push(click):
                        if self.logger:
                            self.logger.info('DESKTOP_PAIR_DETECTED x=%s y=%s view=%s',
                                             click.x, click.y, view)
                        # Hook callbacks must remain fast; MSAA belongs on Qt loop.
                        from PySide6.QtCore import QTimer
                        QTimer.singleShot(0, lambda click=click: self._verify_and_open(click))
        except Exception:
            if self.logger:
                self.logger.exception('Desktop mouse hook failed')
        return self.user.CallNextHookEx(self.hook, code, message, param)

    def start(self):
        if os.name != 'nt':
            return False
        if self.hook:
            return True
        hr = self.ole32.OleInitialize(None)
        if hr not in (0, 1, self.RPC_E_CHANGED_MODE):
            if self.logger:
                self.logger.warning('Desktop double-click unavailable: OleInitialize HRESULT=%s', hr)
            return False
        # Qt/the host may already have COM initialized with MTA. In that case
        # OleInitialize returns RPC_E_CHANGED_MODE; COM remains usable but its
        # apartment is owned by somebody else and must not be uninitialized here.
        self.ole_initialized = hr in (0, 1)
        if hr == self.RPC_E_CHANGED_MODE and self.logger:
            self.logger.info('DESKTOP_COM_EXISTING_APARTMENT hr=%s', hr)
        self.desktop_view = self._scan_desktop_view()
        if self.logger:
            self.logger.info('DESKTOP_VIEW_FOUND view=%s', self.desktop_view)
        signature = c.WINFUNCTYPE(c.c_ssize_t, c.c_int, c.c_size_t, c.c_ssize_t)
        self.callback = signature(self._mouse)
        self.hook = self.user.SetWindowsHookExW(
            self.WH_MOUSE_LL,
            c.cast(self.callback, c.c_void_p),
            self.kernel.GetModuleHandleW(None),
            0,
        )
        if not self.hook:
            if self.logger:
                self.logger.warning('Desktop double-click hook failed: %s', c.get_last_error())
            self.stop()
            return False
        return True

    def stop(self):
        if self.hook:
            self.user.UnhookWindowsHookEx(self.hook)
            self.hook = None
        self.callback = None
        if self.ole_initialized:
            self.ole32.OleUninitialize()
            self.ole_initialized = False
