"""Remote Citrix/VDI mode is opt-in; existing desktop warp stays unchanged."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / 'src' / name).read_text(encoding='utf-8')


def method(name, cls, func):
    tree = ast.parse(source(name))
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in owner.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func)
    return ast.get_source_segment(source(name), node)


def test_settings_are_opt_in_and_persistent():
    constructor = method('app.py', 'Launcher', '__init__')
    assert "'vdi_no_cursor_warp', 'false'" in constructor
    assert 'self.pointer_warp_enabled = not self.vdi_no_cursor_warp' in constructor
    handler = method('app.py', 'Launcher', 'set_vdi_no_cursor_warp')
    assert "setValue('vdi_no_cursor_warp', self.vdi_no_cursor_warp)" in handler
    assert 'view.cancel_bookmark_pointer_follow()' in handler
    assert 'self._classic_wheel_follow_pending = None' in handler
    assert 'Citrix / VDI互換：マウスポインター自動移動OFF' in constructor


def test_all_warp_locations_are_guarded_by_vdi_mode():
    for filename, cls, functions in (
        ('app.py', 'Launcher', ('follow_classic_wheel_pointer',)),
        ('expanded_view.py', 'ExpandedLauncherView', (
            '_finish_zone_jump', 'follow_middle_pointer',
            'follow_middle_back_pointer', 'follow_first_files_pointer',
            'follow_bookmark_pointer', 'follow_root_pointer')),
        ('page_tab_focus.py', 'FocusPageTabBar', ('follow_wheel_tab_pointer',)),
    ):
        for func in functions:
            body = method(filename, cls, func)
            assert 'QCursor.setPos(destination)' in body, (filename, func)
            assert 'pointer_warp_enabled' in body, (filename, func)
    # Both favorites and search history must check at DEFERRED execution time.
    assert "'pointer_warp_enabled', True) and" in method(
        'expanded_view.py', 'ExpandedLauncherView', 'wheel_directory_favorite_history')
    assert 'self.pointer_warp_enabled and' in method(
        'app.py', 'Launcher', 'wheel_search_history')


def test_middle_follows_selection_when_client_pointer_does_not_move():
    body = method('expanded_view.py', 'ExpandedLauncherView', 'wheel_middle_at_edge')
    assert 'self._middle_vdi_anchor_pos == cursor_global' in body
    assert 'tree.currentItem() if following' in body
    assert 'self._middle_vdi_anchor_pos = cursor_global' in body
    assert 'self._middle_vdi_anchor_pos = None' in body


def test_qtab_normal_mode_still_has_warp():
    app = method('app.py', 'Launcher', '__init__')
    assert 'self.tabs._pointer_warp_enabled = lambda: self.pointer_warp_enabled' in app
    tab = method('page_tab_focus.py', 'FocusPageTabBar', 'follow_wheel_tab_pointer')
    assert '(not callable(allowed) or allowed())' in tab


def test_vdi_middle_edge_advances_without_any_cursor_warp():
    # Reuse the Qt-free fake view from the existing WAN regression suite.
    from types import SimpleNamespace
    from test_wan_middle_files_20261025 import Demo, Event, Mouse, World
    Mouse.current = __import__('test_wan_middle_files_20261025').Coord(20, 20)
    Mouse.moves = []
    World.calls = []
    demo = Demo(hovered=1)
    demo.launcher = SimpleNamespace(pointer_warp_enabled=False)
    demo._middle_vdi_anchor_pos = None
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert demo.middle.tree.current == 'item-2'
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert demo.middle.tree.current == 'item-3'
    assert demo.wheel_middle_at_edge(Event(), 0, 0)
    assert demo.middle.tree.current == 'item-4'
    assert Mouse.moves == []
    assert World.calls == []
    assert demo.events == []
