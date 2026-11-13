"""FRB List: fast Remote cadence with the original scrollbar/edge-follow split.

Runs without PySide6; the original Windows GUI feel still needs hands-on review.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from list_wheel_parity import (
    LIST_WHEEL_MATCH_REMOTE, LIST_WHEEL_HYBRID_ENABLED,
    LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH,
    consume_remote_like_wheel, plan_hybrid_scroll)


def test_scroll_plan_keeps_current_on_all_in_range_movement():
    assert plan_hybrid_scroll(100, 0, 1000, -3, 35) == (205, 0)
    assert plan_hybrid_scroll(100, 0, 1000, 2, 35) == (30, 0)
    assert plan_hybrid_scroll(100, 0, 1000, 0, 35) == (100, 0)


def test_scroll_plan_passes_only_unconsumed_wheel_notches_at_edges():
    # Remaining 20px before edge: first notch moves scrollbar; next two follow.
    assert plan_hybrid_scroll(980, 0, 1000, -3, 35) == (1000, -2)
    assert plan_hybrid_scroll(15, 0, 1000, 4, 35) == (0, 3)
    assert plan_hybrid_scroll(1000, 0, 1000, -3, 35) == (1000, -3)
    assert plan_hybrid_scroll(0, 0, 1000, 2, 35) == (0, 2)
    # All rows fit, scrollbar has no travel.
    assert plan_hybrid_scroll(0, 0, 0, -2, 35) == (0, -2)


def test_scroll_plan_no_wrap_and_variable_pixel_step():
    assert plan_hybrid_scroll(50, 0, 100, -2, 50) == (100, -1)
    assert plan_hybrid_scroll(50, 0, 100, -2, 20) == (90, 0)
    assert plan_hybrid_scroll(100, 0, 100, -5, 35) == (100, -5)


SOURCE = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
module = ast.parse(SOURCE)
view_class = next(n for n in module.body if isinstance(n, ast.ClassDef)
                  and n.name == 'ExpandedLauncherView')
method = next(n for n in view_class.body if isinstance(n, ast.FunctionDef)
              and n.name == 'wheel_middle_fast_hybrid')
namespace = dict(
    Qt=NS(KeyboardModifier=NS(NoModifier=0), MouseButton=NS(NoButton=0)),
    QApplication=NS(mouseButtons=lambda: 0),
    QAbstractItemView=NS(State=NS(EditingState='editing')),
    consume_remote_like_wheel=consume_remote_like_wheel,
    plan_hybrid_scroll=plan_hybrid_scroll,
    LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH=LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH,
)
exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
             '<fast_hybrid_method>', 'exec'), namespace)


class Bar:
    def __init__(self, value=150, minimum=0, maximum=1000, single_step=35):
        self.pos = value
        self.low = minimum
        self.high = maximum
        self.step = single_step
        self.set_calls = []
    def value(self): return self.pos
    def minimum(self): return self.low
    def maximum(self): return self.high
    def singleStep(self): return self.step
    def setValue(self, value):
        self.pos = max(self.low, min(self.high, value))
        self.set_calls.append(self.pos)


class Tree:
    def __init__(self, bar, count=100):
        self.bar = bar
        self.count = count
        self.editing = False
    def verticalScrollBar(self): return self.bar
    def topLevelItemCount(self): return self.count
    def state(self): return 'editing' if self.editing else 'ready'


class Wheel:
    def __init__(self, angle=-120, pixel=0, modifiers=0):
        self.angle, self.pixel, self.mods = angle, pixel, modifiers
    def angleDelta(self): return NS(y=lambda: self.angle)
    def pixelDelta(self): return NS(y=lambda: self.pixel)
    def modifiers(self): return self.mods


class Demo:
    wheel_middle_fast_hybrid = namespace['wheel_middle_fast_hybrid']
    def __init__(self, pos=150, max_pos=1000, count=100):
        self.middle = NS(tree=Tree(Bar(pos, 0, max_pos), count))
        self._workspace_mode = 'files'
        self._middle_parity_angle_remainder = 0
        self._middle_parity_pixel_remainder = 0
        self.follow_calls = []
    def isVisible(self): return True
    def wheel_middle_at_edge(self, event, before, after, movement_override=None):
        self.follow_calls.append((before, after, movement_override))


def test_active_hybrid_uses_remote_notches_but_not_current_during_scroll():
    assert LIST_WHEEL_MATCH_REMOTE is True
    assert LIST_WHEEL_HYBRID_ENABLED is True
    demo = Demo()
    assert demo.wheel_middle_fast_hybrid(Wheel(-120))
    assert demo.middle.tree.bar.pos == 185
    assert demo.follow_calls == [(150, 185, None)]
    assert demo.wheel_middle_fast_hybrid(Wheel(-480))
    assert demo.middle.tree.bar.pos == 325
    assert demo.follow_calls[-1] == (185, 325, None)
    # One scrollbar assignment per event, regardless of how fast we spin.
    assert demo.middle.tree.bar.set_calls == [185, 325]


def test_at_edge_follows_one_row_per_notch_and_never_wraps_scrollbar():
    demo = Demo(pos=1000)
    assert demo.wheel_middle_fast_hybrid(Wheel(-120))
    assert demo.middle.tree.bar.set_calls == []
    assert demo.follow_calls == [(1000, 1000, 1)]
    assert demo.wheel_middle_fast_hybrid(Wheel(-240))
    assert demo.follow_calls[-1] == (1000, 1000, 2)
    assert demo.wheel_middle_fast_hybrid(Wheel(120))
    assert demo.middle.tree.bar.pos == 965
    assert demo.follow_calls[-1] == (1000, 965, None)


def test_multi_notch_hits_edge_and_transfers_only_unconsumed_input():
    demo = Demo(pos=980)
    assert demo.wheel_middle_fast_hybrid(Wheel(-360))
    assert demo.middle.tree.bar.pos == 1000
    assert demo.follow_calls == [(980, 1000, None), (1000, 1000, 2)]


def test_no_scrollbar_exactly_reuses_edge_follow_handler():
    demo = Demo(pos=0, max_pos=0)
    assert demo.wheel_middle_fast_hybrid(Wheel(-120))
    assert demo.follow_calls == [(0, 0, 1)]
    assert demo.middle.tree.bar.set_calls == []


def test_partial_wheel_and_reverse_do_not_duplicate_events():
    demo = Demo()
    for _ in range(3):
        assert demo.wheel_middle_fast_hybrid(Wheel(angle=0, pixel=-10))
    assert demo.middle.tree.bar.pos == 150
    assert demo.wheel_middle_fast_hybrid(Wheel(angle=0, pixel=-6))
    assert demo.middle.tree.bar.pos == 185
    assert demo.wheel_middle_fast_hybrid(Wheel(120))
    assert demo.middle.tree.bar.pos == 150
    assert len(demo.middle.tree.bar.set_calls) == 2


def test_editing_modifiers_other_workspace_and_empty_list_fallback_to_qt():
    demo = Demo()
    assert not demo.wheel_middle_fast_hybrid(Wheel(modifiers=1))
    demo.middle.tree.editing = True
    assert not demo.wheel_middle_fast_hybrid(Wheel())
    demo.middle.tree.editing = False
    demo._workspace_mode = 'browser'
    assert not demo.wheel_middle_fast_hybrid(Wheel())
    demo._workspace_mode = 'files'
    demo.middle.tree.count = 0
    assert not demo.wheel_middle_fast_hybrid(Wheel())
    assert demo.middle.tree.bar.set_calls == []


def test_original_wan_decision_and_rollback_mode_retained():
    assert 'self.wheel_middle_at_edge(event, before, bar.value())' in SOURCE
    assert 'self.wheel_middle_at_edge(event, at, at, movement_override=-remaining)' in SOURCE
    assert 'self.middle.tree.remote_parity_wheel_callback = self.wheel_middle_like_remote_button' in SOURCE
    assert 'self.middle.tree.adaptive_wheel_callback = self.wheel_middle_at_edge' in SOURCE
    assert 'if LIST_WHEEL_HYBRID_ENABLED:' in SOURCE
    assert 'self.middle.tree.remote_parity_wheel_callback = self.wheel_middle_fast_hybrid' in SOURCE
    assert 'self.left.tree.adaptive_wheel_callback = self.wheel_files_at_edge' in SOURCE
    # The Remote button's existing wheel processing is NOT modified by this change.
    button = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
    assert 'for _ in range(min(abs(steps), 5)):' in button
