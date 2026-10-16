"""Windows foreground-focus rules simulated without Windows or PySide6."""
import unittest
from unittest.mock import patch

import windows


class FakeUser32:
    def __init__(self, direct=False, allow_attach=True, changed_during_attach=False):
        self.current = 101  # Desktop Explorer starts as foreground.
        self.direct = direct
        self.allow_attach = allow_attach
        self.changed_during_attach = changed_during_attach
        self.attached = False
        self.calls = []

    def GetForegroundWindow(self):
        return self.current

    def IsWindow(self, hwnd):
        return hwnd == 202

    def SetForegroundWindow(self, hwnd):
        self.calls.append(('set_foreground', hwnd))
        if self.direct or self.attached:
            self.current = hwnd
            return True
        return False

    def GetWindowThreadProcessId(self, hwnd, out):
        return 888

    def AttachThreadInput(self, own, other, enable):
        self.calls.append(('attach', own, other, bool(enable)))
        if enable and not self.allow_attach:
            return False
        self.attached = bool(enable)
        if enable and self.changed_during_attach:
            self.current = 303
        return True

    def BringWindowToTop(self, hwnd):
        self.calls.append(('bring_to_top', hwnd))
        return True


class FocusTests(unittest.TestCase):
    def invoke(self, fake, **kwargs):
        class FakeKernel:
            @staticmethod
            def GetCurrentThreadId():
                return 777

        with (patch.object(windows, 'IS_WINDOWS', True),
              patch.object(windows, 'user', fake, create=True),
              patch.object(windows, 'kernel', FakeKernel(), create=True)):
            return windows.activate_keyboard_window(202, **kwargs)

    def test_already_foreground_no_api_calls(self):
        u = FakeUser32(); u.current = 202
        self.assertTrue(self.invoke(u, expected_foreground=101))
        self.assertEqual(u.calls, [])

    def test_direct_activation_needs_no_attachment(self):
        u = FakeUser32(direct=True)
        self.assertTrue(self.invoke(u, expected_foreground=101))
        self.assertEqual(u.calls, [('set_foreground', 202)])

    def test_explorer_background_uses_temporary_attachment(self):
        u = FakeUser32()
        self.assertTrue(self.invoke(u, expected_foreground=101))
        self.assertEqual(u.current, 202)
        self.assertFalse(u.attached)
        self.assertEqual(u.calls, [
            ('set_foreground', 202),
            ('attach', 777, 888, True),
            ('bring_to_top', 202),
            ('set_foreground', 202),
            ('attach', 777, 888, False),
        ])

    def test_no_focus_theft_if_other_app_activated(self):
        u = FakeUser32(); u.current = 303
        self.assertFalse(self.invoke(u, expected_foreground=101))
        self.assertEqual(u.calls, [])

    def test_attach_failure_never_assumes_keyboard_focus(self):
        u = FakeUser32(allow_attach=False)
        self.assertFalse(self.invoke(u, expected_foreground=101))
        self.assertFalse(u.attached)

    def test_switch_during_attach_is_safe_and_always_detaches(self):
        u = FakeUser32(changed_during_attach=True)
        self.assertFalse(self.invoke(u, expected_foreground=101))
        self.assertFalse(u.attached)
        self.assertEqual(u.current, 303)
        self.assertNotIn(('bring_to_top', 202), u.calls)

    def test_invalid_window_no_action(self):
        u = FakeUser32()
        self.assertFalse(self.invalid(u))
        self.assertEqual(u.calls, [])

    def invalid(self, u):
        with (patch.object(windows, 'IS_WINDOWS', True),
              patch.object(windows, 'user', u, create=True)):
            return windows.activate_keyboard_window(0)


if __name__ == '__main__':
    unittest.main()
