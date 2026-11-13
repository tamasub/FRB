"""Win11 shell topology and conservative accessible role checks (mocked)."""
import unittest
from desktop_double_click import DesktopDoubleClick


class FakeUser:
    def __init__(self):
        self.parents = {103: 102, 102: 101, 101: 0, 903: 902, 902: 901, 901: 0}
        self.children = {
            (101, 0, 'SHELLDLL_DefView'): 102,
            (102, 0, 'SysListView32'): 103,
        }

    def GetParent(self, hwnd):
        return self.parents.get(hwnd, 0)

    def FindWindowW(self, kind, title):
        return 101 if kind == 'Progman' else 0

    def FindWindowExW(self, parent, after, kind, title):
        return self.children.get((parent or 0, after or 0, kind), 0)


class Win11DetectionTests(unittest.TestCase):
    def setUp(self):
        self.device = DesktopDoubleClick.__new__(DesktopDoubleClick)
        self.device.user = FakeUser()
        self.device.desktop_view = 0
        classes = {101: 'Progman', 102: 'SHELLDLL_DefView', 103: 'SysListView32',
                   901: 'CabinetWClass', 902: 'SHELLDLL_DefView', 903: 'SysListView32'}
        self.device._class = lambda hwnd: classes.get(hwnd, '')

    def test_desktop_listview_and_shell_parent_both_recognized(self):
        self.assertTrue(self.device._desktop_listview(103))
        self.assertEqual(self.device._view_at(103), 103)
        self.assertEqual(self.device._view_at(102), 103)
        self.assertEqual(self.device._view_at(101), 103)

    def test_explorer_folder_view_not_recognized(self):
        self.assertFalse(self.device._desktop_listview(903))
        self.assertEqual(self.device._view_at(903), 0)

    def test_accessible_role_does_not_open_for_icons(self):
        role = DesktopDoubleClick._wallpaper_role
        self.assertTrue(role(0, 0x21, 0))  # desktop list itself
        self.assertTrue(role(0, 0x0A, 0))  # client area
        self.assertTrue(role(0, 0x10, 0))  # Windows desktop pane
        self.assertFalse(role(0, 0x22, 0))  # icon list item
        self.assertFalse(role(0, 0x21, 12))  # non-background child
        self.assertFalse(role(-1, 0x21, 0))  # MSAA error
        self.assertFalse(role(0, None, 0))  # unknown role

    def test_workerw_nested_inside_progman(self):
        self.device.user.parents.update({210: 200, 200: 101})
        self.device.user.children.update({
            (101, 0, 'WorkerW'): 200,
            (200, 0, 'SHELLDLL_DefView'): 210,
            (210, 0, 'SysListView32'): 211,
        })
        self.device.user.parents[211] = 210
        base = self.device._class
        self.device._class = lambda h: {200:'WorkerW', 210:'SHELLDLL_DefView', 211:'SysListView32'}.get(h, base(h))
        # A child WorkerW is a valid desktop host, but file Explorer isn't.
        self.assertTrue(self.device._desktop_listview(211))
        self.assertEqual(self.device._view_at(211), 211)


if __name__ == '__main__':
    unittest.main()
