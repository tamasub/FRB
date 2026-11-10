"""Regression: preview changes never re-position an active tool window.

Tests use tiny Qt stand-ins; Windows compositing still needs physical QA.
"""
from unittest.mock import Mock
from test_shuriken_confirm_click_and_paint_20261105 import load_button_module, make_button, DummyEvent
from shuriken_model import ShurikenEntry


def point(x,y):
    from types import SimpleNamespace
    return SimpleNamespace(x=lambda:x, y=lambda:y)


def test_visible_preview_eye_update_never_repositions_or_resurfaces_window():
    mod = load_button_module()
    preview = object.__new__(mod.ShurikenPreview)
    owner=object()
    preview._present_owner=owner
    preview.entries=[]
    preview.selected_id=''
    preview.isVisible=lambda:True
    preview.update=Mock()
    preview.move=Mock(side_effect=AssertionError('visible preview must NOT move'))
    preview.show=Mock(side_effect=AssertionError('visible preview must NOT show again'))
    entry=ShurikenEntry('test','test',1,'up',10)
    preview.present(owner,[entry],entry)
    assert preview.selected_id=='test'
    preview.update.assert_called_once_with()
    preview.move.assert_not_called()
    preview.show.assert_not_called()


def test_spurious_native_button_up_does_not_close_preview_or_launch():
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self,*a:(setattr(self,'present',Mock()),setattr(self,'hide',Mock())) and None})
    button,launcher=make_button(mod)
    down={'value':True}
    mod._physical_left_button_down=lambda:down['value']
    mod.QCursor.pos=lambda:point(100,60)
    button.mousePressEvent(DummyEvent())
    button._poll_drag()
    assert button._selected_entry is not None
    for _ in range(4):
        down['value']=False
        button._poll_drag()
        down['value']=True
        button._poll_drag()
    assert button._drag_start is not None
    assert button._preview.hide.call_count == 0
    button.triggered.emit.assert_not_called()


def test_suspected_release_recovers_if_physical_press_continues():
    mod=load_button_module()
    mod.ShurikenPreview=type('Preview', (), {
        '__init__':lambda self,*a:(setattr(self,'present',Mock()),setattr(self,'hide',Mock())) and None})
    button,_=make_button(mod)
    down={'value':True}
    mod._physical_left_button_down=lambda:down['value']
    mod.QCursor.pos=lambda:point(100,60)
    button.mousePressEvent(DummyEvent())
    button._poll_drag()
    down['value']=False
    button.mouseReleaseEvent(DummyEvent())
    for _ in range(button.RELEASE_CONFIRM_SAMPLES-1):
        button._poll_drag()
    button.triggered.emit.assert_not_called()
    down['value']=True
    button._poll_drag()
    assert not button._release_candidate
    assert button._drag_start is not None
    assert button._preview.hide.call_count == 0
    button.triggered.emit.assert_not_called()


def test_held_release_does_not_execute_and_traced_hides_are_explicit():
    mod=load_button_module()
    mod.ShurikenPreview=type('Preview', (), {
        '__init__':lambda self,*a:(setattr(self,'present',Mock()),setattr(self,'hide',Mock())) and None})
    button,_=make_button(mod)
    mod._physical_left_button_down=lambda:True
    button.mousePressEvent(DummyEvent())
    button.mouseMoveEvent(DummyEvent(global_y=50))
    button.mouseReleaseEvent(DummyEvent(global_y=50))
    assert button._drag_start is not None
    button.triggered.emit.assert_not_called()
    assert button._preview.hide.call_count == 0
