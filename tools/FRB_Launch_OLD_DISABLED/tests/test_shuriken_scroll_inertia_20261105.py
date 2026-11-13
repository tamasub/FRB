"""Qt-free physics and input lifecycle tests for release-to-launch animation."""
from pathlib import Path
import ast
import importlib.util
import math
import sys
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_scroll_model import (plan_flick, eased_displacement, ScrollFlight,
                                   DEADZONE_PX, MAX_TRAVEL_PX, MAX_DURATION_S,
                                   MOTION_WINDOW_S)


def samples(dy=-50, duration=.10, dx=0):
    return [(0, 100, 100), (.5*duration, 100+dx*.5, 100+dy*.5),
            (duration, 100+dx, 100+dy)]


@pytest.mark.parametrize('dy,dx,should_launch', [
    (-50, 0, True), (50, 0, True), (-20, 0, True), (-17, 0, False),
    (0, 0, False), (-40, 100, False), (40, 100, False),
])
def test_mouse_flick_vertical_and_deadzone(dy, dx, should_launch):
    assert (plan_flick(samples(dy=dy, dx=dx)) is not None) is should_launch


def test_recent_motion_required_release_after_long_hold_cancels():
    pts = [(0.0, 0, 0), (.06, 0, -60), (0.38, 0, -60)]
    assert plan_flick(pts) is None
    pts = [(0.0, 0, 0), (.35, 0, 0), (.39, 0, -20), (.43, 0, -60)]
    assert plan_flick(pts) is not None


def test_invalid_motion_input_cancels_without_exception():
    assert plan_flick([]) is None
    assert plan_flick([(0, 0, 0)]) is None
    assert plan_flick([(1, 0, 0), (.2, 0, -90)]) is None
    assert plan_flick([(0, 0, 0), (.1, float('nan'), -90)]) is None
    assert plan_flick([(0, 0, 0), (.1, 0, -90), (.2, 0, -90)]) is not None


def test_speed_controls_travel_and_duration_under_upper_bounds():
    slow = plan_flick(samples(-30, .3))
    medium = plan_flick(samples(-30, .12))
    strong = plan_flick(samples(-30, .04))
    assert slow is not None and medium is not None and strong is not None
    assert 0 < slow.distance_px < medium.distance_px < strong.distance_px <= MAX_TRAVEL_PX
    assert slow.duration_s < medium.duration_s < strong.duration_s <= MAX_DURATION_S
    assert plan_flick(samples(-500, .005)).distance_px == MAX_TRAVEL_PX


def test_easing_starts_slow_peaks_midway_and_lands_exactly():
    flight = ScrollFlight(900, 1.2, 800)
    t = flight.duration_s
    vals = [eased_displacement(flight, t*i/12) for i in range(13)]
    increments = [b-a for a,b in zip(vals, vals[1:])]
    assert vals[0] == 0 and vals[-1] == 900
    assert 0 < increments[0] < increments[2] < increments[5]
    assert 0 < increments[-1] < increments[-3] < increments[-6]
    assert all(b>a for a,b in zip(vals, vals[1:]))
    assert eased_displacement(flight, 999) == 900
    assert eased_displacement(flight, -1) == 0
    reverse = ScrollFlight(-900, 1.2, 800)
    assert eased_displacement(reverse, .6) == -450


class FakeSignal:
    def __init__(self, *args):
        self.emitted = []
    def emit(self, *args):
        self.emitted.append(args)
    def connect(self, handler):
        self.handler = handler


class FakeTimer:
    def __init__(self, parent=None):
        self.active = False
        self.timeout = FakeSignal()
    def setInterval(self, value):
        self.interval = value
    def start(self):
        self.active = True
    def stop(self):
        self.active = False


class FakeWidget:
    def __init__(self, parent=None):
        self._parent = parent
    def setObjectName(self, *args): pass
    def setFixedSize(self, *args): pass
    def setCursor(self, *args): pass
    def setFocusPolicy(self, *args): pass
    def setToolTip(self, *args): pass
    def parentWidget(self): return self._parent
    def hideEvent(self, event): pass


class FakeLabel(FakeWidget):
    def __init__(self, text, parent):
        super().__init__(parent)
        self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def setAlignment(self, *args): pass
    def setAttribute(self, *args): pass


class FakeLayout:
    def __init__(self, *args): pass
    def setContentsMargins(self, *args): pass
    def setSpacing(self, *args): pass
    def addWidget(self, *args): pass


class FakeScrollBar:
    def __init__(self, position=400, minimum=0, maximum=12000, page_step=500):
        self.position = position
        self.low = minimum
        self.high = maximum
        self.page = page_step
    def value(self): return self.position
    def minimum(self): return self.low
    def maximum(self): return self.high
    def pageStep(self): return self.page
    def setValue(self, value):
        self.position = max(self.low, min(self.high, int(value)))


class FakeListTree:
    def __init__(self, bar=None):
        self.bar = bar if bar is not None else FakeScrollBar()
    def verticalScrollBar(self):
        return self.bar


class Event:
    def __init__(self, x, y, *, button=1, buttons=1):
        self.xy = (x, y)
        self._button = button
        self._buttons = buttons
        self.accepted = False
    def button(self): return self._button
    def buttons(self): return self._buttons
    def globalPosition(self): return NS(x=lambda:self.xy[0], y=lambda:self.xy[1])
    def accept(self): self.accepted=True
    def ignore(self): self.accepted=False


def scroll_pad():
    qtcore = ModuleType('PySide6.QtCore')
    qtcore.Qt = NS(MouseButton=NS(LeftButton=1), CursorShape=NS(PointingHandCursor=0),
                   FocusPolicy=NS(NoFocus=0), AlignmentFlag=NS(AlignCenter=0),
                   WidgetAttribute=NS(WA_TransparentForMouseEvents=0))
    qtcore.QTimer = FakeTimer
    qtcore.Signal = FakeSignal
    qtwidgets = ModuleType('PySide6.QtWidgets')
    qtwidgets.QFrame=FakeWidget
    qtwidgets.QVBoxLayout=FakeLayout
    qtwidgets.QLabel=FakeLabel
    with patch.dict(sys.modules, {'PySide6': ModuleType('PySide6'),
                                  'PySide6.QtCore':qtcore, 'PySide6.QtWidgets':qtwidgets}):
        spec=importlib.util.spec_from_file_location('test_remote_shuriken_scroll_runtime',
                                                    ROOT/'src/remote_shuriken_scroll.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    pad = module.ShurikenScrollPad(FakeWidget())
    # The real Qt bound signal is per instance, as with this test stand-in.
    pad.scroll_requested = FakeSignal()
    return module, pad


def test_press_move_release_starts_animation_no_scroll_until_release():
    module, pad = scroll_pad()
    clock=[100.0]
    tree=FakeListTree()
    pad.target_provider=lambda:tree
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(100, 100))
        assert not pad._timer.active
        clock[0]+=.05
        pad.mouseMoveEvent(Event(100, 60))
        clock[0]+=.03
        pad.mouseReleaseEvent(Event(100, 40))
        assert pad._timer.active
        assert pad.scroll_requested.emitted == []
        flight=pad._flight
        assert flight.distance_px>0
        clock[0]+=.06
        pad._scroll_tick()
        assert sum(s[0] for s in pad.scroll_requested.emitted)>0
        while clock[0]-pad._flight_start_time < flight.duration_s+.01:
            clock[0]+=.05
            pad._scroll_tick()
        assert sum(s[0] for s in pad.scroll_requested.emitted)==flight.distance_px
        assert not pad._timer.active
        assert pad._flight is None


def test_short_brake_click_slows_but_keeps_flying_and_does_not_relaunch():
    module, pad = scroll_pad()
    clock = [100.0]
    tree = FakeListTree()
    pad.target_provider = lambda: tree
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.05
        pad.mouseMoveEvent(Event(100,40))
        clock[0]+=.01
        pad.mouseReleaseEvent(Event(100,35))
        assert pad._timer.active
        clock[0]+=.1
        pad._scroll_tick()
        pad.mousePressEvent(Event(100,100))
        assert pad._timer.active and pad._braking_press and not pad._pressed
        clock[0]+=.03
        pad.mouseReleaseEvent(Event(100,100))
        assert not pad._braking_press and pad._flight is not None
        assert 0 < pad._cruise_rate < 1.0
        assert pad._caption.text() == '減速中'
        assert pad._timer.active


def test_long_brake_press_stops_and_release_does_not_relaunch():
    module, pad = scroll_pad()
    clock = [100.0]
    tree = FakeListTree()
    pad.target_provider = lambda: tree
    with patch.object(module.time, 'monotonic', side_effect=lambda: clock[0]):
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.06
        pad.mouseMoveEvent(Event(100,30))
        pad.mouseReleaseEvent(Event(100,30))
        clock[0]+=.2
        pad._scroll_tick()
        moved=sum(s[0] for s in pad.scroll_requested.emitted)
        pad.mousePressEvent(Event(100,100))
        assert pad._timer.active and pad._braking_press
        clock[0]+=.55
        pad._scroll_tick()
        assert not pad._timer.active and pad._flight is None
        clock[0]+=.05
        pad.mouseReleaseEvent(Event(100,100))
        assert not pad._braking_press
        clock[0]+=.5
        pad._scroll_tick()
        assert sum(s[0] for s in pad.scroll_requested.emitted)==moved


def test_click_without_flick_stays_idle():
    module,pad=scroll_pad()
    clock=[0]
    pad.target_provider=lambda:object()
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(20,20))
        clock[0]+=.12
        pad.mouseReleaseEvent(Event(20,20))
        assert pad._flight is None and not pad._timer.active
        assert not pad.scroll_requested.emitted


def test_no_target_or_context_changed_stops_flight():
    module,pad=scroll_pad()
    clock=[10.]
    target=FakeListTree()
    active=[target]
    pad.target_provider=lambda:active[0]
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.07
        pad.mouseReleaseEvent(Event(100,40))
        assert pad._timer.active
        active[0]=FakeListTree()
        clock[0]+=.2
        pad._scroll_tick()
        assert not pad._timer.active and not pad.scroll_requested.emitted
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.04
        active[0]=None
        pad.mouseReleaseEvent(Event(100,40))
        assert not pad._timer.active


def test_hide_cancels_pending_animation():
    module,pad=scroll_pad()
    clock=[10.]
    target=FakeListTree()
    pad.target_provider=lambda:target
    with patch.object(module.time,'monotonic',side_effect=lambda:clock[0]):
        pad.mousePressEvent(Event(100,100))
        clock[0]+=.06
        pad.mouseReleaseEvent(Event(100,30))
        assert pad._timer.active
        pad.hideEvent(None)
        assert pad._flight is None and not pad._timer.active


def test_target_accessor_blocks_modal_other_workspace_and_editing():
    src=(ROOT/'src/app.py').read_text('utf-8')
    tree=ast.parse(src)
    method=next(n for cls in tree.body if isinstance(cls,ast.ClassDef)
                for n in cls.body if isinstance(n,ast.FunctionDef) and
                n.name=='remote_scroll_files_list_target')
    ns={'QAbstractItemView':NS(State=NS(EditingState=9))}
    isolated=ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[]))
    exec(compile(isolated,'<scroll-target>', 'exec'),ns)
    invoke=ns['remote_scroll_files_list_target']
    bar=object()
    t=NS(isVisible=lambda: True, state=lambda:0, verticalScrollBar=lambda:bar)
    view=NS(isVisible=lambda:True,_workspace_mode='files',middle=NS(tree=t))
    launcher=NS(isVisible=lambda: True,isMinimized=lambda:False,expanded_view=view,
                _remote_area='directory',_remote_text_dialog=None,
                _remote_confirmation=None,_remote_context_wheel=None)
    assert invoke(launcher) is t
    launcher._remote_confirmation=object()
    assert invoke(launcher) is None
    launcher._remote_confirmation=None
    launcher._remote_area='browser'
    assert invoke(launcher) is None
    launcher._remote_area='directory'
    view._workspace_mode='browser'
    assert invoke(launcher) is None
    view._workspace_mode='files'
    t.state=lambda:9
    assert invoke(launcher) is None
