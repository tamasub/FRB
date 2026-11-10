"""First-hand safety: lost Qt drag events must not cause early execution.

These stand-in tests exercise the event lifecycle without requiring PySide6.
Actual Windows hardware capture must still be checked by a user on Windows.
"""
from types import SimpleNamespace as NS
from unittest.mock import Mock

from test_shuriken_confirm_click_and_paint_20261105 import (
    DummyEvent, load_button_module, make_button,
)
from shuriken_model import ShurikenEntry, configured_entries


def setup(directions=('up',)):
    mod = load_button_module()
    mod.ShurikenPreview = type('Preview', (), {
        '__init__': lambda self, *a: (setattr(self, 'present', Mock()),
                                      setattr(self, 'hide', Mock())) and None,
    })
    button, launcher = make_button(mod)
    launcher.shuriken_items.return_value = [
        ShurikenEntry(f'item-{d}', d, 1, d, i * 10)
        for i, d in enumerate(directions)
    ]
    return mod, button, launcher


def point(x, y):
    return NS(x=lambda: x, y=lambda: y)


def test_vertical_drag_follows_physical_cursor_when_qt_moves_stop():
    mod, button, _ = setup(('up',))
    down = {'held': True}
    cursor = {'at': (100, 100)}
    mod._physical_left_button_down = lambda: down['held']
    mod.QCursor.pos = lambda: point(*cursor['at'])
    button.mousePressEvent(DummyEvent())
    assert button._tracking_timer.active
    assert button._tracking_timer.interval == 16
    # No mouseMoveEvent at all: Qt lost its drag grab when the popup showed.
    cursor['at'] = (100, 62)  # UP is negative dy.
    button._poll_drag()
    assert button._selected_entry.item_id == 'item-up'
    button.triggered.emit.assert_not_called()
    # Cursor travels to the BOTTOM with button still pressed. Eye returns.
    cursor['at'] = (100, 160)
    button._poll_drag()
    assert button._selected_entry is None
    button.triggered.emit.assert_not_called()
    # Move back up and truly release; only a Qt release commits.
    cursor['at'] = (100, 40)
    button._poll_drag()
    assert button._selected_entry.item_id == 'item-up'
    down['held'] = False
    button._poll_drag()
    button.triggered.emit.assert_not_called()
    assert button._tracking_timer.active
    button.mouseReleaseEvent(DummyEvent(global_y=40))
    button.triggered.emit.assert_not_called()
    for _ in range(button.RELEASE_CONFIRM_SAMPLES):
        button._poll_drag()
    button.triggered.emit.assert_called_once_with('item-up')
    assert not button._tracking_timer.active
    button._poll_drag()
    button.triggered.emit.assert_called_once_with('item-up')


def test_stray_qt_release_while_physical_button_is_down_never_executes():
    mod, button, _ = setup(('up', 'right', 'down', 'left'))
    down = {'held': True}
    cursor = {'at': (100, 100)}
    mod._physical_left_button_down = lambda: down['held']
    mod.QCursor.pos = lambda: point(*cursor['at'])
    button.mousePressEvent(DummyEvent())
    cursor['at'] = (100, 50)
    button._poll_drag()
    assert button._selected_entry.item_id == 'item-up'
    # Synthetic Qt mouseRelease while the physical left button is held.
    stray = DummyEvent(global_y=50)
    button.mouseReleaseEvent(stray)
    assert stray.accepted
    assert button._tracking_timer.active
    assert button._selected_entry.item_id == 'item-up'
    button.triggered.emit.assert_not_called()
    # Qt events have stopped: physical cursor still changes target.
    cursor['at'] = (100, 160)
    button._poll_drag()
    assert button._selected_entry.item_id == 'item-down'
    button.triggered.emit.assert_not_called()
    down['held'] = False
    button._poll_drag()
    button.triggered.emit.assert_not_called()
    button.mouseReleaseEvent(DummyEvent(global_y=160))
    button.triggered.emit.assert_not_called()
    for _ in range(button.RELEASE_CONFIRM_SAMPLES):
        button._poll_drag()
    button.triggered.emit.assert_called_once_with('item-down')


def test_idle_and_wrong_direction_cancel_without_commit():
    mod, button, _ = setup(('up',))
    down = {'held': True}
    cursor = {'at': (100, 100)}
    mod._physical_left_button_down = lambda: down['held']
    mod.QCursor.pos = lambda: point(*cursor['at'])
    button.mousePressEvent(DummyEvent())
    for direction in [(100, 100), (100, 180), (180, 100), (20, 100)]:
        cursor['at'] = direction
        button._poll_drag()
        assert button._selected_entry is None
    down['held'] = False
    button._poll_drag()
    button.triggered.emit.assert_not_called()


def test_hiding_button_cancels_drag_and_stops_physical_poll():
    mod, button, _ = setup(('up',))
    mod._physical_left_button_down = lambda: True
    button.mousePressEvent(DummyEvent())
    button.hideEvent(DummyEvent())
    assert not button._tracking_timer.active
    assert button._selected_entry is None
    button._poll_drag()
    button.triggered.emit.assert_not_called()


def test_four_item_clockwise_mapping_unchanged():
    items = [dict(item_id=str(i), title=str(i), shuriken_enabled=True,
                  enabled=True, shuriken_order=i * 10, shuriken_button_index=1)
             for i in range(6)]
    assert [r.direction for r in configured_entries({'items': items})] == [
        'up', 'right', 'down', 'left']


def test_windows_button_state_uses_native_physical_state(monkeypatch):
    """A native-held button beats a stray Qt release/capture-loss report."""
    import ctypes
    mod = load_button_module()
    monkeypatch.setattr(mod.sys, 'platform', 'win32')
    keys = {'pressed': True, 'requested': []}
    def async_state(vk):
        keys['requested'].append(vk)
        return 0x8000 if keys['pressed'] else 0
    monkeypatch.setattr(ctypes, 'windll', NS(user32=NS(GetAsyncKeyState=async_state)),
                        raising=False)
    assert mod._physical_left_button_down()
    keys['pressed'] = False
    assert not mod._physical_left_button_down()
    assert keys['requested'] == [1, 1]


def test_unchanged_eye_does_not_reopen_preview_on_every_poll():
    mod, button, _ = setup(('up',))
    mod._physical_left_button_down = lambda: True
    mod.QCursor.pos = lambda: point(100, 48)
    button.mousePressEvent(DummyEvent())
    for _ in range(15):
        button._poll_drag()
    assert button._selected_entry.item_id == 'item-up'
    assert button._preview.present.call_count == 2  # one initial, one change
    button.triggered.emit.assert_not_called()


def test_transient_or_missing_release_samples_cannot_execute():
    mod, button, _ = setup(('up',))
    down = {'held': True}
    cursor = {'at': (100, 100)}
    mod._physical_left_button_down = lambda: down['held']
    mod.QCursor.pos = lambda: point(*cursor['at'])
    button.mousePressEvent(DummyEvent())
    cursor['at'] = (100, 88)  # only 12px within the physical button
    button._poll_drag()
    assert button._selected_entry.item_id == 'item-up'
    # A one-off false reading from Windows cannot fire the action.
    down['held'] = False
    button._poll_drag()
    button.triggered.emit.assert_not_called()
    down['held'] = True
    button._poll_drag()
    assert button._drag_start is not None
    # Qt release is missing: only CANCEL the drag after prolonged zero state.
    down['held'] = False
    for _ in range(button.MISSING_RELEASE_CANCEL_SAMPLES):
        button._poll_drag()
    assert button._drag_start is None
    button.triggered.emit.assert_not_called()
    assert not button._tracking_timer.active


def test_preview_transparent_window_does_not_cover_button():
    mod = load_button_module()
    preview = mod.ShurikenPreview
    # Under normal screen conditions preview is anchored above button:
    # circle center = button.top - GAP - RADIUS, and canvas extends half-height.
    assert preview.CANVAS_HEIGHT // 2 < preview.GAP_ABOVE_BUTTON + preview.RADIUS
    assert preview.RADIUS + 9 < preview.CANVAS_HEIGHT // 2
    # The gesture is confined to 50x46 button, so 14px was too large.
    assert mod.ShurikenButton.DRAG_DEADZONE == 8
