"""Regression: Press-to-answer lock, native preview stability and ghost Cancel.

Keep these guards independent of Windows-specific Qt native behavior. Full
Windows verification must still be performed separately with a real device.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_first_hand_wheel_confirmation_20261110 import make_flick, click, Wheel
from test_first_hand_persistent_confirmation_20261110 import method
from test_remote_current_outside_consistency_20261031 import native_callbacks

ROOT = Path(__file__).resolve().parents[1]


def test_app_deactivation_is_blocked_from_original_press():
    qt = NS(ApplicationState=NS(ApplicationInactive=2, ApplicationActive=1))
    app_state = method('app.py', 'Launcher', 'app_state',
                       {'Qt': qt, 'QApplication': NS(activeModalWidget=lambda:None)})
    hand = NS(_drag_start=(100,100), _pending_confirmation=None)
    launcher = NS(_cloud_link_handoff=False, _filesystem_dialog_depth=0,
                  _launch_context_menu=None, isVisible=lambda:True,
                  remote_window=NS(shuriken_button=hand),
                  dismiss_on_outside_click=True, hide_remote=Mock(), dismiss=Mock())
    app_state(launcher, 2)
    launcher.hide_remote.assert_not_called()
    launcher.dismiss.assert_not_called()
    hand._drag_start = None
    app_state(launcher, 2)
    launcher.hide_remote.assert_called_once()
    launcher.dismiss.assert_called_once()


def test_native_outside_click_is_blocked_from_original_press():
    hand = NS(_drag_start=(100,100), _pending_confirmation=None)
    launcher = NS(remote_window=NS(isVisible=lambda:True, shuriken_button=hand),
                  dismiss_on_outside_click=True, hide_remote=Mock(), dismiss=Mock(),
                  _remote_folder_root_menu=None, _remote_folder_opener=None,
                  _remote_page_menu=None)
    callback = native_callbacks(launcher)['dismiss_from_outside_click']
    callback()
    launcher.hide_remote.assert_not_called()
    launcher.dismiss.assert_not_called()
    hand._drag_start = None
    callback()
    launcher.hide_remote.assert_called_once()
    launcher.dismiss.assert_called_once()


def test_native_window_mode_switch_deferred_while_pressing():
    qt = NS(WindowType=NS(FramelessWindowHint=1,WindowDoesNotAcceptFocus=2,
                           Tool=4,Window=8,WindowStaysOnTopHint=16))
    sync = method('launch_remote.py','LaunchRemote','sync_window_mode',{'Qt':qt})
    hand=NS(_drag_start=(100,100), _pending_confirmation=None)
    remote=NS(parent=lambda:NS(dismiss_on_outside_click=True),
              windowFlags=lambda:0,shuriken_button=hand,
              isVisible=lambda:True,pos=lambda:'position',
              setWindowFlags=Mock(),move=Mock(),show=Mock(),raise_=Mock())
    sync(remote)
    remote.setWindowFlags.assert_not_called()
    hand._drag_start=None
    sync(remote)
    remote.setWindowFlags.assert_called_once()


def test_first_hand_lock_predicate_covers_drag_and_confirm():
    locked=method('app.py','Launcher','first_hand_confirmation_pending')
    hand=NS(_drag_start=(100,100), _pending_confirmation=None)
    launcher=NS(remote_window=NS(shuriken_button=hand))
    assert locked(launcher)
    hand._drag_start=None
    assert not locked(launcher)
    hand._pending_confirmation=object()
    assert locked(launcher)


def test_ghost_press_and_release_never_dismiss_default_cancel():
    button,_,chosen=make_flick(4,0,-45)
    original=button._pending_confirmation
    for _ in range(4):
        click(button, after_grace=False)
    assert button._pending_confirmation is original
    assert button._selected_entry is chosen
    button._preview.hide.assert_not_called()
    button.triggered.emit.assert_not_called()
    button.wheelEvent(Wheel(120))   # explicit Cancel selection
    click(button)
    assert button._pending_confirmation is None
    button.triggered.emit.assert_not_called()


def test_press_release_is_never_implicitly_ok_without_wheel():
    button,_,chosen=make_flick(4,0,-45)
    click(button, after_grace=False)
    assert button._pending_confirmation.candidate_id==chosen.item_id
    button.triggered.emit.assert_not_called()
    # A deliberate wheel DOWN then click remains the only button OK route.
    button.wheelEvent(Wheel(-120))
    click(button)
    button.triggered.emit.assert_called_once_with(chosen.item_id)


class Point:
    def __init__(self, x, y):self._x,self._y=x,y
    def x(self):return self._x
    def y(self):return self._y
    def __eq__(self,other):return isinstance(other,Point) and (self._x,self._y)==(other._x,other._y)

class Rect:
    def __init__(self, l,t,w,h): self.l,self.t,self.w,self.h=l,t,w,h
    def left(self):return self.l
    def right(self):return self.l+self.w-1
    def top(self):return self.t
    def bottom(self):return self.t+self.h-1


def test_mouse_jitter_does_not_reposition_native_preview():
    present = method('remote_shuriken.py','ShurikenPreview','present',{
        'QPoint':Point,'QPointF':Point,'QRect':Rect,
        'QApplication':NS(screenAt=lambda pos:NS(availableGeometry=lambda:Rect(0,0,1920,1080)),
                          primaryScreen=lambda:None),
        'theme_family':lambda text:text,
        'first_hand_trace':Mock(),
    })
    launcher=NS(color_theme='light')
    remote=NS(files_exp_theme='light')
    button=NS(launcher=launcher,parentWidget=lambda:remote,
              width=lambda:50,
              mapToGlobal=lambda pt:Point(500,600))
    # 500,513 guide center => 240,353 top-left in a 520x320 canvas.
    preview=NS(entries=['same-entry'],selected_id='',_theme='light',
               GAP_ABOVE_BUTTON=15,RADIUS=72,CANVAS_WIDTH=520,
               CANVAS_HEIGHT=320,circle_center=Point(260,160),
               pos=lambda:Point(240,353),move=Mock(),show=Mock(),
               isVisible=lambda:True,set_theme=Mock(),update=Mock())
    for _ in range(30):
        present(preview,button,['same-entry'],None)
    preview.move.assert_not_called()
    preview.show.assert_not_called()
    preview.update.assert_not_called()
    preview.set_theme.assert_not_called()
    # The eye may repaint, but the native tool must still NOT move.
    present(preview,button,['same-entry'],NS(item_id='up'))
    preview.move.assert_not_called()
    preview.update.assert_called_once()
    present(preview,button,['same-entry'],NS(item_id='up'))
    preview.update.assert_called_once()
