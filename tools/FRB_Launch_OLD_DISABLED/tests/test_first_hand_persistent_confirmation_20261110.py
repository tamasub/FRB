"""Persistent first-hand OK/Cancel: no implicit close, regardless of native hide.

Uses the production Qt method bodies with existing lightweight test shims. A
Windows-native Tool-window smoke test is separately required before approval.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_first_hand_wheel_confirmation_20261110 import make_flick, click, Wheel
from test_remote_current_outside_consistency_20261031 import native_callbacks
from test_shuriken_confirm_click_and_paint_20261105 import load_button_module

ROOT = Path(__file__).resolve().parents[1]


def method(file_name, class_name, name, env=None):
    tree = ast.parse((ROOT / 'src' / file_name).read_text(encoding='utf8'))
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == class_name)
    node = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    scope = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 f'<{file_name}.{name}>', 'exec'), scope)
    return scope[name]


def test_confirmation_survives_native_owner_hide_then_responds():
    button, _, chosen = make_flick(4, 0, -45)
    pending = button._pending_confirmation
    assert button._confirmation_visibility_timer.active
    button.hideEvent(object())
    assert button._pending_confirmation is pending
    assert button._selected_entry is chosen
    assert button._confirmation_visibility_timer.active
    assert button._preview.hide.call_count == 0
    # Explicit OK on the SAME first-hand button still works after hide.
    button.wheelEvent(Wheel(-120))
    click(button)
    button.triggered.emit.assert_called_once_with(chosen.item_id)
    assert not button._confirmation_visibility_timer.active


def test_other_remote_commands_cannot_answer_the_dialog():
    button, _, chosen = make_flick(3, -40, -40)
    pending = button._pending_confirmation
    for command in ('BACK', 'DOUBLE_CLICK', 'HOME', 'LEFT', 'RIGHT', 'TARGET_EXP'):
        assert button.confirmation_remote_command(command) is True
        assert button._pending_confirmation is pending
        assert button._selected_entry is chosen
    button.triggered.emit.assert_not_called()
    assert button.confirmation_remote_command('CANCEL') is True
    assert button._pending_confirmation is None


def test_watchdog_recovers_hidden_preview_and_buttons_without_changing_answer():
    button, _, chosen = make_flick(4, 0, -45)
    button.wheelEvent(Wheel(-120))
    pending = button._pending_confirmation
    preview = NS(selected_id=chosen.item_id,
                 isVisible=lambda:False, show=Mock(), raise_=Mock(),
                 _confirmation_hit_layer=NS(isVisible=lambda:False),
                 set_confirmation=Mock())
    button._preview = preview
    button._ensure_confirmation_visibility()
    preview.show.assert_called_once()
    preview.raise_.assert_called_once()
    preview.set_confirmation.assert_called_once_with(pending)
    assert button._pending_confirmation is pending
    assert pending.choice == 'ok'
    button.triggered.emit.assert_not_called()


def test_watchdog_never_revives_mismatched_eye_or_hidden_launcher():
    button, launcher, chosen = make_flick(4, 0, -45)
    preview = NS(selected_id='a_different_id',isVisible=lambda:False,
                 show=Mock(),raise_=Mock(),_confirmation_hit_layer=None)
    button._preview = preview
    button._ensure_confirmation_visibility()
    preview.show.assert_not_called()
    preview.selected_id = chosen.item_id
    launcher.isVisible = lambda:False
    button._ensure_confirmation_visibility()
    preview.show.assert_not_called()
    launcher.isVisible = lambda:True
    button._ensure_confirmation_visibility()
    preview.show.assert_called_once()


def test_remote_native_outside_click_cannot_hide_during_confirm():
    pending = object()
    hand = NS(_pending_confirmation=pending)
    remote = NS(isVisible=lambda:True,shuriken_button=hand)
    launcher = NS(remote_window=remote,dismiss_on_outside_click=True,
                  hide_remote=Mock(),dismiss=Mock(),
                  _remote_folder_root_menu=None,_remote_folder_opener=None,
                  _remote_page_menu=None)
    env = native_callbacks(launcher)
    env['dismiss_from_outside_click']()
    launcher.hide_remote.assert_not_called()
    launcher.dismiss.assert_not_called()
    hand._pending_confirmation = None
    env['dismiss_from_outside_click']()
    launcher.hide_remote.assert_called_once()
    launcher.dismiss.assert_called_once()


def test_launcher_app_deactivation_cannot_dismiss_pending_answer():
    qt = NS(ApplicationState=NS(ApplicationInactive=2,ApplicationActive=1))
    method_app_state = method('app.py','Launcher','app_state',
                              {'Qt':qt,'QApplication':NS(activeModalWidget=lambda:None)})
    hand=NS(_pending_confirmation=object())
    launcher=NS(_cloud_link_handoff=False,_filesystem_dialog_depth=0,
                _launch_context_menu=None,isVisible=lambda:True,
                remote_window=NS(shuriken_button=hand),
                dismiss_on_outside_click=True,hide_remote=Mock(),dismiss=Mock())
    method_app_state(launcher,2)
    launcher.hide_remote.assert_not_called()
    launcher.dismiss.assert_not_called()
    hand._pending_confirmation = None
    method_app_state(launcher,2)
    launcher.hide_remote.assert_called_once()
    launcher.dismiss.assert_called_once()


def test_launcher_hide_and_dismiss_guard_active_confirmation():
    launcher=NS(first_hand_confirmation_pending=lambda:True,
                _remote_kana_companion=None,remote_window=None)
    hide=method('app.py','Launcher','hide_remote')
    dismiss=method('app.py','Launcher','dismiss')
    assert hide(launcher) is None
    assert dismiss(launcher) is None
    # The explicit application Exit path alone bypasses this session lock.
    source=(ROOT/'src/app.py').read_text('utf8')
    assert 'self.dismiss(force=True);self.tray.hide();QApplication.quit()' in source


def test_remote_window_flags_changes_deferred_while_confirming():
    qt=NS(WindowType=NS(FramelessWindowHint=1,
                         WindowDoesNotAcceptFocus=2,Tool=4,Window=8,
                         WindowStaysOnTopHint=16))
    sync=method('launch_remote.py','LaunchRemote','sync_window_mode',{'Qt':qt})
    remote=NS(parent=lambda:NS(dismiss_on_outside_click=True),windowFlags=lambda:0,
              shuriken_button=NS(_pending_confirmation=object()),
              isVisible=lambda:True,pos=lambda:'position',
              setWindowFlags=Mock(),move=Mock(),show=Mock(),raise_=Mock())
    sync(remote)
    remote.setWindowFlags.assert_not_called()
    remote.shuriken_button._pending_confirmation=None
    sync(remote)
    remote.setWindowFlags.assert_called_once()


def test_visible_confirmation_panel_no_reorder_on_wheel_refresh():
    mod=load_button_module()
    mod.QPoint=lambda x,y:(x,y)
    preview=NS(circle_center=NS(x=lambda:260,y=lambda:160),
               mapToGlobal=lambda p:p,confirmation=None,_theme='light')
    panel=NS(_preview=None,isVisible=lambda:True,pos=lambda:(100,9),
             move=Mock(),show=Mock(),raise_=Mock(),update=Mock(),
             cancel_button=NS(setStyleSheet=Mock()),
             ok_button=NS(setStyleSheet=Mock()))
    mod.ShurikenConfirmationHitLayer.show_at(panel,preview)
    panel.move.assert_not_called()
    panel.show.assert_not_called()
    panel.raise_.assert_not_called()
    panel.update.assert_called_once()
