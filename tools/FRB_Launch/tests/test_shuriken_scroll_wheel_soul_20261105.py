"""Scroll-flight throttle + selection-safe current handoff, without Windows Qt."""
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from shuriken_scroll_handoff import handoff_current_at_scroll_stop
from test_shuriken_scroll_inertia_20261105 import (scroll_pad, Event, FakeListTree,
                                                   FakeScrollBar, FakeSignal)


class VisibleRow:
    def __init__(self, number, *, hidden=False, disabled=False):
        self.number = number
        self.hidden = hidden
        self.disabled = disabled
        self.row = {'path': f'/file_{number}.txt'}
    def isHidden(self):
        return self.hidden
    def isDisabled(self):
        return self.disabled


class Viewport:
    def width(self):
        return 120
    def height(self):
        return 180


class FakeTree:
    def __init__(self, length=4000, *, position=2500, page_step=10):
        self.rows = [VisibleRow(i) for i in range(length)]
        self.bar = FakeScrollBar(position=position, maximum=max(0, length-page_step),
                                 page_step=page_step)
        self.current = self.rows[0]
        self.selected = {0, 15}  # A bulk selection MUST not change.
        self.calls = []
        self.empty_in_middle = False

    def verticalScrollBar(self):
        return self.bar
    def topLevelItemCount(self):
        return len(self.rows)
    def topLevelItem(self, index):
        return self.rows[index]
    def viewport(self):
        return Viewport()
    def itemAt(self, x, y):
        if self.empty_in_middle and 82 <= y <= 98:
            return None
        index = self.bar.value() + y // 18
        return self.rows[index] if 0 <= index < len(self.rows) else None
    def currentItem(self):
        return self.current
    def setCurrentItem(self, item, col, flags):
        assert col == 0
        assert flags is NO_UPDATE  # NoUpdate preserves selectedItems().
        self.current = item
        self.calls.append(item.number)


NO_UPDATE = object()


def row_data(item):
    return item.row


def test_handoff_center_at_large_scroll_offset_preserves_multiselection():
    tree = FakeTree(position=2500)
    selected_before = set(tree.selected)
    new_current = handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE)
    assert new_current.number == 2505
    assert tree.current is new_current
    assert tree.selected == selected_before
    assert tree.bar.value() == 2500  # Never jump back to old current.
    assert handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE) is new_current
    assert tree.calls == [2505]


def test_handoff_falls_back_to_near_center_when_center_is_blank():
    tree = FakeTree(position=3200)
    tree.empty_in_middle = True
    target = handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE)
    assert 3200 <= target.number < 3210
    assert tree.selected == {0, 15}


def test_handoff_top_and_bottom_prefer_edges_not_center():
    tree = FakeTree(position=0)
    assert handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE).number == 0
    tree.bar.setValue(tree.bar.maximum())
    assert handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE).number == 3999
    assert tree.selected == {0, 15}


def test_handoff_ignores_hidden_edge_row_and_nonactionable_viewport():
    tree = FakeTree(position=3990)
    tree.rows[-1].hidden = True
    assert handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE).number == 3998
    tree = FakeTree(position=100)
    for row in tree.rows[100:110]:
        row.row = None
    assert handoff_current_at_scroll_stop(tree, row_data, NO_UPDATE) is None
    assert tree.current.number == 0


def launch(module, pad, clock, *, negative=False):
    bar = FakeScrollBar(position=6000, maximum=20000, page_step=500)
    tree = FakeListTree(bar)
    pad.target_provider = lambda: tree
    pad.scroll_requested = FakeSignal()
    # Connect the already-existing scrollbar updater without using Qt itself.
    def update(delta):
        bar.setValue(bar.value() + delta)
    pad.scroll_requested.emit = update
    pad.flight_settled = FakeSignal()
    pad.mousePressEvent(Event(100,100))
    clock[0] += .05
    pad.mouseMoveEvent(Event(100, 160 if negative else 40))
    clock[0] += .04
    pad.mouseReleaseEvent(Event(100, 175 if negative else 25))
    assert pad._flight is not None
    return tree, bar


def test_wheel_forward_accelerates_and_reverse_decelerates_during_flight():
    module, pad = scroll_pad()
    clock = [10.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        tree, bar = launch(module, pad, clock)
        assert pad.wheel_while_flying('DOWN') is True
        assert pad._cruise_rate == module.WHEEL_ACCEL_FACTOR
        assert pad._caption.text() == '加速中'
        assert pad.wheel_while_flying('UP') is True
        assert pad._cruise_rate < 1.0
        assert pad._caption.text() == '減速中'
        clock[0] += 0.2
        pad._scroll_tick()
        assert bar.value() > 6000
        assert pad._flight is not None
        assert pad.wheel_while_flying('RIGHT') is False


def test_negative_flight_inverts_wheel_acceleration_direction():
    module, pad = scroll_pad()
    clock = [20.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        tree, bar = launch(module, pad, clock, negative=True)
        assert pad._flight.distance_px < 0
        assert pad.wheel_while_flying('UP') is True
        assert pad._cruise_rate > 1
        assert pad.wheel_while_flying('DOWN') is True
        assert pad._cruise_rate < 1


def test_wheel_adjustment_is_bounded_and_recovers_from_tap_braking():
    module, pad = scroll_pad()
    clock = [30.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        launch(module, pad, clock)
        for _ in range(70):
            pad.wheel_while_flying('DOWN')
        assert pad._cruise_rate == module.MAX_CRUISE_RATE
        for _ in range(70):
            pad.wheel_while_flying('UP')
        assert pad._cruise_rate == module.MIN_CRUISE_RATE
        for _ in range(15):
            pad.wheel_while_flying('DOWN')
        assert pad._cruise_rate > 1.0


def test_natural_landing_signals_handoff_once():
    module, pad = scroll_pad()
    clock = [40.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        tree, bar = launch(module, pad, clock)
        clock[0] += pad._flight.duration_s + .1
        pad._scroll_tick()
        assert pad._flight is None
        assert bar.value() == bar.maximum()
        assert pad.flight_settled.emitted == [(tree,)]
        pad._scroll_tick()
        assert pad.flight_settled.emitted == [(tree,)]


def test_long_press_stops_and_handoffs_but_context_change_never_handoffs():
    module, pad = scroll_pad()
    clock = [50.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        tree, bar = launch(module, pad, clock)
        clock[0] += .5
        pad._scroll_tick()
        pad.mousePressEvent(Event(100,100))
        clock[0] += module.HOLD_TO_STOP_S + .01
        pad._scroll_tick()
        assert pad._flight is None
        assert pad.flight_settled.emitted == [(tree,)]
        pad.mouseReleaseEvent(Event(100,100))
        assert pad._flight is None

    module, pad = scroll_pad()
    clock = [60.0]
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        tree, bar = launch(module, pad, clock)
        pad.target_provider = lambda: None  # Workspace/popup switch.
        assert pad.wheel_while_flying('DOWN') is False
        assert pad._flight is None
        assert pad.flight_settled.emitted == []


def test_wheel_wiring_only_reinterprets_physical_wheel_and_preserves_ctrl():
    src = (ROOT/'src/launch_remote.py').read_text(encoding='utf-8')
    model = (ROOT/'src/app.py').read_text(encoding='utf-8')
    assert "if callable(adjust_opacity) and adjust_opacity(event):" in src
    assert "scroll_pad.wheel_while_flying(direction)" in src
    assert "self.command.emit(direction)" in src
    assert "self.scroll_pad.flight_settled.connect(launcher.remote_scroll_files_list_settle)" in src
    assert "QItemSelectionModel.SelectionFlag.NoUpdate" in model


def test_real_wheelpad_dispatches_speed_control_only_while_flying():
    """Execute actual WheelPad.wheelEvent body without importing Qt GUI."""
    import ast
    from types import SimpleNamespace as NS

    source = (ROOT/'src/launch_remote.py').read_text('utf-8')
    module = ast.parse(source)
    wheel_cls = next(n for n in module.body if isinstance(n, ast.ClassDef)
                     and n.name == 'WheelPad')
    wheel_method = next(n for n in wheel_cls.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'wheelEvent')
    compiled = compile(ast.Module(body=[wheel_method], type_ignores=[]),
                       'wheelpad_under_test.py', 'exec')
    namespace = {}
    exec(compiled, namespace)
    wheel_event = namespace['wheelEvent']

    module, pad = scroll_pad()
    clock = [10.0]
    emitted = []
    remote = NS(scroll_pad=pad,
                adjust_background_opacity_from_wheel=lambda e: bool(e.ctrl))
    fake_wheel = NS(parentWidget=lambda: remote, _angle_remainder=0,
                    _pixel_remainder=0,
                    command=NS(emit=lambda cmd: emitted.append(cmd)))
    class Wheel:
        def __init__(self, angle, *, ctrl=False):
            self.angle = angle
            self.ctrl = ctrl
            self.accepted = False
        def angleDelta(self): return NS(y=lambda: self.angle)
        def pixelDelta(self): return NS(y=lambda: 0)
        def accept(self): self.accepted=True

    wheel_event(fake_wheel, Wheel(120))
    assert emitted == ['UP']  # Idle still navigates the Files current.
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        launch(module, pad, clock)
        wheel_event(fake_wheel, Wheel(-120))
        assert emitted == ['UP']  # No new row movement while flying.
        assert pad._cruise_rate == module.WHEEL_ACCEL_FACTOR
        wheel_event(fake_wheel, Wheel(120))
        assert pad._cruise_rate < 1.0
        wheel_event(fake_wheel, Wheel(-120, ctrl=True))
        assert pad._cruise_rate < 1.0  # Ctrl wheel stays opacity-only.
        pad._stop()
        wheel_event(fake_wheel, Wheel(-120))
        assert emitted == ['UP', 'DOWN']  # Normal wheel is restored.
