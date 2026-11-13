"""Regression: physical wheel in a cascade column follows that column's row.

Qt-free function tests: PySide6 GUI is verified on Windows separately.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from wheel_adaptive import wheel_steps
from navigation_wrap import move_tree_selection

SOURCE = (ROOT / 'src' / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
MENU = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == 'CascadeMenu')
APP_MENU = next(x for x in TREE.body if isinstance(x, ast.ClassDef) and x.name == 'AppCascadeMenu')


def method(cls, name, **kwargs):
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    copied = ast.FunctionDef(name=node.name, args=node.args, body=node.body,
                             decorator_list=[], returns=node.returns, type_comment=None)
    namespace = dict(kwargs)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[copied], type_ignores=[])),
                 '<app.py method>', 'exec'), namespace)
    return namespace[name]


class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x(), self.y()) == (other.x(), other.y())


QT = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                     MouseButton=SimpleNamespace(NoButton=0))
POINTER = Point(40, 40)
CURSOR = SimpleNamespace(pos=Mock(return_value=POINTER), setPos=Mock())
APPLICATION = SimpleNamespace(mouseButtons=Mock(return_value=0))


def base_menu(*, pointer_auto=True, remote_root=False):
    surface = Mock()
    surface.mapFromGlobal.return_value = Point(12, 22)
    surface.rect.return_value.contains.return_value = True
    surface.width.return_value = 250
    surface.height.return_value = 200
    menu = Mock()
    menu.launcher.pointer_warp_enabled = pointer_auto
    menu.launcher._remote_page_menu = menu if remote_root else None
    menu._wheel_column_viewport.return_value = menu
    menu.mapFromGlobal = surface.mapFromGlobal
    menu.rect = surface.rect
    menu.width = surface.width
    menu.height = surface.height
    menu.mapToGlobal.side_effect = lambda pt: pt
    menu.scroll_tree = None
    menu.tree = None
    menu.filter_action = Mock()
    menu.isVisible.return_value = True
    menu.actionAt.return_value = Mock()
    menu._column_wheel_remainder = 0
    menu.activeAction.return_value = Mock()
    return menu, surface


def event(*, amount=-120, modifiers=0):
    return SimpleNamespace(angleDelta=lambda: SimpleNamespace(y=lambda: amount),
                           pixelDelta=lambda: SimpleNamespace(y=lambda: 0),
                           modifiers=lambda: modifiers, accept=Mock())


WHEEL = method(MENU, '_wheel_column_browse', Qt=QT,
               QApplication=APPLICATION, QCursor=CURSOR,
               wheel_steps=wheel_steps, move_tree_selection=move_tree_selection)


def test_wheel_browses_one_column_and_schedules_pointer_follow():
    menu, _ = base_menu()
    wheel = event()
    assert WHEEL(menu, wheel) is True
    menu._move_filtered_selection.assert_called_once_with(1)
    menu._schedule_column_wheel_follow.assert_called_once_with(POINTER, menu.activeAction.return_value)
    wheel.accept.assert_called_once()
    menu.launcher._remote_page_wheel_expand.assert_not_called()


def test_remote_root_previews_one_child_but_physical_child_wheel_does_not_touch_root():
    root, _ = base_menu(remote_root=True)
    assert WHEEL(root, event()) is True
    root.launcher._remote_page_wheel_expand.assert_called_once_with(root)
    child, _ = base_menu()
    child.launcher = root.launcher
    assert WHEEL(child, event()) is True
    root.launcher._remote_page_wheel_expand.assert_called_once_with(root)
    child._move_filtered_selection.assert_called_once_with(1)


def test_cursor_auto_off_and_modifier_do_not_intercept_wheel():
    menu, _ = base_menu(pointer_auto=False)
    assert WHEEL(menu, event()) is False
    menu._move_filtered_selection.assert_not_called()
    menu.launcher.pointer_warp_enabled = True
    assert WHEEL(menu, event(modifiers=1)) is False
    menu._move_filtered_selection.assert_not_called()


def test_scroll_tree_and_app_tree_take_event_from_viewport():
    menu, surface = base_menu()
    menu.scroll_tree = Mock()
    menu._wheel_column_viewport.return_value = surface
    assert WHEEL(menu, event()) is True
    menu._move_filtered_selection.assert_called_once_with(1)
    app, surface = base_menu()
    app.tree = Mock()
    app.tree.topLevelItemCount.return_value = 0
    app._wheel_column_viewport.return_value = app.tree.viewport.return_value
    app.tree.viewport.return_value.mapFromGlobal.return_value = Point(12, 22)
    app.tree.viewport.return_value.rect.return_value.contains.return_value = True
    assert WHEEL(app, event()) is True
    app.tree.topLevelItemCount.assert_called()  # delegates to move_tree_selection


def test_hides_selection_on_search_bar_and_on_pointer_outside_column():
    menu, surface = base_menu()
    menu.actionAt.return_value = menu.filter_action
    assert WHEEL(menu, event()) is False
    menu.actionAt.return_value = Mock()
    menu.rect.return_value.contains.return_value = False
    assert WHEEL(menu, event()) is False


def test_follow_warp_moves_only_vertical_inside_same_column():
    global POINTER
    menu, surface = base_menu()
    action = menu.activeAction.return_value
    menu._column_wheel_follow_pending = (POINTER, action)
    menu._column_wheel_follow_scheduled = True
    menu.actionGeometry.return_value = SimpleNamespace(left=lambda: 0,
                top=lambda: 50, width=lambda: 250, height=lambda: 24)
    fn = method(MENU, '_follow_column_wheel_pointer', Qt=QT,
                QApplication=APPLICATION, QCursor=CURSOR,
                QPoint=Point, cursor_target=__import__('bookmark_cursor_follow').cursor_target)
    CURSOR.setPos.reset_mock()
    fn(menu)
    CURSOR.setPos.assert_called_once()
    dst = CURSOR.setPos.call_args.args[0]
    assert dst.x() == 12 and dst.y() == 61
    assert menu._column_wheel_follow_pending is None


def test_follow_does_not_jump_when_user_moved_mouse():
    menu, surface = base_menu()
    menu._column_wheel_follow_pending = (Point(12, 10), menu.activeAction.return_value)
    fn = method(MENU, '_follow_column_wheel_pointer', Qt=QT,
                QApplication=APPLICATION, QCursor=CURSOR,
                QPoint=Point, cursor_target=__import__('bookmark_cursor_follow').cursor_target)
    CURSOR.setPos.reset_mock()
    fn(menu)
    CURSOR.setPos.assert_not_called()


def test_hooked_events_and_settings_are_present():
    assert 'def wheelEvent(self, event):' in SOURCE[SOURCE.index('class CascadeMenu('):SOURCE.index('class AppCascadeMenu(')]
    assert 'self._wheel_column_browse(event)' in SOURCE
    assert "if self._wheel_column_browse(event):" in SOURCE[SOURCE.index('class AppCascadeMenu('):SOURCE.index('class FileIndexSignals(')]
    assert "self.pointer_warp_enabled = not self.vdi_no_cursor_warp" in SOURCE
