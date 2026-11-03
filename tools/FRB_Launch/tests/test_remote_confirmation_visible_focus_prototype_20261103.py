"""Regression for visible real Yes/No focus on QMessageBox via Remote commands.

Runs with Qt stand-ins so CI without PySide6 can verify the actual source's
method dispatch. Native Qt/Windows rendering must still be checked manually.
"""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace as NS
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_real_confirmation():
    core = ModuleType('PySide6.QtCore')
    core.QObject = type('QObject', (), {'__init__': lambda self, *args: None})
    core.QEvent = NS(Type=NS(MouseButtonPress=1, MouseButtonRelease=2,
                             MouseButtonDblClick=3, Wheel=4, ContextMenu=5,
                             KeyPress=6, KeyRelease=7, ShortcutOverride=8))
    core.QEventLoop = type('QEventLoop', (), {})
    core.QTimer = type('QTimer', (), {})
    core.Qt = NS(FocusReason=NS(TabFocusReason=2), WindowModality=NS(NonModal=0))
    widgets = ModuleType('PySide6.QtWidgets')
    widgets.QApplication = type('QApplication', (), {})
    widgets.QWidget = type('QWidget', (), {})
    widgets.QMessageBox = NS(StandardButton=NS(Yes=16384, No=65536))
    with patch.dict(sys.modules, {'PySide6': ModuleType('PySide6'),
                                  'PySide6.QtCore': core,
                                  'PySide6.QtWidgets': widgets}):
        spec = importlib.util.spec_from_file_location('real_remote_confirmation',
                                                       ROOT/'src/remote_confirmation.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


class Button:
    def __init__(self, name):
        self.name = name
        self.styles = []
        self.focus_calls = []
        self.click_count = 0
        self.updated = 0

    def setStyleSheet(self, style): self.styles.append(style)
    def setFocus(self, reason): self.focus_calls.append(reason)
    def update(self): self.updated += 1
    def click(self): self.click_count += 1


def fixture():
    mod = load_real_confirmation()
    ctrl = mod.RemoteConfirmation.__new__(mod.RemoteConfirmation)
    buttons = {ctrl.NO: Button('No'), ctrl.YES: Button('Yes')}
    defaults = []
    ctrl.dialog = NS(button=lambda answer: buttons.get(answer),
                     setDefaultButton=lambda b: defaults.append(b), done=Mock())
    ctrl.launcher = NS(remote_window=None)
    ctrl.selected = ctrl.NO
    return ctrl, buttons, defaults


def test_initial_no_highlights_actual_no_button_and_keeps_yes_native():
    ctrl, buttons, defaults = fixture()
    ctrl.choose(ctrl.NO)
    assert '#27865D' in buttons[ctrl.NO].styles[-1]
    assert buttons[ctrl.YES].styles[-1] == ''
    assert buttons[ctrl.NO].focus_calls
    assert defaults[-1] is buttons[ctrl.NO]
    assert buttons[ctrl.NO].updated == 1
    assert ctrl.selected == ctrl.NO


def test_wheel_moves_visible_border_and_real_qt_focus_back_and_forth():
    ctrl, buttons, defaults = fixture()
    ctrl.choose(ctrl.NO)
    ctrl.remote_command('DOWN')
    assert buttons[ctrl.NO].styles[-1] == ''
    assert '#27865D' in buttons[ctrl.YES].styles[-1]
    assert defaults[-1] is buttons[ctrl.YES]
    assert buttons[ctrl.YES].focus_calls
    assert buttons[ctrl.NO].click_count == buttons[ctrl.YES].click_count == 0
    ctrl.remote_command('UP')
    assert buttons[ctrl.YES].styles[-1] == ''
    assert '#27865D' in buttons[ctrl.NO].styles[-1]


def test_arrows_set_exact_button_and_center_clicks_that_real_button():
    ctrl, buttons, _ = fixture()
    ctrl.choose(ctrl.NO)
    ctrl.remote_command('RIGHT')
    assert ctrl.selected == ctrl.YES
    assert '#27865D' in buttons[ctrl.YES].styles[-1]
    ctrl.remote_command('CLICK')
    assert buttons[ctrl.YES].click_count == 1
    assert buttons[ctrl.NO].click_count == 0
    ctrl.remote_command('LEFT')
    assert ctrl.selected == ctrl.NO
    assert '#27865D' in buttons[ctrl.NO].styles[-1]
    ctrl.remote_command('ENTER')
    assert buttons[ctrl.NO].click_count == 1
    ctrl.dialog.done.assert_not_called()


def test_close_is_always_no_even_after_yes_and_other_actions_cannot_confirm():
    ctrl, buttons, _ = fixture()
    ctrl.choose(ctrl.YES)
    for command in ('SEARCH_HISTORY', 'DOUBLE_CLICK', 'REMOTE_TARGET_EXP'):
        assert ctrl.remote_command(command) is True
    assert buttons[ctrl.YES].click_count == 0
    ctrl.remote_command('CLOSE')
    assert buttons[ctrl.NO].click_count == 1
    assert buttons[ctrl.YES].click_count == 0


def test_no_focus_style_is_applied_to_actual_buttons_not_only_remote_label():
    source = (ROOT/'src/remote_confirmation.py').read_text(encoding='utf-8')
    assert 'button.setStyleSheet(self.FOCUS_BUTTON_STYLE if candidate == answer else' in source
    assert 'self.dialog.setDefaultButton(button)' in source
    assert 'button.setFocus(Qt.FocusReason.TabFocusReason)' in source
    assert 'button.click()' in source
    assert 'self.dialog.activateWindow()' in source
