"""Qt-free regression checks for context UI and hover movement.

These invoke selected actual methods from app.py, without inventing Qt mouse
messages, to keep the interaction policies testable on non-Windows CI.
"""
import ast
from pathlib import Path
import types
import unittest
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'app.py'
TEXT = SRC.read_text(encoding='utf-8')
TREE = ast.parse(TEXT)


def method(cls, name, scope=None):
    node = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == cls)
    member = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == name)
    isolated = ast.Module(body=[member], type_ignores=[])
    ast.fix_missing_locations(isolated)
    env = dict(scope or {})
    exec(compile(isolated, str(SRC), 'exec'), env)
    return env[name]


class Point:
    def __init__(self, y): self._y = y
    def y(self): return self._y


class Rect:
    def __init__(self, bottom): self._bottom = bottom
    def bottom(self): return self._bottom
    def isValid(self): return True


class Item:
    def __init__(self, bottom, hidden=False): self.bottom = bottom; self.hidden = hidden
    def isHidden(self): return self.hidden


class List:
    def __init__(self, bottoms): self.items = [Item(b) for b in bottoms]
    def itemAt(self, position):
        last = -1
        for item in self.items:
            if not item.isHidden() and last < position.y() <= item.bottom:
                return item
            last = item.bottom
        return None
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, index): return self.items[index]
    def visualItemRect(self, item): return Rect(item.bottom)


class UiRegressions(unittest.TestCase):
    def test_page_background_only_below_last_rendered_row(self):
        fn = method('Launcher', 'page_empty_area_can_open_context')
        context = types.SimpleNamespace(selection=None, stack=[],
                                        search=types.SimpleNamespace(text=lambda: ''),
                                        list=List([35, 70, 105]))
        self.assertFalse(fn(context, Point(5)))    # first row
        self.assertFalse(fn(context, Point(70)))   # on a row's bottom edge
        self.assertFalse(fn(context, Point(105)))  # last row
        self.assertTrue(fn(context, Point(106)))   # genuine blank beneath last row
        self.assertTrue(fn(context, Point(300)))
        context.stack = [{'item_id': 'nested'}]
        self.assertFalse(fn(context, Point(300)))
        context.stack = []
        context.search.text = lambda: 'filter'
        self.assertFalse(fn(context, Point(300)))

    def test_no_background_menu_for_spaces_near_tabs_header_or_reorder(self):
        # QWidget contextMenuEvent must not call the root page properties.
        node = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'contextMenuEvent')
        src = ast.get_source_segment(TEXT, fn)
        self.assertNotIn('show_launch_context_menu', src)
        self.assertIn('event.accept()', src)

    def test_mouse_enter_switch_waits_only_while_heading_to_cascade(self):
        # Root item-to-item movement uses 250ms; diagonal travel toward the
        # already open cascade retains the 650ms safety window.
        class Qt:
            class MouseButton:
                LeftButton = 1
        class QApplication:
            @staticmethod
            def mouseButtons(): return 0
        fn = method('Launcher', 'hover', {'Qt': Qt, 'QApplication': QApplication})
        owner = object()
        other = object()
        m = types.SimpleNamespace(isVisible=lambda: True, owner_item=owner)
        widget = types.SimpleNamespace(selection=None, list=types.SimpleNamespace(
            order_dragging=False, setCurrentItem=Mock()), menu=m,
            pending_menu_item=None, hover_timer=Mock(),
            data={'launch_hover_delay_ms': 250},
            main_hover_heading_to_cascade=lambda: False)
        fn(widget, other, 0)
        widget.list.setCurrentItem.assert_not_called()
        widget.hover_timer.start.assert_called_once_with(250)
        self.assertIs(widget.pending_menu_item, other)
        widget.hover_timer.reset_mock()
        widget.main_hover_heading_to_cascade = lambda: True
        fn(widget, other, 0)
        widget.hover_timer.start.assert_called_once_with(650)
        widget.hover_timer.reset_mock()
        fn(widget, owner, 0)
        widget.list.setCurrentItem.assert_called_once_with(owner)
        widget.hover_timer.start.assert_called_once_with(250)

    def test_mouse_motion_direction_and_expiry(self):
        # In a Qt-free unit test, QPoint-like objects supply x() and y().
        # Rapid diagonal right movement protects the open submenu, while
        # vertical scanning and stale motion do not delay row switching.
        record = method('Launcher', 'record_main_hover_motion', {'time': __import__('time')})
        heading = method('Launcher', 'main_hover_heading_to_cascade')
        class Pos:
            def __init__(self, x, y): self.x_value=x; self.y_value=y
            def x(self): return self.x_value
            def y(self): return self.y_value
        w = types.SimpleNamespace(_main_hover_motion=[])
        record(w, Pos(20, 10), 1.00)
        record(w, Pos(50, 17), 1.05)
        self.assertTrue(heading(w))  # Mostly rightward
        record(w, Pos(50, 45), 1.35)
        record(w, Pos(51, 75), 1.40)
        self.assertFalse(heading(w))  # Mostly vertical; old samples expired
        record(w, Pos(5, 80), 1.50)
        self.assertFalse(heading(w))  # Moving left

    def test_submenu_hover_does_not_close_child_immediately(self):
        cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
        for name in ('mouseMoveEvent', '_scroll_hover'):
            fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
            src = ast.get_source_segment(TEXT, fn)
            self.assertNotIn('self.child.close()', src, name)

    def test_menu_context_popup_freezes_auto_dismiss(self):
        fn = method('Launcher', 'check_hover_menus')
        c = types.SimpleNamespace(_launch_context_menu=types.SimpleNamespace(
            isVisible=lambda: True))
        self.assertIsNone(fn(c))


if __name__ == '__main__':
    unittest.main()
