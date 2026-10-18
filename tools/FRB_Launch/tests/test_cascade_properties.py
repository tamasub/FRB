"""Cascade right-click -> existing Studio item editor, without a Qt dependency."""
import ast
from pathlib import Path
import types
import unittest
from unittest.mock import Mock

from cascade_properties import authored_cascade_row

SOURCE = Path(__file__).resolve().parents[1] / 'app.py'


def isolated_method(name):
    """Compile the actual CascadeMenu method, not a reimplementation."""
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    source = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(source)
    class EventType:
        MouseButtonPress = 1
        MouseButtonRelease = 2
        MouseButtonDblClick = 3
        ContextMenu = 4
    class MouseButton:
        RightButton = 8
    qt = types.SimpleNamespace(MouseButton=MouseButton,
                               ItemDataRole=types.SimpleNamespace(UserRole=32))
    queued = []
    timer = types.SimpleNamespace(singleShot=lambda delay, callback: queued.append(callback))
    ns = {'QEvent': types.SimpleNamespace(Type=EventType), 'Qt': qt, 'QTimer': timer}
    exec(compile(source, str(SOURCE), 'exec'), ns)
    return ns[name], queued, EventType


class Event:
    def __init__(self, kind, right=True):
        self.kind = kind
        self.right = right
        self.accepted = False
    def type(self): return self.kind
    def button(self): return 8 if self.right else 1
    def globalPosition(self): return types.SimpleNamespace(toPoint=lambda: (17, 29))
    def accept(self): self.accepted = True


class ContextSelectionTests(unittest.TestCase):
    def setUp(self):
        self.authored = [{'item_id': 'settings', 'page_id': 'windows', 'title': '設定'},
                         {'item_id': 'folder', 'page_id': 'work', 'title': 'Files'}]

    def test_authored_category_and_command_are_editable(self):
        self.assertEqual(authored_cascade_row({'item_id': 'settings'}, self.authored), self.authored[0])
        self.assertEqual(authored_cascade_row({'item_id': 'folder', 'item_kind': 'directory'}, self.authored), self.authored[1])

    def test_generated_items_are_not_editable(self):
        for row in (None, {}, {'item_id': 'C:\\docs\\a.py'},
                    {'item_id': '__file_index_C:\\docs\\a.py'},
                    {'item_id': '__browser_bookmark_1'}, {'item_id': 99}):
            with self.subTest(row=row):
                self.assertIsNone(authored_cascade_row(row, self.authored))

    def test_hit_test_short_menu_reads_clicked_action(self):
        fn, _, _ = isolated_method('_right_click_row')
        action = types.SimpleNamespace(data=lambda: self.authored[1])
        launcher = types.SimpleNamespace(data={'items': self.authored})
        obj = types.SimpleNamespace(launcher=launcher, scroll_tree=None, tree=None)
        obj.actionAt = lambda pos: action if pos == (12, 34) else None
        obj._authored_context_row = lambda row: authored_cascade_row(row, self.authored)
        event = types.SimpleNamespace(position=lambda: types.SimpleNamespace(
            toPoint=lambda: (12, 34)))
        self.assertEqual(fn(obj, event, obj), self.authored[1])

    def test_hit_test_long_scroll_uses_viewport_row_not_selection(self):
        fn, _, _ = isolated_method('_right_click_row')
        item = types.SimpleNamespace()
        action = types.SimpleNamespace(data=lambda: self.authored[0])
        viewport = object()
        scroll = types.SimpleNamespace(viewport=lambda: viewport, itemAt=lambda p: item)
        obj = types.SimpleNamespace(scroll_tree=scroll, tree=None)
        obj._scroll_item_action = lambda it: action if it is item else None
        obj._authored_context_row = lambda row: authored_cascade_row(row, self.authored)
        event = types.SimpleNamespace(position=lambda: types.SimpleNamespace(toPoint=lambda: (5, 6)))
        self.assertEqual(fn(obj, event, viewport), self.authored[0])

    def test_hit_test_installed_app_list_ignores_virtual_row(self):
        fn, _, _ = isolated_method('_right_click_row')
        item = types.SimpleNamespace(data=lambda col, role: {'item_id': 'virtual.exe'})
        viewport = object()
        tree = types.SimpleNamespace(viewport=lambda: viewport, itemAt=lambda p: item)
        obj = types.SimpleNamespace(scroll_tree=None, tree=tree)
        obj._authored_context_row = lambda row: authored_cascade_row(row, self.authored)
        event = types.SimpleNamespace(position=lambda: types.SimpleNamespace(toPoint=lambda: (2, 3)))
        self.assertIsNone(fn(obj, event, viewport))

    def test_accurate_release_routes_to_existing_context_menu(self):
        fn, queued, kind = isolated_method('_handle_right_click_properties')
        row = self.authored[0]
        obj = types.SimpleNamespace(_right_context_row=None, hover_timer=Mock())
        obj._right_click_row = lambda evt, src: row
        opened = []
        obj._open_context_properties = lambda r, pos: opened.append((r, pos))
        press, release = Event(kind.MouseButtonPress), Event(kind.MouseButtonRelease)
        self.assertTrue(fn(obj, press, obj))
        self.assertEqual(opened, [])
        self.assertTrue(fn(obj, release, obj))
        self.assertEqual(len(queued), 1)
        queued.pop(0)()
        self.assertEqual(opened, [(row, (17, 29))])
        self.assertTrue(press.accepted and release.accepted)

    def test_release_on_different_row_does_not_open(self):
        fn, queued, kind = isolated_method('_handle_right_click_properties')
        first, second = self.authored
        obj = types.SimpleNamespace(_right_context_row=None, _open_context_properties=Mock(), hover_timer=Mock())
        obj._right_click_row = lambda evt, src: first
        fn(obj, Event(kind.MouseButtonPress), obj)
        obj._right_click_row = lambda evt, src: second
        fn(obj, Event(kind.MouseButtonRelease), obj)
        self.assertFalse(queued)
        obj._open_context_properties.assert_not_called()

    def test_generated_entry_does_not_open(self):
        fn, queued, kind = isolated_method('_handle_right_click_properties')
        obj = types.SimpleNamespace(_right_context_row=None, _open_context_properties=Mock(), hover_timer=Mock())
        obj._right_click_row = lambda evt, src: None
        fn(obj, Event(kind.MouseButtonPress), obj)
        fn(obj, Event(kind.MouseButtonRelease), obj)
        self.assertFalse(queued)

    def test_no_properties_for_right_double_click(self):
        fn, queued, kind = isolated_method('_handle_right_click_properties')
        obj = types.SimpleNamespace(_right_context_row=None, _open_context_properties=Mock(), hover_timer=Mock())
        obj._right_click_row = lambda evt, src: self.authored[0]
        fn(obj, Event(kind.MouseButtonDblClick), obj)
        self.assertFalse(queued)

    def test_existing_main_studio_route_is_reused(self):
        source = SOURCE.read_text(encoding='utf-8')
        self.assertIn('self.launcher.show_launch_context_menu(pos, row, context_parent=self)', source)
        self.assertNotIn('self.launcher.close_cascade_for_main_interaction()',
                         ast.get_source_segment(source, next(n for n in ast.walk(ast.parse(source))
                             if isinstance(n, ast.FunctionDef) and n.name == '_open_context_properties')))
        self.assertIn("args.append('--launch-item-id=' + str(item_id))", source)
        self.assertIn('self._scroll_item_action(', source)
        self.assertIn('source is self.tree.viewport()', source)


if __name__ == '__main__':
    unittest.main()
