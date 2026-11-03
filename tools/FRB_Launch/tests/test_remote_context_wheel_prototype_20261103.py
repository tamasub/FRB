"""FRB Launch: Remote-only Files List QMenu wheel prototype (without Qt runtime)."""
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
REMOTE = (ROOT / 'src/launch_remote.py').read_text(encoding='utf-8')
MODULE = ROOT / 'src/remote_context_wheel.py'


class Signal:
    def __init__(self):
        self.handlers = []

    def connect(self, handler):
        self.handlers.append(handler)

    def emit(self):
        for handler in tuple(self.handlers):
            handler()


class FakeAction:
    def __init__(self, text, *, enabled=True, visible=True, separator=False, submenu=None):
        self.text = text
        self.enabled = enabled
        self.visible = visible
        self.separator = separator
        self.submenu = submenu
        self.trigger_calls = 0

    def isVisible(self):
        return self.visible

    def isEnabled(self):
        return self.enabled

    def isSeparator(self):
        return self.separator

    def menu(self):
        return self.submenu

    def trigger(self):
        self.trigger_calls += 1


class FakeMenu:
    def __init__(self, *actions):
        self._actions = list(actions)
        self._active = None
        self.visible = True
        self.aboutToHide = Signal()
        self.popup_positions = []

    def actions(self):
        return self._actions

    def isVisible(self):
        return self.visible

    def activeAction(self):
        return self._active

    def setActiveAction(self, action):
        self._active = action

    def actionGeometry(self, action):
        return NS(topRight=lambda: (3, 4))

    def mapToGlobal(self, point):
        return point

    def popup(self, point):
        self.visible = True
        self.popup_positions.append(point)

    def close(self):
        if self.visible:
            self.visible = False
            self.aboutToHide.emit()


class FakeApplication:
    def __init__(self):
        self.filters = []

    def installEventFilter(self, event_filter):
        self.filters.append(event_filter)

    def removeEventFilter(self, event_filter):
        self.filters.remove(event_filter)


@pytest.fixture
def harness(monkeypatch):
    app = FakeApplication()
    jobs = []
    pyqt = ModuleType('PySide6')
    core = ModuleType('PySide6.QtCore')
    gui = ModuleType('PySide6.QtGui')
    widgets = ModuleType('PySide6.QtWidgets')
    class QObject:
        def __init__(self, parent=None):
            self.parent = parent
            self.deleted = False
        def deleteLater(self):
            self.deleted = True
    core.QObject = QObject
    core.QEvent = NS(Type=NS(Wheel='wheel', MouseButtonPress='press',
                             MouseButtonRelease='release', MouseButtonDblClick='double'))
    core.QTimer = NS(singleShot=lambda delay, cb: jobs.append(cb))
    core.Qt = NS(MouseButton=NS(LeftButton=1))
    gui.QCursor = NS(pos=lambda: 'outside')
    widgets.QApplication = NS(instance=lambda: app)
    for name, module in [('PySide6', pyqt), ('PySide6.QtCore', core),
                         ('PySide6.QtGui', gui), ('PySide6.QtWidgets', widgets)]:
        monkeypatch.setitem(__import__('sys').modules, name, module)
    spec = importlib.util.spec_from_file_location('remote_context_wheel_under_test', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    label = NS(value='操作先：Files List')
    label.text = lambda: label.value
    label.setText = lambda value: setattr(label, 'value', value)
    class Widget:
        def __init__(self, target):
            self.target = target
        def isVisible(self):
            return True
        def rect(self):
            return NS(contains=lambda point: point == self.target)
        def mapFromGlobal(self, point):
            return point
    pad = Widget('pad')
    remote = NS(isVisible=lambda: True, pad=pad, area_label=label,
                left_button=Widget('left'), right_button=Widget('right'))
    launcher = NS(remote_window=remote, _remote_context_wheel=None)
    def new_menu(*actions):
        menu = FakeMenu(*actions)
        controller = module.RemoteContextWheel(launcher, menu)
        launcher._remote_context_wheel = controller
        return menu, controller
    def drain():
        while jobs:
            jobs.pop(0)()
    return NS(module=module, app=app, jobs=jobs, label=label,
              launcher=launcher, remote=remote, new_menu=new_menu, drain=drain)


def test_skips_disabled_and_separators_and_wraps(harness):
    a = FakeAction('コピー')
    disabled = FakeAction('貼り付け', enabled=False)
    separator = FakeAction('-', separator=True)
    b = FakeAction('削除')
    menu, controller = harness.new_menu(a, disabled, separator, b)
    harness.drain()
    assert menu.activeAction() is a
    controller.command('DOWN')
    assert menu.activeAction() is b
    controller.command('DOWN')
    assert menu.activeAction() is a
    controller.command('UP')
    assert menu.activeAction() is b
    assert a.trigger_calls == b.trigger_calls == 0


def test_remote_center_click_executes_original_action_only_after_menu_is_closed(harness):
    a = FakeAction('削除')
    menu, controller = harness.new_menu(a)
    harness.drain()
    assert controller.command('CLICK') is True
    assert not menu.isVisible()
    assert harness.launcher._remote_context_wheel is None
    assert harness.label.text() == '操作先：Files List'
    assert a.trigger_calls == 0  # Closing the native grab precedes the action.
    harness.drain()
    assert a.trigger_calls == 1


def test_left_at_root_cancels_without_trigger(harness):
    a = FakeAction('削除')
    menu, controller = harness.new_menu(a)
    harness.drain()
    assert controller.command('LEFT') is True
    assert not menu.isVisible()
    harness.drain()
    assert a.trigger_calls == 0


def test_right_opens_submenu_without_executing_anything(harness):
    leaf = FakeAction('テキストファイル')
    sub = FakeMenu(leaf)
    sub.visible = False
    folder = FakeAction('新規作成', submenu=sub)
    menu, controller = harness.new_menu(folder)
    harness.drain()
    assert controller.command('RIGHT') is True
    harness.drain()
    assert sub.isVisible()
    assert sub.activeAction() is leaf
    assert controller.command('LEFT') is True
    assert not sub.isVisible()
    assert menu.isVisible()
    assert controller.current is menu


def test_popup_grab_wheel_redirected_by_pointer_position(harness):
    a = FakeAction('コピー')
    b = FakeAction('削除')
    menu, controller = harness.new_menu(a, b)
    harness.drain()
    class FakeEvent:
        def __init__(self, kind, point='pad', button=1):
            self.kind, self.point, self.which = kind, point, button
            self.accepted = False
        def type(self):
            return self.kind
        def globalPosition(self):
            return NS(toPoint=lambda: self.point)
        def button(self):
            return self.which
        def accept(self):
            self.accepted = True
    def emit_remote_wheel(event):
        controller.command('DOWN')
        event.accept()
    harness.remote.pad.wheelEvent = emit_remote_wheel
    event = FakeEvent('wheel')
    assert controller.eventFilter(menu, event) is True
    assert event.accepted
    assert menu.activeAction() is b
    # Ordinary wheel events *over the menu itself* retain native QMenu handling.
    event = FakeEvent('wheel', point='over-menu')
    assert controller.eventFilter(menu, event) is False
    assert menu.activeAction() is b
    press = FakeEvent('press')
    release = FakeEvent('release')
    assert controller.eventFilter(menu, press) is True
    assert controller.eventFilter(menu, release) is True
    harness.drain()
    assert b.trigger_calls == 1
    assert a.trigger_calls == 0


def test_popup_grab_left_right_clicks_still_route_to_actual_menu(harness):
    actions = [FakeAction('コピー'), FakeAction('削除')]
    menu, controller = harness.new_menu(*actions)
    harness.drain()
    def evt(kind, point):
        return NS(type=lambda: kind, globalPosition=lambda: NS(toPoint=lambda: point),
                  button=lambda: 1, accept=lambda: None)
    assert controller.eventFilter(menu, evt('press', 'right')) is True
    assert controller.eventFilter(menu, evt('release', 'right')) is True
    assert menu.isVisible()  # A leaf must never execute on RIGHT.
    assert controller.eventFilter(menu, evt('press', 'left')) is True
    assert controller.eventFilter(menu, evt('release', 'left')) is True
    assert not menu.isVisible()  # LEFT closes safely.
    assert all(a.trigger_calls == 0 for a in actions)


def test_remote_opened_files_list_only_and_normal_context_unchanged():
    assert "from remote_context_wheel import RemoteContextWheel" in APP
    assert "if pane is view.middle:\n                self._enable_remote_context_wheel()" in APP
    assert "menu_wheel = getattr(self, '_remote_context_wheel', None)" in APP
    assert "if menu_wheel is not None and menu_wheel.command(command):" in APP
    assert "self.left_button = self._button('←'" in REMOTE
    assert "self.right_button = self._button('→'" in REMOTE
    assert "self._launch_context_menu = menu" in APP


def test_remote_cursor_survives_native_qmenu_clearing_active_highlight(harness):
    a, b, c = (FakeAction(x) for x in ('開く', 'コピー', '削除'))
    menu, controller = harness.new_menu(a, b, c)
    harness.drain()
    controller.command('DOWN')
    assert menu.activeAction() is b
    menu.setActiveAction(None)  # Windows popup hover/focus loss can do this.
    controller.command('DOWN')
    assert menu.activeAction() is c  # Continue from b, not from first item.


def test_no_action_is_executable_when_all_entries_disabled(harness):
    a = FakeAction('貼り付け', enabled=False)
    menu, controller = harness.new_menu(a)
    harness.drain()
    assert controller.command('DOWN')
    assert controller.command('CLICK')
    harness.drain()
    assert a.trigger_calls == 0
    assert menu.isVisible()  # No selection made: user can cancel manually.
    controller.command('LEFT')
    assert not menu.isVisible()


def test_files_list_blank_background_uses_same_remote_context_adapter():
    assert ("self.show_expanded_background_paste_menu(pos)\n"
            "                self._enable_remote_context_wheel()" in APP)
    assert 'def _enable_remote_context_wheel(self):' in APP
    assert 'menu.popup(global_pos)' in APP


def test_files_exp_context_starts_on_back_even_when_qt_hovered_files_list(harness):
    back, forward, files = (FakeAction(s) for s in ('戻る', '進む', 'Filesリスト'))
    menu, controller = harness.new_menu(back, forward, files)
    menu._remote_pad_initial_action = back
    menu.setActiveAction(files)  # QMenu/native hover initially picked Filesリスト.
    harness.drain()
    assert menu.activeAction() is back
    controller.command('DOWN')
    assert menu.activeAction() is forward
    controller._select_first()  # Subsequent focus repairs keep current selection.
    assert menu.activeAction() is forward


def test_other_context_keeps_qt_native_initial_selection(harness):
    back, forward, files = (FakeAction(s) for s in ('戻る', '進む', 'Filesリスト'))
    menu, _controller = harness.new_menu(back, forward, files)
    menu.setActiveAction(files)
    harness.drain()
    assert menu.activeAction() is files
