"""Regression for the Nov 8 report: wheel cursor jumps back to 新規作成.

Qt-free models; Windows/Qt menu behavior still requires a real-device check.
"""
from types import SimpleNamespace as NS

from test_remote_context_wheel_prototype_20261103 import (  # noqa: F401
    FakeAction, FakeMenu, Signal, harness,
)


class Hovered:
    def __init__(self):
        self.handlers = []

    def connect(self, callback):
        self.handlers.append(callback)

    def disconnect(self, callback):
        self.handlers.remove(callback)

    def emit(self, action):
        for callback in tuple(self.handlers):
            callback(action)


def setup_wheel_menu(harness):
    first = FakeAction('切り取り')
    new_action = FakeAction('新規作成')
    last = FakeAction('エクスプローラで開く')
    root = FakeMenu(first, new_action, last)
    root.hovered = Hovered()
    submenu = FakeMenu(FakeAction('フォルダー'))
    submenu.visible = False
    submenu.aboutToShow = Signal()
    root.findChildren = lambda cls: [submenu]
    nav = harness.module.RemoteContextWheel(harness.launcher, root)
    harness.launcher._remote_context_wheel = nav
    harness.drain()
    nav.command('DOWN')
    nav.command('DOWN')
    assert nav._selected is last
    assert root.activeAction() is last
    return root, nav, new_action, last, submenu


def test_stationary_pointer_hover_does_not_steal_wheel_cursor(harness):
    root, nav, new_action, last, sub = setup_wheel_menu(harness)
    # Reproduce native Qt replacing the wheel cursor with the action under
    # the stationary pointer; it must NOT change the controller selection.
    root.setActiveAction(new_action)
    root.hovered.emit(new_action)
    harness.drain()
    assert nav._selected is last
    assert root.activeAction() is last
    assert nav.current is root


def test_stationary_pointer_cannot_open_new_submenu_automatically(harness):
    root, nav, new_action, last, sub = setup_wheel_menu(harness)
    sub.visible = True  # QMenu has popped a child from an old hover timer.
    sub.aboutToShow.emit()
    harness.drain()
    assert not sub.isVisible()
    assert root.activeAction() is last
    assert nav.current is root


def test_explicit_right_does_open_selected_submenu(harness):
    folder = FakeMenu(FakeAction('フォルダー'))
    folder.visible = False
    folder.aboutToShow = Signal()
    action = FakeAction('新規作成', submenu=folder)
    root, nav = harness.new_menu(FakeAction('切り取り'), action)
    root.findChildren = lambda cls: [folder]
    nav._install_hover_guards()
    old_popup = folder.popup
    def popup(point):
        folder.aboutToShow.emit()
        old_popup(point)
    folder.popup = popup
    harness.drain()
    nav.command('DOWN')
    nav.command('RIGHT')
    harness.drain()
    assert folder.isVisible()
    assert nav.current is folder
    assert folder.activeAction().text == 'フォルダー'
    nav.command('LEFT')
    assert nav.current is root
    assert not folder.isVisible()


def test_real_pointer_motion_returns_ownership_to_native_mouse(harness):
    root, nav, new_action, last, sub = setup_wheel_menu(harness)
    # A real pointer move (rather than QMenu's synthetic hover event) should
    # restore normal clickable/hoverable menu behavior.
    harness.module.QCursor.pos = lambda: 'physically-moved'
    root.setActiveAction(new_action)
    root.hovered.emit(new_action)
    harness.drain()
    assert root.activeAction() is new_action
    assert not nav._wheel_owned_selection
    sub.visible = True
    sub.aboutToShow.emit()
    harness.drain()
    assert sub.isVisible()


def test_qt_synthetic_mouse_move_is_blocked_until_cursor_really_moves(harness):
    root, nav, new_action, last, sub = setup_wheel_menu(harness)
    harness.module.QEvent.Type.MouseMove = 'mouse-move'
    event = NS(type=lambda: 'mouse-move', accepted=False)
    event.accept = lambda: setattr(event, 'accepted', True)
    assert nav.eventFilter(root, event) is True
    assert event.accepted
    harness.module.QCursor.pos = lambda: 'real-move'
    event.accepted = False
    assert nav.eventFilter(root, event) is False
    assert not event.accepted


def test_persistent_settings_menu_does_not_retain_old_hover_handlers(harness):
    root, nav, new_action, last, sub = setup_wheel_menu(harness)
    assert len(root.hovered.handlers) == 1
    nav.stop()
    assert len(root.hovered.handlers) == 0
    assert nav not in harness.app.filters
