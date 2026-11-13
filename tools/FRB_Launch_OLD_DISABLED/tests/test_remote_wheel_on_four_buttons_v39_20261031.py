"""v39: four Remote buttons accept wheel rotation like the central pad.

These tests exercise the real WheelPad.wheelEvent and RemoteWheelButton
implementation with a lightweight Qt stand-in (CI does not have PySide6).
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'launch_remote.py'
SOURCE = SRC.read_text(encoding='utf-8')
MODULE = ast.parse(SOURCE)


class FakePushButton:
    def __init__(self, text='', parent=None):
        self.text = text
        self._parent = parent
        self.native_wheel = Mock()
        self.clicked = SimpleNamespace(connect=Mock())
        self.props = {}

    def parentWidget(self):
        return self._parent

    def wheelEvent(self, event):
        self.native_wheel(event)

    def setToolTip(self, text):
        self.tooltip = text

    def setProperty(self, key, value):
        self.props[key] = value

    def setFixedSize(self, width, height):
        self.size = (width, height)

    def setFocusPolicy(self, focus):
        self.focus = focus


class FakeWheelEvent:
    def __init__(self, *, angle=0, pixel=0):
        self.angle = angle
        self.pixel = pixel
        self.accepted = False

    def angleDelta(self):
        return SimpleNamespace(y=lambda: self.angle)

    def pixelDelta(self):
        return SimpleNamespace(y=lambda: self.pixel)

    def accept(self):
        self.accepted = True


def class_method(class_name, method_name):
    klass = next(x for x in MODULE.body if isinstance(x, ast.ClassDef)
                 and x.name == class_name)
    return next(x for x in klass.body if isinstance(x, ast.FunctionDef)
                and x.name == method_name)


def prepare_test_classes():
    wheel_button = next(x for x in MODULE.body if isinstance(x, ast.ClassDef)
                        and x.name == 'RemoteWheelButton')
    wheel_pad_fn = class_method('WheelPad', 'wheelEvent')
    pad_class = ast.ClassDef(name='WheelOnly', bases=[], keywords=[],
                             body=[wheel_pad_fn], decorator_list=[])
    ns = {'QPushButton': FakePushButton}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[wheel_button, pad_class],
                                            type_ignores=[])), str(SRC), 'exec'), ns)
    pad = ns['WheelOnly']()
    pad.command = SimpleNamespace(emit=Mock())
    pad._angle_remainder = 0
    pad._pixel_remainder = 0
    parent = SimpleNamespace(pad=pad)
    return ns['RemoteWheelButton'], parent, pad


def test_exactly_four_requested_buttons_are_wheel_enabled():
    init = class_method('LaunchRemote', '__init__')
    enabled = []
    other = []
    for node in ast.walk(init):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == '_button'):
            continue
        command = node.args[2].value
        enabled_arg = next((x.value.value for x in node.keywords
                            if x.arg == 'wheel_enabled'), False)
        (enabled if enabled_arg else other).append(command)
    assert set(enabled) == {'BACKTAB', 'TAB', 'SEARCH_HISTORY', 'FOLDER_HISTORY'}
    assert len(enabled) == 4
    assert {'LEFT', 'RIGHT', 'HOME', 'CLOSE', 'MORE_MENU'}.issubset(other)


def test_all_four_buttons_forward_wheel_to_one_shared_pad_and_keep_fractional_steps():
    button_class, parent, pad = prepare_test_classes()
    buttons = [button_class(name, parent) for name in
               ('BackTab', 'Tab', '検索履歴', 'フォルダー履歴')]
    # Half-step on one button and half-step on another must be one step,
    # exactly like rolling the physical wheel over the center pad twice.
    first = FakeWheelEvent(angle=60)
    second = FakeWheelEvent(angle=60)
    buttons[0].wheelEvent(first)
    assert pad.command.emit.call_count == 0
    buttons[1].wheelEvent(second)
    pad.command.emit.assert_called_once_with('UP')
    assert first.accepted and second.accepted
    # Down rotation is identical to the central pad; buttons do not TAB.
    pad.command.emit.reset_mock()
    buttons[2].wheelEvent(FakeWheelEvent(angle=-120))
    buttons[3].wheelEvent(FakeWheelEvent(angle=120))
    assert [a.args[0] for a in pad.command.emit.call_args_list] == ['DOWN', 'UP']
    assert all(b.native_wheel.call_count == 0 for b in buttons)


def test_pixel_trackpad_accumulator_is_shared_across_buttons():
    button_class, parent, pad = prepare_test_classes()
    button_class('BackTab', parent).wheelEvent(FakeWheelEvent(pixel=18))
    button_class('検索履歴', parent).wheelEvent(FakeWheelEvent(pixel=18))
    pad.command.emit.assert_called_once_with('UP')


def test_without_pad_naturally_falls_back_to_native_wheel_event():
    button_class, _, _ = prepare_test_classes()
    obj = button_class('Tab', SimpleNamespace())
    event = FakeWheelEvent(angle=120)
    obj.wheelEvent(event)
    obj.native_wheel.assert_called_once_with(event)


def test_existing_click_actions_and_focus_policy_are_preserved():
    fn = class_method('LaunchRemote', '_button')
    ns = {'RemoteWheelButton': prepare_test_classes()[0],
          'QPushButton': FakePushButton,
          'Qt': SimpleNamespace(FocusPolicy=SimpleNamespace(NoFocus='no_focus'))}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                 str(SRC), 'exec'), ns)
    parent = SimpleNamespace(pad=Mock())
    parent.command = SimpleNamespace(emit=Mock())
    wheel_btn = ns['_button'](parent, 'BackTab', '前へ', 'BACKTAB',
                              width=76, height=37, role='tab', wheel_enabled=True)
    normal_btn = ns['_button'](parent, '←', '戻る', 'LEFT', width=45, height=44)
    assert type(wheel_btn).__name__ == 'RemoteWheelButton'
    assert type(normal_btn) is FakePushButton
    assert wheel_btn.size == (76, 37) and normal_btn.size == (45, 44)
    assert wheel_btn.focus == 'no_focus'
    assert wheel_btn.clicked.connect.call_count == 1
    assert normal_btn.clicked.connect.call_count == 1
    wheel_btn.clicked.connect.call_args.args[0]()
    normal_btn.clicked.connect.call_args.args[0]()
    assert [a.args[0] for a in parent.command.emit.call_args_list] == ['BACKTAB', 'LEFT']


def test_no_global_event_filter_or_synthetic_input_for_this_feature():
    button_class = next(x for x in MODULE.body if isinstance(x, ast.ClassDef)
                        and x.name == 'RemoteWheelButton')
    text = ast.get_source_segment(SOURCE, button_class)
    assert 'installEventFilter' not in text
    assert 'QKeyEvent' not in text
    assert 'pad.wheelEvent(event)' in text
