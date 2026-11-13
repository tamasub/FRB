"""Windows mouse-pointer-rod v0.2: deterministic semantic tests without Windows GUI.

The user must validate actual menu z-order and double-click against Windows.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import mouse_pointer_rod_windows as native


def extract(name, cls='MousePointerRodPad', env=None):
    tree=ast.parse((ROOT/'src/mouse_pointer_rod.py').read_text('utf-8'))
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    fn=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name==name)
    scope=dict(env or {})
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'test_extract','exec'),scope)
    return scope[name]


def test_single_click_waits_for_system_double_interval():
    queue=extract('_queue_native_single_click',env={
        'QApplication': NS(styleHints=lambda: NS(mouseDoubleClickInterval=lambda: 420))
    })
    pad=NS(_pending_native_tip=None,tip_global=lambda:(44,55),
           _native_single_timer=NS(start=Mock()))
    queue(pad)
    assert pad._pending_native_tip==(44,55)
    pad._native_single_timer.start.assert_called_once_with(420)


def test_single_click_flushes_saved_tip_not_latest_tip():
    flush=extract('_flush_pending_native_click')
    launch=object()
    remote=NS(parent=lambda:launch)
    cb=Mock(return_value=True)
    pad=NS(_pending_native_tip=(110,120),_enabled=True,
           _windows_click_mode=True,parentWidget=lambda:remote,
           _cursor_on_blue=lambda: True,_dispatch_windows_click=cb)
    flush(pad)
    assert pad._pending_native_tip is None
    cb.assert_called_once_with('select',remote,launch,target_override=(110,120))
    flush(pad)
    assert cb.call_count==1


def test_pending_click_cancelled_on_mode_change_or_double():
    cancel=extract('_cancel_pending_native_click')
    pending=NS(_pending_native_tip=(110,120),_native_single_timer=NS(stop=Mock()))
    cancel(pending)
    assert pending._pending_native_tip is None
    pending._native_single_timer.stop.assert_called_once()


def test_second_physical_release_dispatches_native_double_not_triple():
    release=extract('mouseReleaseEvent',env={
        'Qt': NS(MouseButton=NS(LeftButton=1))
    })
    dispatch=Mock()
    pad=NS(_enabled=True,_windows_click_mode=True,_left_pressed=True,
           _wheel_during_press=False,_double_pending=True,
           rect=lambda:NS(contains=lambda p: True),_wheel_pad=None,
           _cancel_pending_native_click=Mock(),
           _dispatch_tip_action=dispatch,_queue_native_single_click=Mock())
    evt=NS(button=lambda:1,position=lambda:NS(toPoint=lambda:(4,5)),accept=Mock())
    release(pad,evt)
    pad._cancel_pending_native_click.assert_called_once()
    dispatch.assert_called_once_with('double')
    pad._queue_native_single_click.assert_not_called()


def test_first_physical_release_queues_and_does_not_send_windows_click():
    release=extract('mouseReleaseEvent',env={
        'Qt': NS(MouseButton=NS(LeftButton=1))
    })
    pad=NS(_enabled=True,_windows_click_mode=True,_left_pressed=True,
           _wheel_during_press=False,_double_pending=False,
           rect=lambda:NS(contains=lambda p: True),_wheel_pad=None,
           _dispatch_tip_action=Mock(),_queue_native_single_click=Mock())
    evt=NS(button=lambda:1,position=lambda:NS(toPoint=lambda:(4,5)),accept=Mock())
    release(pad,evt)
    pad._queue_native_single_click.assert_called_once()
    pad._dispatch_tip_action.assert_not_called()


def test_rod_recovers_after_popup_captures_hover():
    watch=extract('_watch_windows_hover')
    pad=NS(_enabled=True,_windows_click_mode=True,isVisible=lambda:True,
           _cursor_on_blue=lambda:True,_sync_hover=Mock(),
           _aim_visible=True,refresh_position=Mock())
    watch(pad)
    pad._sync_hover.assert_called_once()
    pad.refresh_position.assert_called_once()


def test_rod_does_not_show_when_real_pointer_leaves():
    watch=extract('_watch_windows_hover')
    pad=NS(_enabled=True,_windows_click_mode=True,isVisible=lambda:True,
           _cursor_on_blue=lambda:False,_native_warp_guard=False,
           _stop_aiming=Mock())
    watch(pad)
    pad._stop_aiming.assert_called_once()


def test_warp_leave_is_not_mistaken_for_real_leave():
    leave=extract('leaveEvent',env={'super':lambda: NS(leaveEvent=lambda e:None)})
    pad=NS(_native_warp_guard=True,_cursor_on_blue=lambda:True,_stop_aiming=Mock())
    leave(pad,object())
    pad._stop_aiming.assert_not_called()
    pad._native_warp_guard=False
    leave(pad,object())
    pad._stop_aiming.assert_called_once()


def test_native_double_second_send_failure_still_restores_cursor(monkeypatch):
    class Position:
        def __init__(self,x,y): self.x,self.y=x,y
        def __sub__(self,other):
            return NS(manhattanLength=lambda:abs(self.x-other.x)+abs(self.y-other.y))
    class Cursor:
        current=Position(10,20)
        @classmethod
        def pos(cls): return cls.current
        @classmethod
        def setPos(cls,new): cls.current=new
    shots=[]
    def click():
        shots.append((Cursor.current.x,Cursor.current.y))
        if len(shots)==2: raise OSError('blocked second click')
    monkeypatch.setattr(native,'send_left_click',click)
    monkeypatch.setattr(native.time,'sleep',lambda _:None)
    try:
        native.click_at(Position(100,200),cursor=Cursor,double=True)
    except OSError:
        pass
    else:
        assert False,'second native input must report failure'
    assert shots == [(100,200),(100,200)]
    assert (Cursor.current.x,Cursor.current.y)==(10,20)


def test_overlay_is_topmost_and_mouse_transparent_and_compact():
    src=(ROOT/'src/mouse_pointer_rod.py').read_text('utf-8')
    assert 'Qt.WindowType.WindowStaysOnTopHint' in src
    assert 'Qt.WindowType.WindowTransparentForInput' in src
    assert 'self.raise_()' in src
    assert "font.setPixelSize(10)" in src
    assert "QRectF(6, 47, self.width() - 12, 12)" in src
    assert 'QTimer.singleShot(85, self._finish_native_warp)' in src
