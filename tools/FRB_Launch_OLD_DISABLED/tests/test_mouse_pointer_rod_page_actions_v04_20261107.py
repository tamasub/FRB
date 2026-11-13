"""Page-menu regression tests. Deterministic, no desktop/PySide dependency.

The manual Windows smoke test must still verify click delivery and z-order.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mouse_pointer_rod_qt_menu import dispatch_page_cascade_action


class Position:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __sub__(self, other):
        return NS(manhattanLength=lambda: abs(self.x-other.x)+abs(self.y-other.y))
    def __eq__(self, other):
        return isinstance(other, Position) and (self.x,self.y)==(other.x,other.y)


class Action:
    def __init__(self, row=None, right_arrow=False, enabled=True):
        self.row = row
        self.right_arrow = right_arrow
        self.enabled = enabled
        self.trigger = Mock()
    def data(self):
        return self.row
    def isEnabled(self):
        return self.enabled
    def isVisible(self):
        return True
    def property(self, key):
        return self.right_arrow if key == 'launch_right_arrow_executes' else None


class Menu:
    def __init__(self, action=None, *, parent=None, page=True, bookmark=False,
                 visible=True, left=100, top=100, width=200, height=240):
        self._action = action
        self._parent = parent
        self.remote_page_navigation = page
        self.bookmark_navigation = bookmark
        self._visible = visible
        self._x, self._y, self._w, self._h = left, top, width, height
        self.filter_action = Action()
        self.setActiveAction = Mock()
    def isVisible(self): return self._visible
    def parentWidget(self): return self._parent
    def mapFromGlobal(self, pos): return Position(pos.x-self._x,pos.y-self._y)
    def rect(self):
        return NS(contains=lambda p: 0 <= p.x < self._w and 0 <= p.y < self._h)
    def actionAt(self, pos): return self._action
    def frameGeometry(self): return NS(contains=lambda p: True)


def test_one_page_item_trigger_is_exactly_once():
    a = Action({'item_kind':'command','title':'hello'})
    menu = Menu(a)
    assert dispatch_page_cascade_action(Position(112, 122), [menu])
    a.trigger.assert_called_once_with()
    menu.setActiveAction.assert_called_once_with(a)


def test_nested_page_column_wins_even_if_root_is_enumerated_last():
    root_action = Action({'item_kind':'category'})
    child_action = Action({'item_kind':'command'})
    root = Menu(root_action)
    child = Menu(child_action, parent=root)
    assert dispatch_page_cascade_action(Position(112,122), [child,root])
    root_action.trigger.assert_not_called()
    child_action.trigger.assert_called_once()


def test_non_page_and_browser_bookmarks_do_not_intercept_native_click():
    for flags in ({'page':False},{'bookmark':True}):
        a = Action({'item_kind':'command'})
        assert not dispatch_page_cascade_action(Position(112,122),[Menu(a,**flags)])
        a.trigger.assert_not_called()


def test_unusable_rows_or_missed_hit_are_not_triggered():
    for options in ({'enabled':False},{'row':None}):
        a = Action(**options)
        assert not dispatch_page_cascade_action(Position(112,122),[Menu(a)])
        a.trigger.assert_not_called()
    a = Action({'item_kind':'command'})
    assert not dispatch_page_cascade_action(Position(12,22),[Menu(a)])
    a.trigger.assert_not_called()


def test_page_search_field_is_not_mistaken_for_a_command():
    menu = Menu()
    menu._action = menu.filter_action
    assert not dispatch_page_cascade_action(Position(112,122),[menu])


def test_page_utility_action_remains_supported():
    a = Action(right_arrow=True)
    assert dispatch_page_cascade_action(Position(112,122),[Menu(a)])
    a.trigger.assert_called_once()


def test_closed_or_deleted_menu_does_not_crash():
    a = Action({'item_kind':'command'})
    menu = Menu(a,visible=False)
    assert not dispatch_page_cascade_action(Position(112,122),[menu])
    class DeletedMenu(Menu):
        def isVisible(self): raise RuntimeError('Internal C++ object deleted')
    assert not dispatch_page_cascade_action(Position(112,122),[DeletedMenu(a)])


def test_rod_uses_qaction_for_page_without_native_cursor_warp(monkeypatch):
    source = (ROOT/'src/mouse_pointer_rod.py').read_text('utf8')
    tree = ast.parse(source)
    cls = next(c for c in tree.body if isinstance(c,ast.ClassDef)
               and c.name=='MousePointerRodPad')
    fn = next(f for f in cls.body if isinstance(f,ast.FunctionDef)
              and f.name=='_dispatch_windows_click')
    native_click = Mock()
    stub_module = NS(click_at=native_click)
    monkeypatch.setitem(sys.modules, 'mouse_pointer_rod_windows', stub_module)
    a = Action({'item_kind':'command'})
    menu = Menu(a)
    cursor = NS(pos=lambda: Position(11,13),setPos=Mock())
    scope = {
        'QPoint': Position,
        'QApplication': NS(screenAt=lambda _:True,topLevelWidgets=lambda:[menu]),
        'QMenu':Menu, 'QCursor':cursor,
        'QTimer': NS(singleShot=Mock()),
    }
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'v04_page_click','exec'),scope)
    rod = NS(_cursor_on_blue=lambda:True,tip_global=lambda:(112,122))
    remote = NS(frameGeometry=lambda: NS(contains=lambda _:False))
    assert scope[fn.name](rod,'select',remote,NS(footer=None))
    assert a.trigger.call_count == 1
    native_click.assert_not_called()
    cursor.setPos.assert_not_called()
    assert scope[fn.name](rod,'double',remote,NS(footer=None))
    assert a.trigger.call_count == 2  # one per gesture, never twice per gesture
