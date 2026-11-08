"""FRB hybrid with wheel-armed shuriken: Qt-free regression suite.

Windows hand-feel/UI timing is separate from these deterministic rules.
"""
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from guriguri_shuriken_auto import WheelShurikenGate, AUTO_SHURIKEN_REVERSE_STOP_NOTCHES
from test_shuriken_scroll_inertia_20261105 import (scroll_pad, FakeScrollBar,
                                                   FakeListTree, FakeSignal)


def test_fast_consecutive_notches_arm_only_once():
    g = WheelShurikenGate()
    assert [g.feed(n, now=t, source='list') for t,n in
            [(1.0,-1), (1.04,-2), (1.08,-2), (1.12,-2)]] == [0,0,-1,0]
    assert g.feed(-3, now=1.16) == 0  # re-arm cooldown
    assert g.feed(-1, now=2.0) == 0


def test_slow_wheel_reverse_source_change_and_single_batch_do_not_arm():
    g = WheelShurikenGate()
    for index in range(12):
        assert g.feed(-1, now=10.0 + index*.25) == 0
    g = WheelShurikenGate()
    assert g.feed(-5, now=30.0) == 0  # one wheel event != sustained gesture
    assert g.feed(2, now=30.03) == 0  # direction change resets
    assert g.feed(-2, source='remote', now=30.06) == 0  # source change resets
    assert g.feed(-2, source='remote', now=30.10) == -1
    assert g.feed(-2, source='remote', now=30.14) == 0  # cooldown
    assert g.feed(-1, source='remote', now=30.18) == 0


def test_rapid_upward_flight_direction_is_correct():
    g = WheelShurikenGate()
    assert [g.feed(+2, now=40.0+index*.04) for index in range(4)] == [0,1,0,0]




def test_coalesced_fast_wheel_starts_without_four_events():
    """2 Qt events with several notches each must work; 4 events were too strict."""
    g = WheelShurikenGate()
    assert g.feed(-2, now=10.0) == 0
    assert g.feed(-3, now=10.065) == -1


def test_single_aggregated_event_does_not_start():
    g = WheelShurikenGate()
    assert g.feed(-20, now=10.0) == 0


def test_slow_dense_wheel_stays_normal_hybrid():
    """Even with several wheel events, low average pace does not arm."""
    g = WheelShurikenGate()
    assert [g.feed(-1, now=t) for t in (10.0, 10.16, 10.32, 10.48)] == [0, 0, 0, 0]


def test_not_enough_duration_does_not_arm_even_with_many_notches():
    g = WheelShurikenGate()
    assert g.feed(-5, now=11.0) == 0
    assert g.feed(-5, now=11.010) == 0
    assert g.feed(-1, now=11.042) == -1


def test_window_cuts_old_events_and_direction_flip_resets():
    g = WheelShurikenGate()
    assert g.feed(-2, now=15.0) == 0
    assert g.feed(-2, now=15.40) == 0  # beyond MAX_GAP_MS
    assert g.feed(+3, now=15.46) == 0  # direction flip
    assert g.feed(+2, now=15.52) == +1


def make_auto_pad(*, position=6000, maximum=20000):
    module, pad = scroll_pad()
    bar = FakeScrollBar(position=position, maximum=maximum, page_step=500)
    tree = FakeListTree(bar)
    pad.auto_target_provider = lambda: tree
    pad.target_provider = lambda: None   # Test wheel-trigger without any visible Remote.
    pad.scroll_requested = FakeSignal()
    pad.scroll_requested.emit = lambda delta: bar.setValue(bar.value()+delta)
    pad.flight_settled = FakeSignal()
    return module,pad,tree,bar


def test_wheel_launch_uses_existing_full_range_engine_without_remote():
    module,pad,tree,bar = make_auto_pad()
    with patch.object(module.time, 'monotonic', return_value=100.0):
        assert pad.start_from_wheel(-1)
        assert pad._auto_wheel_flight
        assert pad._flight_target is tree
        assert pad._flight.full_range
        assert pad._flight.distance_px == bar.maximum() - 6000
        assert pad.wheel_while_flying('DOWN')
        assert pad._cruise_rate > 1
        assert pad.wheel_while_flying('UP')
        assert pad._cruise_rate < 1
    assert pad.start_from_wheel(-1) is False  # no overlap


def test_auto_reverse_brake_stops_without_leaking_row_moves():
    module,pad,tree,bar = make_auto_pad()
    with patch.object(module.time, 'monotonic', return_value=123.0):
        assert pad.start_from_wheel(-1)
        for _ in range(AUTO_SHURIKEN_REVERSE_STOP_NOTCHES - 1):
            assert pad.wheel_while_flying('UP')
            assert pad._flight is not None
        assert pad.wheel_while_flying('UP')
    assert pad._flight is None
    assert pad.flight_settled.emitted == [(tree,)]
    assert pad._auto_wheel_flight is False


def test_same_direction_resets_reverse_count():
    module,pad,tree,bar = make_auto_pad()
    with patch.object(module.time, 'monotonic', return_value=200.0):
        assert pad.start_from_wheel(1)
        for _ in range(AUTO_SHURIKEN_REVERSE_STOP_NOTCHES-1):
            pad.wheel_while_flying('DOWN')
        assert pad._flight is not None
        pad.wheel_while_flying('UP')  # same as scrollbar movement -> acceleration
        assert pad._reverse_notches == 0
        pad.wheel_while_flying('DOWN')
        assert pad._flight is not None


def test_auto_at_edge_cannot_launch_and_invalid_target_cancels_without_settle():
    module,pad,tree,bar = make_auto_pad(position=20000)
    assert pad.start_from_wheel(-1) is False
    assert pad._auto_wheel_flight is False
    bar.setValue(4000)
    with patch.object(module.time, 'monotonic', return_value=300.0):
        assert pad.start_from_wheel(-1)
        pad.auto_target_provider = lambda: None
        assert pad.wheel_while_flying('UP') is False
        assert pad._flight is None
    assert pad.flight_settled.emitted == []


def test_integration_preserves_legacy_button_and_gates_correct_lists():
    app = (ROOT/'src/app.py').read_text('utf-8')
    remote = (ROOT/'src/launch_remote.py').read_text('utf-8')
    view = (ROOT/'src/expanded_view.py').read_text('utf-8')
    assert 'self._shuriken_wheel_gate = WheelShurikenGate()' in app
    assert 'launcher.auto_shuriken_scroll_files_list_target' in remote
    assert "auto_input(max(-5, min(5, steps)), source='remote')" in remote
    assert "auto_handler(steps, source='list')" in view
    assert 'self.scroll_pad = ShurikenScrollPad(self)' in remote
    assert 'root.addWidget(self.scroll_pad' in remote  # manual fallback preserved
    assert 'self.middle.tree.shuriken_stop_on_action' in view
    assert 'self._auto_wheel_flight' in (ROOT/'src/remote_shuriken_scroll.py').read_text('utf-8')


def test_list_wheel_can_start_and_brake_with_remote_initially_absent():
    """Isolated actual Launcher method: auto-created engine works without UI."""
    import ast
    from types import SimpleNamespace as NS
    source = (ROOT/'src/app.py').read_text('utf-8')
    module = ast.parse(source)
    klass = next(n for n in module.body if isinstance(n, ast.ClassDef)
                 and n.name == 'Launcher') if 'class Launcher(' in source else None
    if klass is None:
        # Pick by method, not GUI class name (which can change across releases).
        klass = next(n for n in module.body if isinstance(n, ast.ClassDef)
                     and any(isinstance(c, ast.FunctionDef)
                             and c.name == 'shuriken_wheel_list_input' for c in n.body))
    method = next(n for n in klass.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'shuriken_wheel_list_input')
    ns = {'AUTO_SHURIKEN_ENABLED': True}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated_auto_input>', 'exec'), ns)
    invoke = ns['shuriken_wheel_list_input']
    _,pad,tree,_ = make_auto_pad()
    class LauncherMock:
        remote_window = None
        _shuriken_wheel_gate = WheelShurikenGate()
        def auto_shuriken_scroll_files_list_target(self): return tree
        def ensure_remote_window(self):
            self.remote_window = NS(scroll_pad=pad)
            return self.remote_window
    launcher = LauncherMock()
    # Gate timing and sustained-count policy is tested separately above.
    # Here assert the Launcher route without importing the real Qt GUI.
    outcomes = iter([0, 0, 0, -1])
    launcher._shuriken_wheel_gate.feed = lambda *_args, **_kwargs: next(outcomes)
    for i in range(3):
        assert invoke(launcher, -2, source='list') is False
    assert invoke(launcher, -2, source='list') is True
    assert launcher.remote_window is not None
    assert pad._auto_wheel_flight
    # Extra input is for velocity only, never current-row navigation.
    assert invoke(launcher, 1, source='list') is True


def test_auto_scroll_callback_bypasses_remote_area_only_during_auto_flight():
    import ast
    from types import SimpleNamespace as NS
    source = (ROOT/'src/app.py').read_text('utf-8')
    module = ast.parse(source)
    method = next(n for klass in module.body if isinstance(klass, ast.ClassDef)
                  for n in klass.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'remote_scroll_files_list')
    ns = {'QAbstractItemView': NS(State=NS(EditingState=9))}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                 '<isolated_scroll>', 'exec'), ns)
    class Bar:
        val = 100
        def value(self): return self.val
        def minimum(self): return 0
        def maximum(self): return 1000
        def setValue(self, n): self.val = max(0, min(1000, n))
    class Tree:
        bar = Bar()
        def isVisible(self): return True
        def state(self): return 0
        def verticalScrollBar(self): return self.bar
    tree = Tree()
    class LauncherMock:
        _remote_area = 'files_exp'
        _remote_text_dialog = None
        _remote_confirmation = None
        _remote_context_wheel = None
        expanded_view = NS(isVisible=lambda: True, _workspace_mode='files',
                           middle=NS(tree=tree))
        def isVisible(self): return True
        def isMinimized(self): return False
        def auto_shuriken_scroll_files_list_target(self): return tree
    launcher = LauncherMock()
    launcher.remote_window = NS(scroll_pad=NS(_auto_wheel_flight=False, _flight_target=tree))
    ns['remote_scroll_files_list'](launcher, 90)
    assert tree.bar.val == 100  # Remote target mismatch: blocked normally.
    launcher.remote_window.scroll_pad._auto_wheel_flight = True
    ns['remote_scroll_files_list'](launcher, 90)
    assert tree.bar.val == 190  # auto wheel: scrolling allowed without Remote.


def test_remote_armed_flight_obeys_remote_target_switch():
    module,pad,tree,bar = make_auto_pad()
    pad.target_provider = lambda: tree
    with patch.object(module.time, 'monotonic', return_value=400.0):
        assert pad.start_from_wheel(-1, source='remote')
        assert pad._auto_wheel_source == 'remote'
        pad.target_provider = lambda: None
        assert pad.wheel_while_flying('DOWN') is False
        assert pad._flight is None
        assert pad.flight_settled.emitted == []


def test_auto_landing_notifies_gate_for_rearm_safety():
    module,pad,tree,bar = make_auto_pad()
    ended = []
    pad.auto_end_callback = lambda: ended.append('cooldown')
    with patch.object(module.time, 'monotonic', return_value=500.0):
        assert pad.start_from_wheel(-1)
        pad._settle()
    assert ended == ['cooldown']
    assert pad.flight_settled.emitted == [(tree,)]
