"""Wheel-then-click on a normal context menu follows the same Remote cursor.

All tests are Qt-free models. Real Win11 Qt mouse routing requires user testing.
"""
from types import SimpleNamespace as NS

from test_remote_context_wheel_prototype_20261103 import FakeAction, FakeMenu, harness


class Click:
    def __init__(self, kind):
        self.kind = kind
        self.accepted = False

    def type(self):
        return self.kind

    def button(self):
        return 1  # Qt.MouseButton.LeftButton in the existing harness

    def globalPosition(self):
        return NS(toPoint=lambda: 'over-menu')

    def accept(self):
        self.accepted = True


def event(nav, menu, name):
    ev = Click(name)
    result = nav.eventFilter(menu, ev)
    return result, ev.accepted


def test_click_after_wheel_enters_selected_submenu_without_pointer_travel(harness):
    sub = FakeMenu(FakeAction('フォルダー'), FakeAction('テキスト文書'))
    sub.visible = False
    action = FakeAction('新規作成', submenu=sub)
    other = FakeAction('エクスプローラで開く')
    root, nav = harness.new_menu(FakeAction('切り取り'), action, other)
    harness.module.QCursor.pos = lambda: 'over-menu'
    harness.drain()
    assert nav.command('DOWN')
    assert nav._selected is action
    assert event(nav, root, 'press') == (True, True)
    assert event(nav, root, 'release') == (True, True)
    harness.drain()
    assert sub.isVisible()
    assert nav.current is sub
    assert sub.activeAction().text == 'フォルダー'
    assert action.trigger_calls == 0

    # A second stationary click should choose the child's current action.
    assert event(nav, root, 'press') == (True, True)
    assert event(nav, root, 'release') == (True, True)
    harness.drain()
    assert sub.actions()[0].trigger_calls == 1
    assert not root.isVisible()


def test_normal_click_before_wheel_keeps_native_qmenu_behavior(harness):
    root, nav = harness.new_menu(FakeAction('切り取り'))
    harness.module.QCursor.pos = lambda: 'over-menu'
    harness.drain()
    assert event(nav, root, 'press') == (False, False)
    assert event(nav, root, 'release') == (False, False)
    assert root.isVisible()


def test_pointer_motion_after_wheel_returns_normal_mouse_click(harness):
    root, nav = harness.new_menu(FakeAction('切り取り'), FakeAction('新規作成'))
    harness.module.QCursor.pos = lambda: 'over-menu'
    harness.drain()
    nav.command('DOWN')
    assert nav._wheel_owned_selection
    # Physical pointer motion even to another menu row cancels wheel ownership.
    harness.module.QCursor.pos = lambda: 'submenu-area'
    assert event(nav, root, 'press') == (False, False)
    assert not nav._wheel_owned_selection
    assert event(nav, root, 'release') == (False, False)


def test_press_after_wheel_on_unrelated_surface_is_not_captured(harness):
    root, nav = harness.new_menu(FakeAction('切り取り'))
    harness.module.QCursor.pos = lambda: 'over-menu'
    harness.drain()
    nav.command('DOWN')
    # While mouse leaves the context popup, normal controls remain operable.
    harness.module.QCursor.pos = lambda: 'files-outside'
    assert event(nav, root, 'press') == (False, False)
