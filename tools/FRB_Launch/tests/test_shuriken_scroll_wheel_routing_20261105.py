"""Remote wheel ownership during an active shuriken scroll (Qt-free)."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

from test_shuriken_scroll_wheel_soul_20261105 import launch
from test_shuriken_scroll_inertia_20261105 import scroll_pad as build_scroll_pad

ROOT = Path(__file__).resolve().parents[1]


def actual_remote_wheel_handler():
    tree = ast.parse((ROOT / 'src/launch_remote.py').read_text('utf-8'))
    klass = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                 and node.name == 'WheelPad')
    method = next(node for node in klass.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'wheelEvent')
    space = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<wheelpad>', 'exec'), space)
    return space['wheelEvent']


class WheelEvent:
    def __init__(self, delta):
        self.delta = delta
        self.accepted = False
    def angleDelta(self):
        return NS(y=lambda: self.delta)
    def pixelDelta(self):
        return NS(y=lambda: 0)
    def accept(self):
        self.accepted = True


def wheel_driver(scroll_pad):
    emitted=[]
    remote=NS(scroll_pad=scroll_pad,
              adjust_background_opacity_from_wheel=lambda event: False)
    fake=NS(parentWidget=lambda:remote, _angle_remainder=0,
            _pixel_remainder=0, command=NS(emit=lambda command:emitted.append(command)))
    return actual_remote_wheel_handler(), fake, emitted


def test_wheel_up_down_changes_speed_not_current_while_flight():
    module, scroll_pad=build_scroll_pad()
    clock=[10.0]
    handler, fake, emitted=wheel_driver(scroll_pad)
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        launch(module, scroll_pad, clock)
        assert scroll_pad._caption.text()=='滑走中'
        assert scroll_pad._glyph.text()=='↓＋ ↑－'
        handler(fake, WheelEvent(-120))   # DOWN on a flight toward the end.
        assert abs(scroll_pad._cruise_rate-1.45)<1e-5
        assert scroll_pad._caption.text()=='加速中'
        assert emitted==[]
        handler(fake, WheelEvent(120))
        assert scroll_pad._cruise_rate<1.0
        assert scroll_pad._caption.text()=='減速中'
        assert emitted==[]
        scroll_pad._stop()
        handler(fake, WheelEvent(-120))
        assert emitted==['DOWN']


def test_flight_target_becoming_invalid_does_not_leak_wheel_into_current():
    module, scroll_pad=build_scroll_pad()
    clock=[10.0]
    handler, fake, emitted=wheel_driver(scroll_pad)
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        launch(module, scroll_pad, clock)
        scroll_pad.target_provider=lambda:None
        # First notch invalidates the flight. Remaining 4 notches must still
        # belong to the flight, not become 4 accidental current-row steps.
        event=WheelEvent(-600)
        handler(fake,event)
        assert event.accepted
        assert emitted==[]
        assert scroll_pad._flight is None


def test_reverse_flight_shows_reversed_wheel_controls():
    module, scroll_pad=build_scroll_pad()
    clock=[10.0]
    handler, fake, emitted=wheel_driver(scroll_pad)
    with patch.object(module.time, 'monotonic', side_effect=lambda:clock[0]):
        launch(module, scroll_pad, clock, negative=True)
        assert scroll_pad._glyph.text()=='↑＋ ↓－'
        handler(fake, WheelEvent(120))
        assert scroll_pad._cruise_rate>1.0
        assert scroll_pad._caption.text()=='加速中'
        assert emitted==[]
        scroll_pad._stop()
        assert scroll_pad._glyph.text()=='⇅'
