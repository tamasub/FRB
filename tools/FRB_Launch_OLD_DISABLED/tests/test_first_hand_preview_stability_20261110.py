"""The 10:38 preview is a separate transparent non-interactive tool window.

Known remaining issue: occasional preview flicker in Windows. This test does not
claim flicker has been fixed. Existing approved eye motion is more important.
"""
from pathlib import Path
from unittest.mock import Mock
from test_shuriken_confirm_click_and_paint_20261105 import load_button_module, make_button, DummyEvent, Preview
from shuriken_model import ShurikenEntry, current_indicator_position


def test_preview_never_takes_focus_or_input():
    source=(Path(__file__).resolve().parents[1]/'src/remote_shuriken.py').read_text('utf8')
    assert 'Qt.WindowType.WindowTransparentForInput' in source
    assert 'Qt.WindowType.WindowDoesNotAcceptFocus' in source
    assert 'Qt.WidgetAttribute.WA_TransparentForMouseEvents' in source
    assert 'Qt.WidgetAttribute.WA_ShowWithoutActivating' in source


def test_preview_selection_tracks_last_move_without_triggering_action():
    mod=load_button_module()
    mod.ShurikenPreview=Preview
    button,launcher=make_button(mod)
    launcher.shuriken_items.return_value=[
        ShurikenEntry('u','UP',1,'up',10), ShurikenEntry('r','RIGHT',1,'right',20),
        ShurikenEntry('d','DOWN',1,'down',30), ShurikenEntry('l','LEFT',1,'left',40)]
    button.mousePressEvent(DummyEvent())
    assert button._preview.present.call_count==1
    for x,y,target in [(100,50,'u'),(100,150,'d'),(150,100,'r'),(50,100,'l')]:
        button.mouseMoveEvent(DummyEvent(global_x=x,global_y=y))
        assert button._selected_entry.item_id==target
        assert current_indicator_position(button._entries,target)!=(0,0)
        button.triggered.emit.assert_not_called()
    assert button._preview.hide.call_count==0
    button.mouseReleaseEvent(DummyEvent(global_x=50,global_y=100))
    button.triggered.emit.assert_not_called()
    assert button._pending_confirmation.candidate_id == 'l'
    button._preview.hide.assert_not_called()
