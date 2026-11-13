"""Regression: confirmation MUST consume ぐりぐり/first-hand wheel and clicks.

This is the real bug the previous unit tests missed: direct
ShurikenButton.wheelEvent passed, but LaunchRemote.eventFilter had stolen
native wheel input and navigated Files Exp before that method ran.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest

from test_first_hand_wheel_confirmation_20261110 import make_flick, Wheel

ROOT = Path(__file__).resolve().parents[1]


def unbound_method(file_name, class_name, method_name, **environment):
    """Extract the production method without importing Qt on headless CI."""
    source = ast.parse((ROOT / 'src' / file_name).read_text('utf-8'))
    owner = next(node for node in source.body if isinstance(node, ast.ClassDef)
                 and node.name == class_name)
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef)
                  and node.name == method_name)
    # No hard-coded imitation of branching logic: execute the real AST.
    mod = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(mod)
    namespace = environment.copy()
    exec(compile(mod, str(ROOT / 'src' / file_name), 'exec'), namespace)
    return namespace[method_name]


def test_remote_event_filter_routes_native_wheel_to_first_hand_before_exp():
    wheel=1
    remote_filter=unbound_method(
        'launch_remote.py', 'LaunchRemote', 'eventFilter',
        QEvent=NS(Type=NS(Wheel=wheel)), QWidget=object,)
    hand=NS(_pending_confirmation=object(),wheelEvent=Mock())
    # Real event is installed on Remote itself and its children.
    remote=NS(shuriken_button=hand,pad=NS(wheelEvent=Mock()),
              adjust_background_opacity_from_wheel=Mock(return_value=False))
    event=NS(type=lambda: wheel,accept=Mock())
    assert remote_filter(remote,remote,event) is True
    hand.wheelEvent.assert_called_once_with(event)
    remote.pad.wheelEvent.assert_not_called()
    remote.adjust_background_opacity_from_wheel.assert_not_called()
    event.accept.assert_called_once()


def test_embedded_guriguri_rod_reparent_still_routes_to_first_hand():
    pad_wheel=unbound_method('launch_remote.py', 'WheelPad', 'wheelEvent')
    hand=NS(_pending_confirmation=object(),wheelEvent=Mock())
    remote=NS(shuriken_button=hand)
    pointing_rod=NS(_remote=remote)  # Parent changes in rod mode.
    pad=NS(parentWidget=lambda: pointing_rod,command=NS(emit=Mock()))
    event=NS(accept=Mock())
    pad_wheel(pad,event)
    hand.wheelEvent.assert_called_once_with(event)
    pad.command.emit.assert_not_called()


def test_central_guriguri_wheel_does_not_navigate_exp_during_confirm():
    pad_wheel=unbound_method('launch_remote.py', 'WheelPad', 'wheelEvent')
    hand=NS(_pending_confirmation=object(),wheelEvent=Mock())
    remote=NS(shuriken_button=hand)
    pad=NS(parentWidget=lambda: remote,command=NS(emit=Mock()))
    event=NS(accept=Mock())
    pad_wheel(pad,event)
    hand.wheelEvent.assert_called_once_with(event)
    pad.command.emit.assert_not_called()
    event.accept.assert_called_once()


@pytest.mark.parametrize('command', ['UP','DOWN','CLICK','DOUBLE_CLICK','LEFT','BACK'])
def test_semantic_pad_command_while_confirming_never_reaches_exp(command):
    # Find class owning the production method without depending on class rename.
    source=ast.parse((ROOT/'src/app.py').read_text('utf-8'))
    owner=next(node.name for node in source.body if isinstance(node,ast.ClassDef)
               and any(isinstance(m,ast.FunctionDef) and m.name=='remote_command'
                       for m in node.body))
    remote_command=unbound_method('app.py', owner, 'remote_command')
    hand=NS(_pending_confirmation=object(), confirmation_remote_command=Mock())
    launcher=NS(remote_window=NS(shuriken_button=hand))
    remote_command(launcher, command)
    hand.confirmation_remote_command.assert_called_once_with(command)


def test_approved_overlay_click_executes_and_cancels_only_as_clicked():
    button,_,chosen=make_flick(4,0,-45)
    assert button._pending_confirmation.candidate_id==chosen.item_id
    button.confirm_from_overlay('cancel')
    button.triggered.emit.assert_not_called()
    assert button._pending_confirmation is None

    button,_,chosen=make_flick(4,0,-45)
    button.confirm_from_overlay('ok')
    button.triggered.emit.assert_called_once_with(chosen.item_id)
    assert button._pending_confirmation is None


def test_pad_guriguri_up_down_then_click_executes_only_after_ok():
    button,_,chosen=make_flick(4,0,-45)
    assert button.confirmation_remote_command('DOWN') is True
    assert button._pending_confirmation.choice=='ok'
    assert button._pending_confirmation.wheel_selected
    button.triggered.emit.assert_not_called()
    assert button.confirmation_remote_command('UP') is True
    button.confirmation_remote_command('CLICK')
    button.triggered.emit.assert_not_called()

    button,_,chosen=make_flick(4,0,-45)
    button.confirmation_remote_command('DOWN')
    button.confirmation_remote_command('CLICK')
    button.triggered.emit.assert_called_once_with(chosen.item_id)


def test_confirmation_buttons_are_real_qpushbuttons_with_click_connections():
    source=(ROOT/'src/remote_shuriken.py').read_text('utf8')
    assert "QPushButton('キャンセル', self)" in source
    assert "QPushButton('OK（実行）', self)" in source
    assert ".clicked.connect(" in source
    assert "button.confirm_from_overlay('cancel')" in source
    assert "button.confirm_from_overlay('ok')" in source
    # Only the small panel accepts clicks; the Pokeball remains pass-through.
    assert 'WindowTransparentForInput' in source
    assert 'self.setFixedSize(320, 71)' in source
