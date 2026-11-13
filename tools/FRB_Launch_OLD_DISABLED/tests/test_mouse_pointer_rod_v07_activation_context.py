"""v0.8 Mouse Pointer Rod: native menu routes belong to central ぐりぐり.

The production adapter is executed against tiny fakes because desktop Qt is
not installed on this headless runner. Windows geometry and popup-grab behavior
must still be verified manually on the user's machine.
"""
from pathlib import Path
import ast
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_direct import direct_files_action
from test_mouse_pointer_rod_direct_v06 import Point, harness


def test_list_blue_double_selects_without_activation_or_os_click():
    launcher, list_tree, exp = harness()
    view = launcher.expanded_view
    view.activate_row = Mock()
    view.context_menu = Mock()
    assert direct_files_action(launcher, (320, 220), 'double', point_type=Point)
    assert list_tree.current is list_tree.item
    assert list_tree.item.selected
    view.activate_row.assert_not_called()
    view.context_menu.assert_not_called()
    assert exp.current is None


def test_list_single_select_does_not_activate_files():
    launcher, list_tree, _ = harness()
    launcher.expanded_view.activate_row = Mock()
    assert direct_files_action(launcher, (320, 220), 'select', point_type=Point)
    launcher.expanded_view.activate_row.assert_not_called()


def test_list_right_routes_to_native_context_menu_with_tip_position():
    launcher, list_tree, _ = harness()
    view = launcher.expanded_view
    view.context_menu = Mock()
    assert direct_files_action(launcher, (320, 220), 'context', point_type=Point)
    view.context_menu.assert_called_once()
    args, kwargs = view.context_menu.call_args
    assert args[0] is view.middle
    assert (args[1].x, args[1].y) == (20, 20)
    assert (kwargs['global_pos'].x, kwargs['global_pos'].y) == (320, 220)
    assert list_tree.current is list_tree.item


def test_exp_context_routes_to_existing_exp_menu_signal_path():
    launcher, list_tree, exp = harness()
    panel = launcher.expanded_view.embedded_files_exp
    panel._show_folder_context = Mock()
    assert direct_files_action(launcher, (120, 220), 'context', point_type=Point)
    panel._show_folder_context.assert_called_once()
    point = panel._show_folder_context.call_args.args[0]
    assert (point.x, point.y) == (20, 20)
    launcher.set_files_operating_target.assert_called_once_with('files_exp')
    assert exp.current is exp.index
    assert list_tree.current is None


def test_exp_double_keeps_existing_expand_behavior():
    launcher, _, exp = harness()
    assert direct_files_action(launcher, (120, 220), 'double', point_type=Point)
    assert exp.expansions == ['expand']
    assert direct_files_action(launcher, (120, 220), 'double', point_type=Point)
    assert exp.expansions == ['expand', 'collapse']


def test_right_double_and_blank_cannot_operate_outside_files():
    launcher, _, _ = harness()
    launcher.expanded_view.context_menu = Mock()
    launcher.expanded_view.embedded_files_exp._show_folder_context = Mock()
    assert not direct_files_action(launcher, (800, 800), 'context', point_type=Point)
    assert not direct_files_action(launcher, (800, 800), 'double', point_type=Point)
    launcher.expanded_view._workspace_mode = 'browser'
    assert not direct_files_action(launcher, (320, 220), 'context', point_type=Point)
    assert not direct_files_action(launcher, (320, 220), 'double', point_type=Point)
    launcher.expanded_view.context_menu.assert_not_called()
    launcher.expanded_view.embedded_files_exp._show_folder_context.assert_not_called()


def _actual_method(name):
    source = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')
    klass = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef)
                 and n.name == 'MousePointerRodPad')
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef)
                  and n.name == name)
    scope = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), 'mouse_pointer_rod.py', 'exec'), scope)
    return scope[name]


def test_real_blue_pad_context_menu_event_is_inert():
    sent = []
    rod = NS(_enabled=True, _double_pending=True,
             _dispatch_tip_action=lambda name: sent.append(name))
    event = NS(accept=Mock())
    _actual_method('contextMenuEvent')(rod, event)
    assert sent == []
    assert not rod._double_pending
    event.accept.assert_called_once()
    rod._enabled = False
    _actual_method('contextMenuEvent')(rod, event)
    assert sent == []


def test_rod_pad_height_and_no_system_cursor_hijack():
    pad = (ROOT / 'src' / 'mouse_pointer_rod.py').read_text('utf-8')
    remote = (ROOT / 'src' / 'launch_remote.py').read_text('utf-8')
    adapter = (ROOT / 'src' / 'mouse_pointer_rod_direct.py').read_text('utf-8')
    assert 'PAD_HEIGHT = 144' in pad
    assert "self._dispatch_tip_action('context')" not in pad
    assert "self._dispatch_tip_action('double' if self._double_pending else 'select')" in pad
    assert "QTimer.singleShot(0, self._clamp_pointer_rod_to_screen)" in remote
    for text in (pad, adapter):
        for api in ('SetCursorPos', 'SendInput(', 'QCursor.setPos(', 'QTest.mouseClick('):
            assert api not in text
