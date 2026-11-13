"""v0.6 contract: directly select List/Exp with no system mouse injection.

Qt-free behavioral fakes deliberately exercise the real routing source. A
separate Windows/PySide6 smoke test is required for actual widget geometry.
"""
from __future__ import annotations

from pathlib import Path
import ast
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_direct import direct_files_action


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, width=120, height=120):
        self.width = width
        self.height = height

    def contains(self, point):
        return 0 <= point.x < self.width and 0 <= point.y < self.height


class Viewport:
    def __init__(self, x, y, visible=True):
        self.x, self.y, self.visible = x, y, visible
        self.update = Mock()

    def isVisible(self):
        return self.visible

    def rect(self):
        return Rect()

    def mapFromGlobal(self, point):
        return Point(point.x - self.x, point.y - self.y)


class Item:
    def __init__(self):
        self.selected = False

    def setSelected(self, selected):
        self.selected = selected


class Index:
    def __init__(self, valid=True):
        self.valid = valid

    def isValid(self):
        return self.valid


class ListTree:
    def __init__(self):
        self.viewport_widget = Viewport(300, 200)
        self.visible = True
        self.item = Item()
        self.deliberate_blank_selection = True
        self.select_count = 0
        self.current = None

    def isVisible(self):
        return self.visible

    def viewport(self):
        return self.viewport_widget

    def itemAt(self, point):
        return self.item if 10 <= point.y < 50 else None

    def clearSelection(self):
        self.select_count += 1
        self.item.setSelected(False)

    def setCurrentItem(self, item):
        self.current = item


class ExpTree:
    def __init__(self):
        self.viewport_widget = Viewport(100, 200)
        self.visible = True
        self.index = Index()
        self.current = None
        self.expanded = False
        self.has_children = True
        self.expansions = []

    def isVisible(self):
        return self.visible

    def viewport(self):
        return self.viewport_widget

    def indexAt(self, point):
        return self.index if 10 <= point.y < 50 else Index(False)

    def setCurrentIndex(self, index):
        self.current = index

    def isExpanded(self, index):
        return self.expanded

    def model(self):
        return NS(hasChildren=lambda index: self.has_children)

    def expand(self, index):
        self.expanded = True
        self.expansions.append('expand')

    def collapse(self, index):
        self.expanded = False
        self.expansions.append('collapse')


def harness():
    list_tree, exp_tree = ListTree(), ExpTree()
    view = NS(isVisible=lambda: True, _workspace_mode='files',
              middle=NS(tree=list_tree), embedded_files_exp=NS(tree=exp_tree))
    launcher = NS(expanded_view=view, set_files_operating_target=Mock())
    return launcher, list_tree, exp_tree


def test_list_left_selects_row_and_claims_logical_target():
    launcher, tree, _ = harness()
    assert direct_files_action(launcher, (320, 220), point_type=Point)
    launcher.set_files_operating_target.assert_called_once_with('directory')
    assert tree.current is tree.item and tree.item.selected
    assert tree.select_count == 1 and not tree.deliberate_blank_selection
    tree.viewport().update.assert_called_once()


def test_blank_area_does_not_select_or_fallback():
    launcher, tree, exp = harness()
    assert not direct_files_action(launcher, (320, 280), point_type=Point)
    assert not direct_files_action(launcher, (10, 10), point_type=Point)
    assert tree.current is None and exp.current is None
    launcher.set_files_operating_target.assert_not_called()


def test_exp_select_then_double_toggle_and_keep_target():
    launcher, tree, exp = harness()
    assert direct_files_action(launcher, (120, 220), point_type=Point)
    assert exp.current is exp.index
    assert not exp.expanded
    assert direct_files_action(launcher, (120, 220), 'toggle', point_type=Point)
    assert exp.expanded
    assert direct_files_action(launcher, (120, 220), 'toggle', point_type=Point)
    assert not exp.expanded
    assert exp.expansions == ['expand', 'collapse']
    assert launcher.set_files_operating_target.call_count == 3
    assert tree.current is None


def test_exp_leaf_still_selectable_but_cannot_expand():
    launcher, tree, exp = harness()
    exp.has_children = False
    assert direct_files_action(launcher, (120, 220), 'toggle', point_type=Point)
    assert exp.current is exp.index
    assert exp.expansions == []


def test_no_routing_into_browser_compact_hidden_or_unknown_actions():
    launcher, tree, exp = harness()
    view = launcher.expanded_view
    view._workspace_mode = 'browser'
    assert not direct_files_action(launcher, (320, 220), point_type=Point)
    view._workspace_mode = 'files'
    view.isVisible = lambda: False
    assert not direct_files_action(launcher, (320, 220), point_type=Point)
    view.isVisible = lambda: True
    tree.visible = False
    assert not direct_files_action(launcher, (320, 220), point_type=Point)
    exp.viewport_widget.visible = False
    assert not direct_files_action(launcher, (120, 220), point_type=Point)
    assert not direct_files_action(launcher, (120, 220), 'right', point_type=Point)
    launcher.set_files_operating_target.assert_not_called()


def test_no_system_mouse_cursor_or_event_injection_in_adapter():
    source = (ROOT / 'src' / 'mouse_pointer_rod_direct.py').read_text('utf-8')
    for forbidden in ('SetCursorPos', 'SendInput(', 'QCursor.setPos(',
                      'QTest.mouseClick(', 'postEvent(', 'sendEvent('):
        assert forbidden not in source
    assert 'list_tree.setCurrentItem(item)' in source
    assert 'exp_tree.setCurrentIndex(index)' in source
    assert 'exp_tree.expand(index)' in source
    assert 'exp_tree.collapse(index)' in source


def _actual_method(name, globals_):
    source = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')
    klass = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef)
                 and n.name == 'MousePointerRodPad')
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef)
                  and n.name == name)
    scope = dict(globals_)
    exec(compile(ast.Module(body=[method], type_ignores=[]), 'rod', 'exec'), scope)
    return scope[name]


def test_real_pad_methods_dispatch_first_click_and_double_toggle_only():
    # Invoke the real event-method bodies, not copies of the desired behavior.
    class MouseButtons:
        LeftButton = object()
        RightButton = object()
    class Qt:
        MouseButton = MouseButtons
    actions = []
    class Everywhere:
        def contains(self, point):
            return True
    rod = NS(_enabled=True, _double_pending=False, _left_pressed=False,
             _wheel_during_press=False, _wheel_pad=None,
             rect=lambda: Everywhere(),
             _dispatch_tip_action=lambda action: actions.append(action))
    evt = lambda button: NS(button=lambda: button, accept=Mock(),
                            position=lambda: NS(toPoint=lambda: (10, 10)))
    release = _actual_method('mouseReleaseEvent', {'Qt': Qt})
    double = _actual_method('mouseDoubleClickEvent', {'Qt': Qt})
    release(rod, evt(MouseButtons.LeftButton))
    double(rod, evt(MouseButtons.LeftButton))
    release(rod, evt(MouseButtons.LeftButton))
    release(rod, evt(MouseButtons.RightButton))
    assert actions == ['select', 'double']
    assert not rod._double_pending
    rod._enabled = False
    release(rod, evt(MouseButtons.LeftButton))
    assert actions == ['select', 'double']
