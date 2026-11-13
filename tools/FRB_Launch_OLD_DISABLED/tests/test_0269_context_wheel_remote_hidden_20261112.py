"""A visible pointer menu owns wheel/click even without the floating Remote."""
from test_remote_context_wheel_prototype_20261103 import FakeAction, harness  # noqa: F401


def test_hidden_remote_menu_wheel_target_and_click(harness):
    actions = [FakeAction('前'), FakeAction('削除')]
    menu, controller = harness.new_menu(*actions)
    harness.drain()
    harness.remote.isVisible = lambda: False
    harness.module.QCursor.pos = lambda: 'over-menu'
    assert controller._hit('pad') is None
    assert controller._wheel_target('over-menu') == 'menu'
    assert controller._wheel_target('outside') is None
    # Same context-menu QAction cursor. No remote window should be shown.
    controller.command('DOWN')
    assert controller._selected is actions[1]
    assert controller.command('CLICK')
    assert not menu.isVisible()
    harness.drain()
    assert actions[1].trigger_calls == 1
