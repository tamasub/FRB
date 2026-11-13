"""Files List search history: outside clicks must dismiss the non-grabbing menu.

Pure GUI-event stubs: repeat on Windows with the real Remote/Windows mouse rod.
"""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]


def _method(name):
    source = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    owner = next(node for node in tree.body
                 if isinstance(node, ast.ClassDef)
                 and node.name == 'ExpandedLauncherView')
    node = next(node for node in owner.body
                if isinstance(node, ast.FunctionDef) and node.name == name)
    scope = {'QEvent': NS(Type=NS(MouseButtonPress=1, ApplicationDeactivate=2)),
             'QWidget': FakeWidget, 'QMenu': FakeMenu}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<history>', 'exec'), scope)
    return scope[name]


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def contains(self, p):
        return self.x1 <= p.x <= self.x2 and self.y1 <= p.y <= self.y2


class FakeWidget:
    pass


class FakeMenu(FakeWidget):
    def __init__(self, bounds, *, visible=True, submenus=()):
        self.bounds = Rect(*bounds)
        self.visible = visible
        self.submenus = submenus
        self.hide = Mock()

    def isVisible(self):
        return self.visible

    def frameGeometry(self):
        return self.bounds

    def findChildren(self, cls):
        assert cls is FakeMenu
        return self.submenus


class FakeButton(FakeWidget):
    def __init__(self, bounds):
        self.bounds = Rect(*bounds)

    def isVisible(self):
        return True

    def rect(self):
        return self.bounds

    def mapFromGlobal(self, point):
        return point  # Already in the same mock coordinate space.


class FakeEvent:
    def __init__(self, kind, point=(0, 0)):
        self.kind, self.point = kind, Point(*point)
        self.accept = Mock()

    def type(self):
        return self.kind

    def globalPosition(self):
        return NS(toPoint=lambda: self.point)


def setup():
    submenu = FakeMenu((210, 120, 350, 240))
    menu = FakeMenu((30, 50, 210, 160), submenus=[submenu])
    button = FakeButton((30, 20, 60, 49))
    view = NS(middle_search_history_menu=menu,
              middle_search_history_button=button)
    return _method('_dismiss_middle_search_history_on_outside_click'), view, menu, submenu


def test_outside_click_closes_menu_but_does_not_consume_click():
    fn, view, menu, _ = setup()
    event = FakeEvent(1, (400, 300))
    assert fn(view, FakeWidget(), event) is None
    menu.hide.assert_called_once_with()
    event.accept.assert_not_called()  # Real target must receive its click.


def test_mouse_press_from_native_qwindow_also_closes_menu():
    fn, view, menu, _ = setup()
    fn(view, object(), FakeEvent(1, (400, 300)))
    menu.hide.assert_called_once_with()


def test_clock_button_press_is_left_to_existing_toggle():
    fn, view, menu, _ = setup()
    fn(view, FakeWidget(), FakeEvent(1, (41, 33)))
    menu.hide.assert_not_called()


def test_click_on_main_history_or_nested_delete_menu_is_preserved():
    fn, view, menu, _ = setup()
    fn(view, menu, FakeEvent(1, (100, 100)))
    fn(view, FakeWidget(), FakeEvent(1, (300, 190)))
    menu.hide.assert_not_called()


def test_outside_click_still_closes_if_a_submenu_is_open():
    fn, view, menu, _ = setup()
    fn(view, FakeWidget(), FakeEvent(1, (600, 500)))
    menu.hide.assert_called_once_with()


def test_application_deactivate_hides_menu_even_without_qt_mouse_press():
    fn, view, menu, _ = setup()
    fn(view, object(), FakeEvent(2))
    menu.hide.assert_called_once_with()


def test_other_events_are_not_treated_as_outside_clicks():
    fn, view, menu, _ = setup()
    fn(view, FakeWidget(), FakeEvent(3, (600, 500)))  # Mouse move/wheel/etc.
    menu.hide.assert_not_called()


def test_not_visible_history_does_not_interfere():
    fn, view, menu, _ = setup()
    menu.visible = False
    fn(view, FakeWidget(), FakeEvent(1, (600, 500)))
    menu.hide.assert_not_called()


def test_expanded_view_app_event_filter_invokes_dismissal():
    source = (ROOT / 'src' / 'expanded_view.py').read_text(encoding='utf-8')
    assert 'QApplication.instance().installEventFilter(self)' in source
    assert ('def eventFilter(self, obj, event):\n'
            '        self._dismiss_middle_search_history_on_outside_click(obj, event)') in source
    # Do not revert to grabbing InstantPopup; Windows mouse rod needs this.
    assert 'self.middle_search_history_menu = _NonGrabbingHistoryMenu(' in source
