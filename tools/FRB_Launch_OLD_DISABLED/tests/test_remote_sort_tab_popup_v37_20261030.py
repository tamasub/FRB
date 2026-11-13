"""v37: real tab-ring dispatch and Remote sort popup contract, no Qt needed."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from remote_navigation import next_area, previous_area, EXPANDED_AREAS, CLASSIC_AREAS
from expanded_keyboard_model import tab_target, FOCUS_ORDER
from focus_session import normalize_focus_state


def extract_method(filename, class_name, name, env=None):
    module = ast.parse((SRC / filename).read_text('utf-8'))
    cls = next(x for x in module.body if isinstance(x, ast.ClassDef) and x.name == class_name)
    func = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = dict(env or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[])), filename, 'exec'), ns)
    return ns[name]


def test_sort_between_directory_and_bookmarks_in_both_tab_rings():
    assert EXPANDED_AREAS == FOCUS_ORDER
    assert next_area('directory') == 'sort'
    assert next_area('sort') == 'bookmarks'
    assert previous_area('bookmarks') == 'sort'
    assert previous_area('sort') == 'directory'
    assert tab_target('directory') == 'sort'
    assert tab_target('sort') == 'bookmarks'
    assert tab_target('bookmarks', backward=True) == 'sort'
    assert tab_target('sort', backward=True) == 'directory'
    assert CLASSIC_AREAS == ('search', 'pages', 'list')
    assert normalize_focus_state({'area': 'sort'})['area'] == 'sort'


def test_sort_focus_recognized_and_main_keyboard_routes_to_the_button():
    focus_area = extract_method('app.py', 'Launcher', 'expanded_focus_area')
    button = object()
    tree = lambda: NS(viewport=lambda: object())
    view = NS(isVisible=lambda: True, middle_sort_button=button,
              address_bar=NS(editor=object()), root_buttons=[],
              left=NS(tree=tree()), middle=NS(tree=tree()), right=NS(tree=tree()))
    launcher = NS(expanded_view=view, search=object(), tabs=object())
    assert focus_area(launcher, button) == 'sort'
    assert focus_area(launcher, view.middle.tree) == 'directory'

    # The toolbar control must get key events before Qt falls back to its
    # default focus traversal (which would skip the custom pane ring).
    app = (SRC / 'app.py').read_text('utf-8')
    expanded = (SRC / 'expanded_view.py').read_text('utf-8')
    assert "elif target == 'sort':\n            view.middle_sort_button.setFocus" in app
    assert '[view.address_bar.editor, view.middle_sort_button]' in app
    # v38: keyboard routing is handled by the button itself, without the
    # broad Launcher.eventFilter (the latter caused nested PySide failures).
    assert 'self.middle_sort_button.installEventFilter(launcher)' not in expanded
    assert 'self.middle_sort_button = _MiddleSortButton(launcher, self.middle_search_bar)' in expanded
    assert 'self.middle_sort_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)' in expanded
    assert 'remoteSortActive="true"' in expanded


def test_wheel_click_on_sort_opens_menu_without_activating_a_file():
    fn = extract_method('app.py', 'Launcher', 'remote_mouse_click')
    open_menu = Mock()
    view = NS(isVisible=lambda: True, commit_remote_inline_rename=lambda: False,
              ensure_middle_current_selection=Mock())
    launcher = NS(expanded_view=view, _remote_area='sort', _last_focus_area='directory',
                  _remote_mouse_last_click='stale', _remote_mouse_menu_click=None,
                  remote_middle_sort_menu=open_menu)
    fn(launcher)
    open_menu.assert_called_once_with()
    assert launcher._remote_mouse_last_click is None
    view.ensure_middle_current_selection.assert_not_called()
    fn(launcher, double=True)
    assert open_menu.call_count == 1


def test_rename_commit_keeps_priority_over_sort_popup():
    fn = extract_method('app.py', 'Launcher', 'remote_mouse_click')
    open_menu = Mock()
    launcher = NS(expanded_view=NS(isVisible=lambda: True,
                                    commit_remote_inline_rename=lambda: True),
                  _remote_area='sort', _remote_mouse_last_click='stale',
                  _remote_mouse_menu_click='stale', remote_middle_sort_menu=open_menu)
    fn(launcher)
    open_menu.assert_not_called()
    assert launcher._remote_mouse_last_click is None
    assert launcher._remote_mouse_menu_click is None


class Point:
    def __init__(self, x=0, y=0): self._x, self._y = x, y
    def x(self): return self._x
    def y(self): return self._y
    def setX(self, val): self._x = val
    def setY(self, val): self._y = val


class Rect:
    def __init__(self, x, y, w, h): self._x, self._y, self._w, self._h = x, y, w, h
    def left(self): return self._x
    def top(self): return self._y
    def right(self): return self._x + self._w - 1
    def bottom(self): return self._y + self._h - 1
    def center(self): return Point(self._w//2, self._h//2)


def test_real_existing_menu_is_anchored_to_remote_pad_right_and_toggleable():
    screen = NS(availableGeometry=lambda: Rect(0, 0, 1600, 900))
    app = NS(screenAt=lambda pos: screen, primaryScreen=lambda: screen)
    fn = extract_method('app.py', 'Launcher', 'remote_middle_sort_menu',
                        {'QPoint': Point, 'QApplication': app})
    menu = NS(isVisible=Mock(return_value=False), close=Mock(),
              ensurePolished=Mock(), sizeHint=lambda: NS(width=lambda: 210, height=lambda: 160),
              popup=Mock())
    pad = NS(width=lambda: 56, rect=lambda: Rect(0,0,56,46),
             mapToGlobal=lambda p: Point(300 + p.x(), 200 + p.y()))
    launcher = NS(remote_window=NS(isVisible=lambda: True, pad=pad),
                  expanded_view=NS(isVisible=lambda: True, middle_sort_menu=menu))
    fn(launcher)
    point = menu.popup.call_args.args[0]
    assert (point.x(), point.y()) == (360, 200)
    menu.ensurePolished.assert_called_once()
    menu.isVisible.return_value = True
    fn(launcher)
    menu.close.assert_called_once()
    assert menu.popup.call_count == 1


def test_popup_falls_back_inside_screen_if_no_right_side_room():
    screen = NS(availableGeometry=lambda: Rect(0,0,430,330))
    app = NS(screenAt=lambda pos: screen, primaryScreen=lambda: screen)
    fn = extract_method('app.py', 'Launcher', 'remote_middle_sort_menu',
                        {'QPoint': Point, 'QApplication': app})
    menu = NS(isVisible=lambda: False, ensurePolished=lambda:None,
              sizeHint=lambda: NS(width=lambda:180, height=lambda:200), popup=Mock())
    pad = NS(width=lambda:56, rect=lambda:Rect(0,0,56,46),
             mapToGlobal=lambda p:Point(350+p.x(),280+p.y()))
    launcher = NS(remote_window=NS(isVisible=lambda: True, pad=pad),
                  expanded_view=NS(isVisible=lambda: True, middle_sort_menu=menu))
    fn(launcher)
    point=menu.popup.call_args.args[0]
    assert (point.x(),point.y())==(166,130)


def test_remote_area_status_and_action_use_existing_menu():
    app = (SRC / 'app.py').read_text('utf-8')
    remote = (SRC / 'launch_remote.py').read_text('utf-8')
    assert "'sort': '第2列 並び替え'" in remote
    assert 'menu = view.middle_sort_menu' in app
    assert "if area == 'sort':\n            # Wheel CLICK" in app
    assert "elif area == 'sort':\n                view.middle_sort_button.setFocus" in app


def test_remote_tab_visually_activates_sort_only_then_bookmarks():
    # Exercise the real controller method with a stubbed Qt widget tree:
    # the tab stop must be visibly active even when Remote is non-activating.
    qt = NS(FocusReason=NS(TabFocusReason=12, OtherFocusReason=13))
    fn = extract_method('app.py', 'Launcher', 'remote_focus_area', {'Qt': qt})

    class Button:
        def __init__(self):
            self.props = {'remoteSortActive': False}
            self.focus_calls = []
            self.polish = Mock()
        def setFocus(self, reason): self.focus_calls.append(reason)
        def property(self, key): return self.props.get(key)
        def setProperty(self, key, value): self.props[key] = value
        def style(self): return NS(unpolish=self.polish, polish=self.polish)
        def update(self): pass

    def pane():
        tree = NS(remote_highlight_mode=False, remote_logical_active=False,
                  property=lambda key: False, setProperty=Mock(),
                  style=lambda:NS(unpolish=Mock(), polish=Mock()),
                  viewport=lambda:NS(update=Mock()))
        return NS(tree=tree)

    button = Button()
    view = NS(isVisible=lambda: True, middle_sort_button=button,
              left=pane(), middle=pane(), right=pane(),
              ensure_middle_current_selection=Mock(), focus_panel=Mock())
    remote = NS(set_area=Mock())
    launcher = NS(expanded_view=view, remote_window=remote, _remote_area='directory')

    fn(launcher, 'sort')
    assert launcher._remote_area == 'sort'
    assert button.props['remoteSortActive'] is True
    assert button.focus_calls == [12]
    assert not view.middle.tree.remote_logical_active
    assert not view.right.tree.remote_logical_active
    remote.set_area.assert_called_with('sort')
    fn(launcher, 'bookmarks')
    assert button.props['remoteSortActive'] is False
    assert view.right.tree.remote_logical_active
    view.focus_panel.assert_called_once_with(view.right)
    remote.set_area.assert_called_with('bookmarks')
