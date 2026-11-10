"""Shuriken v4: solid circle, smaller cursor and safe dialog-confirm click.

Pure Qt stand-ins run on CI without PySide6. Actual Windows painting, native
mouse capture and dialog z-order remain subject to on-device validation.
"""
from pathlib import Path
import importlib.util
import sys
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import Mock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from shuriken_model import ShurikenEntry


class DummySignal:
    def __init__(self):
        self.emit = Mock()


class DummyWidget:
    def __init__(self, *args):
        self.base_press = 0
        self.base_release = 0
        self.base_hide = 0

    def setObjectName(self, *args): pass
    def setProperty(self, *args): pass
    def setToolTip(self, *args): pass
    def setFixedSize(self, *args): pass
    def setFocusPolicy(self, *args): pass
    def setCursor(self, *args): pass
    def setDown(self, *args): pass
    def mousePressEvent(self, event): self.base_press += 1
    def mouseReleaseEvent(self, event): self.base_release += 1
    def mouseMoveEvent(self, event): pass
    def hideEvent(self, event): self.base_hide += 1
    def rect(self): return NS(contains=lambda point: 0 <= point[0] < 50 and 0 <= point[1] < 46)


class FakeTimer:
    def __init__(self, *args):
        self.interval = 0
        self.active = False
        self.timeout = NS(connect=lambda callback: setattr(self, 'callback', callback))
    def setInterval(self, interval): self.interval = interval
    def start(self): self.active = True
    def stop(self): self.active = False


class DummyEvent:
    def __init__(self, x=20, y=20, global_x=100, global_y=100, button=1):
        self.xy = (x, y)
        self.gxy = (global_x, global_y)
        self._button = button
        self.accepted = False

    def button(self): return self._button
    def buttons(self): return self._button
    def position(self): return NS(toPoint=lambda: self.xy)
    def globalPosition(self): return NS(toPoint=lambda: NS(x=lambda: self.gxy[0], y=lambda: self.gxy[1]))
    def accept(self): self.accepted = True


def load_button_module():
    core = ModuleType('PySide6.QtCore')
    core.Qt = NS(MouseButton=NS(LeftButton=1), FocusPolicy=NS(NoFocus=0),
                 CursorShape=NS(PointingHandCursor=0),
                 WindowType=NS(Tool=1, FramelessWindowHint=2,
                               WindowDoesNotAcceptFocus=4, WindowTransparentForInput=8),
                 WidgetAttribute=NS(WA_TranslucentBackground=1,
                                    WA_ShowWithoutActivating=2,
                                    WA_TransparentForMouseEvents=4))
    core.Signal = lambda *args: DummySignal()
    core.QTimer = FakeTimer
    for name in ('QPoint', 'QPointF', 'QRect', 'QRectF'):
        setattr(core, name, type(name, (), {}))
    gui = ModuleType('PySide6.QtGui')
    for name in ('QPainter', 'QPen', 'QColor', 'QFont', 'QFontMetrics', 'QPixmap'):
        setattr(gui, name, type(name, (), {'__init__': lambda self, *a: None}))
    gui.QCursor = NS(pos=lambda: NS(x=lambda: 100, y=lambda: 100))
    widgets = ModuleType('PySide6.QtWidgets')
    widgets.QApplication = DummyWidget
    widgets.QWidget = DummyWidget
    widgets.QPushButton = DummyWidget
    appearance = ModuleType('launch_appearance')
    appearance.theme_family = lambda *args: 'light'
    with patch.dict(sys.modules, {'PySide6': ModuleType('PySide6'),
                                  'PySide6.QtCore': core, 'PySide6.QtGui': gui,
                                  'PySide6.QtWidgets': widgets,
                                  'launch_appearance': appearance}):
        spec = importlib.util.spec_from_file_location('test_remote_shuriken_runtime',
                                                       ROOT / 'src/remote_shuriken.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class Preview:
    def __init__(self, *args):
        self.present = Mock()
        self.hide = Mock()
        self.set_confirmation = Mock()


@pytest.fixture
def module():
    mod = load_button_module()
    mod.ShurikenPreview = Preview
    return mod


def make_button(mod, text_dialog=None, confirm_dialog=None):
    launcher = NS(_remote_text_dialog=text_dialog, _remote_confirmation=confirm_dialog,
                  shuriken_items=Mock(return_value=[
                      ShurikenEntry('zip', 'ZIP保存', 1, 'up', 1),
                      ShurikenEntry('git', 'Gitコミット', 1, 'down', 2)]))
    button = mod.ShurikenButton(launcher, DummyWidget(), 1)
    button.triggered = DummySignal()
    return button, launcher


@pytest.mark.parametrize('dialog_kind', ['text', 'yesno'])
def test_dialog_press_click_routes_to_exact_selected_dialog_without_preview(module, dialog_kind):
    controller = NS(remote_command=Mock())
    button, launcher = make_button(module, **{dialog_kind == 'text' and 'text_dialog' or 'confirm_dialog': controller})
    press = DummyEvent()
    button.mousePressEvent(press)
    assert button._drag_start is None
    assert button._preview is None
    launcher.shuriken_items.assert_not_called()
    release = DummyEvent()
    button.mouseReleaseEvent(release)
    assert release.accepted
    controller.remote_command.assert_called_once_with('CLICK')
    button.triggered.emit.assert_not_called()
    assert button.base_press == 1 and button.base_release == 1


def test_release_outside_the_button_cancels_dialog_confirmation(module):
    controller = NS(remote_command=Mock())
    button, launcher = make_button(module, confirm_dialog=controller)
    button.mousePressEvent(DummyEvent())
    button.mouseReleaseEvent(DummyEvent(x=80, y=80))
    controller.remote_command.assert_not_called()
    button.triggered.emit.assert_not_called()


def test_no_click_if_dialog_closed_or_replaced_between_press_and_release(module):
    first, second = NS(remote_command=Mock()), NS(remote_command=Mock())
    button, launcher = make_button(module, confirm_dialog=first)
    button.mousePressEvent(DummyEvent())
    launcher._remote_confirmation = second
    button.mouseReleaseEvent(DummyEvent())
    first.remote_command.assert_not_called()
    second.remote_command.assert_not_called()
    button.triggered.emit.assert_not_called()


def test_normal_shuriken_flick_remains_intact_outside_confirmation(module):
    button, launcher = make_button(module)
    button.mousePressEvent(DummyEvent())
    assert button._preview is not None
    assert button._preview.present.call_count == 1
    button.mouseMoveEvent(DummyEvent(global_y=50))  # Draw UP eye first.
    button.mouseReleaseEvent(DummyEvent(global_y=50))  # -50px = UP
    # First flick proposes but never executes or closes the Pokeball.
    button.triggered.emit.assert_not_called()
    assert button._pending_confirmation.candidate_id == 'zip'
    assert button._pending_confirmation.choice == 'cancel'
    button._preview.hide.assert_not_called()
    launcher.shuriken_items.assert_called_once_with(1)



def test_dialog_appearing_during_flick_prevents_background_launch(module):
    button, launcher = make_button(module)
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_y=50))
    launcher._remote_confirmation = NS(remote_command=Mock())
    button.mouseReleaseEvent(DummyEvent(global_y=50))
    button.triggered.emit.assert_not_called()
    launcher._remote_confirmation.remote_command.assert_not_called()


def test_normal_click_with_no_dialog_does_not_launch_action(module):
    button, launcher = make_button(module)
    button.mousePressEvent(DummyEvent())
    button.mouseReleaseEvent(DummyEvent())
    button.triggered.emit.assert_not_called()


def test_visual_contract_opaque_background_smaller_marker():
    src = (ROOT / 'src/remote_shuriken.py').read_text('utf-8')
    assert 'CURRENT_RADIUS = 24' in src
    assert 'painter.setBrush(QColor(228, 244, 215, 255))' in src
    assert 'QColor(150, 203, 121, 125)' in src  # mark remains translucent
    assert 'WA_TranslucentBackground' in src  # OUTSIDE the ring stays clear
