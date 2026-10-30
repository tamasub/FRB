"""v38: sort button captures keys locally and avoids the Launcher eventFilter.

These tests run without Qt installed; Windows/PySide6 GUI smoke check remains
necessary for validation of the original repeatedly nested eventFilter failure.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'expanded_view.py'


class FakeQToolButton:
    def __init__(self, parent=None):
        self.parent_arg = parent
        self.fallback = Mock(return_value=False)
        self.showMenu = Mock()

    def event(self, event):
        return self.fallback(event)


class FakeEvent:
    def __init__(self, key, modifiers=0, event_type=2):
        self._key = key
        self._modifiers = modifiers
        self._type = event_type
        self.accepted = False

    def key(self): return self._key
    def modifiers(self): return self._modifiers
    def type(self): return self._type
    def accept(self): self.accepted = True


Qt = NS(Key=NS(Key_Tab=1, Key_Backtab=2, Key_Return=3, Key_Enter=4,
                Key_Space=5, Key_Right=6), KeyboardModifier=NS(NoModifier=0))
QEvent = NS(Type=NS(KeyPress=2))


def get_button():
    module = ast.parse(SRC.read_text(encoding='utf-8'))
    klass = next(node for node in module.body if isinstance(node, ast.ClassDef)
                 and node.name == '_MiddleSortButton')
    ns = {'QToolButton': FakeQToolButton, 'Qt': Qt, 'QEvent': QEvent}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])),
                 str(SRC), 'exec'), ns)
    launcher = NS(expanded_focus_key=Mock(return_value=True))
    obj = ns['_MiddleSortButton'](launcher, 'bar')
    return obj, launcher


def test_child_no_longer_installs_launcher_event_filter():
    source = SRC.read_text('utf-8')
    assert 'self.middle_sort_button.installEventFilter(launcher)' not in source
    assert 'self.middle_sort_button = _MiddleSortButton(launcher, self.middle_search_bar)' in source
    assert 'self.middle_sort_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)' in source


def test_tab_and_backtab_delegate_only_existing_navigation():
    obj, launcher = get_button()
    for key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
        event = FakeEvent(key)
        assert obj.event(event) is True
        launcher.expanded_focus_key.assert_called_with(obj, event)
    assert launcher.expanded_focus_key.call_count == 2
    obj.showMenu.assert_not_called()
    obj.fallback.assert_not_called()


def test_unhandled_tab_goes_to_qt_normal_processing():
    obj, launcher = get_button()
    launcher.expanded_focus_key.return_value = False
    event = FakeEvent(Qt.Key.Key_Tab)
    assert obj.event(event) is False
    obj.fallback.assert_called_once_with(event)


def test_enter_and_right_open_original_sort_menu():
    obj, launcher = get_button()
    for key in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                Qt.Key.Key_Space, Qt.Key.Key_Right):
        event = FakeEvent(key)
        assert obj.event(event) is True
        assert event.accepted
    assert obj.showMenu.call_count == 4
    launcher.expanded_focus_key.assert_not_called()
    obj.fallback.assert_not_called()


def test_unrelated_events_stay_in_native_button():
    obj, launcher = get_button()
    obj.event(FakeEvent(Qt.Key.Key_Right, modifiers=1))
    obj.event(FakeEvent(Qt.Key.Key_Return, event_type=44))
    assert obj.fallback.call_count == 2
    obj.showMenu.assert_not_called()
    launcher.expanded_focus_key.assert_not_called()


def test_popup_is_still_remote_anchored_by_launcher_not_child_button():
    source = (ROOT / 'src' / 'app.py').read_text('utf-8')
    assert 'def remote_middle_sort_menu(self):' in source
    assert 'pad = remote.pad' in source
    assert 'menu = view.middle_sort_menu' in source
    assert "if area == 'sort':\n            self.remote_middle_sort_menu()" in source
