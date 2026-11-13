"""Regression: wheel current must not loop back to a stationary mouse after shuriken.

Qt-free tests exercising the actual extracted Launcher settle handler together
with the real existing Files List edge-follow algorithm.  A Windows GUI check
is still required for Qt's asynchronous viewport geometry.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))
from shuriken_scroll_handoff import handoff_current_at_scroll_stop
from test_wan_middle_files_20261025 import Demo, Event, Mouse, World, Coord


def _settle_method():
    code = (ROOT / 'src/app.py').read_text('utf-8')
    node = ast.parse(code)
    owner = next(c for c in node.body if isinstance(c, ast.ClassDef)
                 and any(isinstance(f, ast.FunctionDef) and
                         f.name == 'remote_scroll_files_list_settle' for f in c.body))
    func = next(f for f in owner.body if isinstance(f, ast.FunctionDef) and
                f.name == 'remote_scroll_files_list_settle')
    module = ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[]))
    env = {
        'handoff_current_at_scroll_stop': handoff_current_at_scroll_stop,
        'QItemSelectionModel': SimpleNamespace(SelectionFlag=SimpleNamespace(NoUpdate=17)),
        'QCursor': Mouse,
    }
    exec(compile(module, '<extracted-settle>', 'exec'), env)
    return env['remote_scroll_files_list_settle']


class Item:
    def __init__(self, n): self.n = n
    def isHidden(self): return False
    def isDisabled(self): return False


class Bar:
    def __init__(self, value, maximum=100): self.v, self.max = value, maximum
    def value(self): return self.v
    def minimum(self): return 0
    def maximum(self): return self.max


class Viewport:
    def rect(self): return self
    def contains(self, point): return 0 <= point.x() < 200 and 0 <= point.y() < 200
    def mapFromGlobal(self, point): return point


class Tree:
    def __init__(self, end=100):
        self.items = [Item(n) for n in range(10)]
        self.current = self.items[2]
        self.no_update_flag = None
        self.bar = Bar(end)
        self.screen = Viewport()
        self.deliberate_blank_selection = False
    def verticalScrollBar(self): return self.bar
    def topLevelItemCount(self): return len(self.items)
    def topLevelItem(self, i): return self.items[i]
    def currentItem(self): return self.current
    def setCurrentItem(self, item, col, flag):
        self.current = item
        self.no_update_flag = flag
    def viewport(self): return self.screen


def settled(*, warp_enabled=False, cursor=(20, 120), end=100):
    tree = Tree(end=end)
    view = SimpleNamespace(row_data=lambda item: {'path': str(item.n)},
                           _middle_vdi_anchor_pos=None)
    launcher = SimpleNamespace(expanded_view=view, pointer_warp_enabled=warp_enabled,
                               remote_scroll_files_list_target=lambda: None,
                               auto_shuriken_scroll_files_list_target=lambda: tree)
    Mouse.current = Coord(*cursor)
    _settle_method()(launcher, tree)
    return tree, view


def test_after_shuriken_lands_at_bottom_next_down_not_reanchor_from_hover():
    """Fixed pointer five rows above bottom must NOT steal the logical current."""
    tree, view = settled(warp_enabled=False)
    assert tree.current is tree.items[-1]
    assert tree.no_update_flag == 17
    assert view._middle_vdi_anchor_pos == Mouse.current

    # A separate Qt-free execution of the existing actual wheel edge method.
    demo = Demo(size=10, hovered=4)
    demo.launcher = SimpleNamespace(pointer_warp_enabled=False)
    demo.middle.tree.current = demo.middle.tree.items[-1]
    demo._middle_vdi_anchor_pos = view._middle_vdi_anchor_pos
    demo.middle.tree.bar.hi = 100
    World.buttons = 0
    World.calls.clear()
    Mouse.moves.clear()
    assert demo.wheel_middle_at_edge(Event(degrees=-120), 100, 100)
    assert demo.middle.tree.current is demo.middle.tree.items[-1]
    # Reverse direction first scrolls the viewport (normal hybrid), without
    # rewriting current. If everything fits, edge-follow can go back one row.
    assert demo.wheel_middle_at_edge(Event(degrees=120), 100, 90) is False
    assert demo.middle.tree.current is demo.middle.tree.items[-1]
    # Once a *real* scroll happens, the VDI anchor resets intentionally.
    assert demo._middle_vdi_anchor_pos is None
    demo.middle.tree.bar.lo = 0
    demo.middle.tree.bar.hi = 0
    # A fresh edge session is allowed to start from the actual hovered row.
    assert demo.wheel_middle_at_edge(Event(degrees=120), 0, 0)
    assert demo.middle.tree.current is demo.middle.tree.items[3]
    assert not Mouse.moves
    assert not World.calls


def test_handoff_top_keeps_current_and_up_is_clamped():
    tree, view = settled(warp_enabled=False, end=0)
    assert tree.current is tree.items[0]
    assert view._middle_vdi_anchor_pos == Mouse.current


def test_warp_enabled_does_not_arm_fixed_cursor_follow():
    tree, view = settled(warp_enabled=True)
    assert tree.current is tree.items[-1]
    assert view._middle_vdi_anchor_pos is None


def test_no_anchor_when_cursor_outside_list():
    tree, view = settled(warp_enabled=False, cursor=(250, 120))
    assert tree.current is tree.items[-1]
    assert view._middle_vdi_anchor_pos is None


def test_ordinary_scroll_and_shuriken_engine_preserved():
    source = (ROOT / 'src/expanded_view.py').read_text('utf-8')
    assert 'self.wheel_middle_at_edge(event, before, bar.value())' in source
    assert 'self.wheel_middle_at_edge(event, at, at, movement_override=-remaining)' in source
    assert "auto_handler(steps, source='list')" in source
    assert 'if scroll_before != scroll_after:\n            self._middle_vdi_anchor_pos = None' in source
    assert 'if position != self._middle_vdi_anchor_pos:\n                self._middle_vdi_anchor_pos = None' in source
    assert 'if is_warp_generated_mouse_move((position.x(), position.y()), warp):' in source
