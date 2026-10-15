"""OS-independent tests of Windows wallpaper double-click pairing."""
import unittest
import ctypes
from desktop_double_click import Click, ClickPair, Variant, OutsideClickGuard, DesktopDoubleClick


class PairTests(unittest.TestCase):
    def setUp(self):
        self.pair = ClickPair(500, 4, 4)

    def test_same_desktop_within_time_and_distance(self):
        self.assertFalse(self.pair.push(Click(100, 200, 1000, 123)))
        self.assertTrue(self.pair.push(Click(102, 201, 1400, 123)))
        self.assertFalse(self.pair.push(Click(101, 201, 1450, 123)))

    def test_app_windows_reset_sequence(self):
        self.assertFalse(self.pair.push(Click(100, 200, 1000, 123)))
        self.assertFalse(self.pair.push(Click(100, 200, 1200, 0)))
        self.assertFalse(self.pair.push(Click(100, 200, 1300, 123)))

    def test_other_view_does_not_form_pair(self):
        self.assertFalse(self.pair.push(Click(100, 200, 1000, 123)))
        self.assertFalse(self.pair.push(Click(100, 200, 1200, 456)))

    def test_far_or_slow_clicks_do_not_open(self):
        self.assertFalse(self.pair.push(Click(100, 200, 1000, 123)))
        self.assertFalse(self.pair.push(Click(104, 200, 1200, 123)))
        self.assertFalse(self.pair.push(Click(104, 200, 1900, 123)))
        self.assertTrue(self.pair.push(Click(104, 200, 1980, 123)))

    def test_windows_variant_abi_size(self):
        # A 16-byte VARIANT on Win64 would be overwritten by Oleacc.
        expected = 24 if ctypes.sizeof(ctypes.c_void_p) == 8 else 16
        self.assertEqual(ctypes.sizeof(Variant), expected)

    def test_windows_tick_overflow(self):
        self.assertFalse(self.pair.push(Click(100, 200, 0xFFFFFFF0, 123)))
        self.assertTrue(self.pair.push(Click(100, 200, 25, 123)))


class WindowsApiBindingTests(unittest.TestCase):
    def test_variant_clear_comes_from_oleaut32_not_ole32(self):
        # Simulate DLL exports: Ole32 intentionally has no VariantClear.
        from desktop_double_click import DesktopDoubleClick

        class Function:
            argtypes = None
            restype = None

        class Library:
            def __init__(self, exports):
                self.exports = {name: Function() for name in exports}

            def __getattr__(self, name):
                if name not in self.exports:
                    raise AttributeError('function %r not found' % name)
                return self.exports[name]

        api = DesktopDoubleClick.__new__(DesktopDoubleClick)
        api.user = Library(('GetDoubleClickTime', 'GetSystemMetrics',
                            'WindowFromPoint', 'GetWindowThreadProcessId', 'GetClassNameW', 'GetParent',
                            'FindWindowW', 'FindWindowExW',
                            'SetWindowsHookExW', 'UnhookWindowsHookEx',
                            'CallNextHookEx'))
        api.kernel = Library(('GetModuleHandleW',))
        api.ole32 = Library(('OleInitialize', 'OleUninitialize'))
        api.oleaut32 = Library(('VariantClear',))
        api.oleacc = Library(('AccessibleObjectFromPoint',))
        api._declare_functions()  # Must not touch ole32.VariantClear
        self.assertEqual(api.oleaut32.VariantClear.argtypes, [ctypes.POINTER(Variant)])
        self.assertEqual(api.oleaut32.VariantClear.restype, ctypes.c_long)





class HookIntegrationTests(unittest.TestCase):
    """Run real _mouse logic against a fake Win32 API / queued Qt timer."""
    def test_wallpaper_open_then_external_dismiss_without_accidental_reopen(self):
        import sys
        import types
        from unittest.mock import patch
        from ctypes import wintypes
        from desktop_double_click import LowLevelMouseInfo

        state = {'visible': False, 'opened': 0, 'dismissed': 0}
        scheduled = []
        timer = types.ModuleType('PySide6.QtCore')
        timer.QTimer = types.SimpleNamespace(singleShot=lambda ms, cb: scheduled.append(cb))
        root = types.ModuleType('PySide6')
        root.QtCore = timer
        def drain():
            while scheduled:
                scheduled.pop(0)()

        class FakeUser:
            def WindowFromPoint(self, point):
                return 77 if point.x >= 500 else 88

            def GetWindowThreadProcessId(self, hwnd, ppid):
                out = ctypes.cast(ppid, ctypes.POINTER(wintypes.DWORD))
                out.contents.value = 222 if hwnd == 77 else 111
                return 5

            def CallNextHookEx(self, hook, code, message, lparam):
                return 0

        api = DesktopDoubleClick.__new__(DesktopDoubleClick)
        api.user = FakeUser()
        api.hook = 999
        api.process_id = 111
        api.logger = None
        api.pair = ClickPair(500, 4, 4)
        api.raw_pair = ClickPair(500, 4, 4)
        api.outside_guard = OutsideClickGuard(500)
        api.is_launcher_visible = lambda: state['visible']
        api.on_outside_click = lambda: (state.__setitem__('dismissed', state['dismissed'] + 1),
                                        state.__setitem__('visible', False))
        api._view_at = lambda hwnd: 123 if hwnd == 77 else 0
        api._verify_and_open = lambda click: (state.__setitem__('opened', state['opened'] + 1),
                                              state.__setitem__('visible', True))

        def click(message, tick, x):
            info = LowLevelMouseInfo()
            info.pt.x, info.pt.y, info.time = x, 500, tick
            api._mouse(0, message, ctypes.addressof(info))
            drain()

        with patch.dict(sys.modules, {'PySide6': root, 'PySide6.QtCore': timer}):
            click(api.WM_LBUTTONDOWN, 1000, 800)
            click(api.WM_LBUTTONUP, 1050, 800)
            click(api.WM_LBUTTONDOWN, 1150, 800)
            click(api.WM_LBUTTONUP, 1200, 800)
            self.assertEqual(state['opened'], 1)
            self.assertTrue(state['visible'])

            # Own window and menus do not dismiss the launcher.
            click(api.WM_LBUTTONDOWN, 1220, 100)
            self.assertTrue(state['visible'])
            self.assertEqual(state['dismissed'], 0)

            # Single click on a different process closes the launcher.
            click(api.WM_LBUTTONDOWN, 1300, 800)
            self.assertFalse(state['visible'])
            self.assertEqual(state['dismissed'], 1)
            click(api.WM_LBUTTONUP, 1330, 800)
            click(api.WM_LBUTTONDOWN, 1390, 800)
            click(api.WM_LBUTTONUP, 1420, 800)
            self.assertEqual(state['opened'], 1)  # no bounce-open
            self.assertFalse(state['visible'])

            # Later desktop double click continues to launch normally.
            click(api.WM_LBUTTONDOWN, 2000, 800)
            click(api.WM_LBUTTONUP, 2020, 800)
            click(api.WM_LBUTTONDOWN, 2150, 800)
            click(api.WM_LBUTTONUP, 2170, 800)
            self.assertEqual(state['opened'], 2)
            self.assertTrue(state['visible'])

class OutsideClickTests(unittest.TestCase):
    def test_external_click_is_distinct_from_our_own_menus(self):
        self.assertFalse(DesktopDoubleClick._external_pid(101, 101))
        self.assertTrue(DesktopDoubleClick._external_pid(202, 101))
        self.assertFalse(DesktopDoubleClick._external_pid(0, 101))

    def test_after_outside_click_the_second_desktop_click_cannot_reopen(self):
        guard = OutsideClickGuard(500)
        guard.closed_on(1000)
        self.assertTrue(guard.blocks_open(1020))  # first button UP
        self.assertTrue(guard.blocks_open(1250))  # second button UP
        self.assertFalse(guard.blocks_open(1501))  # later double click works

    def test_guard_handles_os_timestamp_wraparound(self):
        guard = OutsideClickGuard(500)
        guard.closed_on(0xFFFFFFF0)
        self.assertTrue(guard.blocks_open(25))
        self.assertFalse(guard.blocks_open(700))

    def test_no_outside_dismiss_does_not_block_open(self):
        self.assertFalse(OutsideClickGuard(500).blocks_open(0))

if __name__ == '__main__':
    unittest.main()
