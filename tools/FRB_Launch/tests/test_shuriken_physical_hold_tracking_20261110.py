"""Regression of the physical 10:38 mouse lifecycle (replaces the retired timer polling tests).

The 16ms polling / GetAsyncKeyState implementation was NOT part of the user-verified
smooth controller. This deliberately tests the restored press/move/release behavior.
"""
import hashlib
from pathlib import Path
from unittest.mock import Mock
from test_shuriken_confirm_click_and_paint_20261105 import load_button_module, make_button, DummyEvent, Preview
from shuriken_model import ShurikenEntry, configured_entries, choose_entry

ROOT = Path(__file__).resolve().parents[1]
BASELINE_CLASS_SHA256 = "0edca2549b1a4855328c8a7552560e699692896eae481e51ab0975480da65535"


def test_first_hand_execution_requires_separate_wheel_and_click():
    source=(ROOT/'src/remote_shuriken.py').read_text('utf8')
    cls=source[source.index('class ShurikenButton('):]
    assert '_tracking_timer' not in cls
    assert '_physical_left_button_down' not in cls
    assert 'RELEASE_CONFIRM_SAMPLES' not in cls
    assert 'DRAG_DEADZONE = 14' in cls
    assert 'self._pending_confirmation = FirstHandConfirmation(' in cls
    assert 'self.triggered.emit(approved)' in cls


def test_four_way_mouse_move_only_selects_until_real_release_event():
    mod=load_button_module()
    mod.ShurikenPreview=Preview
    button,launch=make_button(mod)
    launch.shuriken_items.return_value=[
        ShurikenEntry(f'item_{direction}',direction,1,direction,(i+1)*10)
        for i,direction in enumerate(('up','right','down','left'))]
    button.mousePressEvent(DummyEvent())
    for x,y,expected in [(100,50,'up'),(150,100,'right'),(100,150,'down'),(50,100,'left'),(100,50,'up')]:
        button.mouseMoveEvent(DummyEvent(global_x=x, global_y=y))
        assert button._selected_entry.item_id=='item_'+expected
        assert button._drag_start is not None
        button.triggered.emit.assert_not_called()
    button.mouseReleaseEvent(DummyEvent(global_y=50))
    # Release only locks the shown choice; repeated release does nothing.
    button.triggered.emit.assert_not_called()
    assert button._pending_confirmation.candidate_id == 'item_up'
    button.mouseReleaseEvent(DummyEvent(global_y=50))
    button.triggered.emit.assert_not_called()


def test_click_without_move_cancels():
    mod=load_button_module()
    mod.ShurikenPreview=Preview
    button,_=make_button(mod)
    button.mousePressEvent(DummyEvent())
    button.mouseReleaseEvent(DummyEvent())
    button.triggered.emit.assert_not_called()


def test_four_action_order_still_clockwise_and_5th_ignored():
    rows=[dict(item_id=f'i{i}',title=f'Item{i}',shuriken_enabled=True,enabled=True,
               shuriken_order=(i+1)*10,shuriken_button_index=1,
               shuriken_direction='legacy_ignored') for i in range(5)]
    chosen=configured_entries({'items':rows})
    assert len(chosen)==4
    assert [e.direction for e in chosen]==['up','right','down','left']
    for entry,(dx,dy) in zip(chosen,[(0,-50),(50,0),(0,50),(-50,0)]):
        assert choose_entry(chosen,dx,dy)==entry
