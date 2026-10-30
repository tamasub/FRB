"""v48: the Chrome-style '+' must never sit on the last tab's close X.

Pure-source geometry tests run without Qt on CI; a real Windows Qt GUI test
is still needed for pixel-level rendering.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def _get_method(class_name, name):
    cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return node


def _position():
    node = _get_method('_WebTabBar', 'position_new_tab_button')
    # Pure geometry portion: self.mapTo() can be simulated without PySide6.
    class QPoint:
        def __init__(self, x, y):
            self._x, self._y = x, y
        def x(self): return self._x
        def y(self): return self._y
    namespace = {'QPoint': QPoint}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 '<v48>', 'exec'), namespace)
    return namespace['position_new_tab_button']


class MockButton:
    def __init__(self, host):
        self.host = host
        self.xy = None
        self.raised = False
    def width(self): return 29
    def height(self): return 29
    def parentWidget(self): return self.host
    def move(self, x, y): self.xy = (x, y)
    def raise_(self): self.raised = True


class MockHost:
    def __init__(self, width=900): self._width = width
    def width(self): return self._width


class MockBar:
    def __init__(self, tab_right, bar_width=400, host_width=900, tabs=2, origin=(0, 0)):
        self.host = MockHost(host_width)
        self._new_tab_button = MockButton(self.host)
        self.tab_right = tab_right
        self.bar_width = bar_width
        self.tabs = tabs
        self.origin = origin
    def parentWidget(self): return self.host
    def tabRect(self, index):
        assert index == self.tabs - 1
        return SimpleNamespace(right=lambda: self.tab_right)
    def count(self): return self.tabs
    def width(self): return self.bar_width
    def height(self): return 33
    def mapTo(self, host, point):
        assert host is self.host
        return SimpleNamespace(x=lambda: self.origin[0] + point.x(),
                               y=lambda: self.origin[1] + point.y())


def test_new_tab_is_sibling_of_tabbar_not_child():
    assert 'self.tabs = _WebTabs(self)' in SOURCE
    assert 'new_tab = QToolButton(self.tabs)' in SOURCE
    assert 'button.setParent(host)' in SOURCE
    assert 'new_tab = QToolButton(self.tabs.tabBar())' not in SOURCE
    assert 'button.raise_()' in SOURCE


def test_two_tabs_plus_stays_to_right_of_close_x_even_if_tabbar_has_no_extra_width():
    bar = MockBar(tab_right=325, bar_width=326, host_width=900)
    _position()(bar)
    assert bar._new_tab_button.xy == (333, 2)
    assert bar._new_tab_button.xy[0] > bar.tab_right
    assert bar._new_tab_button.raised


def test_tabbar_parent_offset_applied():
    bar = MockBar(tab_right=325, bar_width=326, host_width=900, origin=(8, 5))
    _position()(bar)
    assert bar._new_tab_button.xy == (341, 7)


def test_tab_overflow_keeps_plus_after_visible_strip_not_on_invisible_last_tab():
    bar = MockBar(tab_right=1200, bar_width=450, host_width=500, tabs=14)
    _position()(bar)
    assert bar._new_tab_button.xy == (457, 2)
    assert bar._new_tab_button.xy[0] >= bar.bar_width
    assert bar._new_tab_button.xy[0] + 29 <= bar.host.width()


def test_parent_reserves_plus_width_during_resize_and_tab_change():
    tabs_resize = _get_method('_WebTabs', 'resizeEvent')
    tabbar_reserve = _get_method('_WebTabBar', 'reserve_new_tab_space')
    assert 'reserve_new_tab_space' in ast.unparse(tabs_resize)
    assert 'self.setMaximumWidth(max_width)' in ast.unparse(tabbar_reserve)
    assert 'host.width() - button.width() - 16' in SOURCE
    for name in ('resizeEvent', 'tabLayoutChange', 'tabInserted', 'tabRemoved'):
        assert '_queue_new_tab_position()' in ast.unparse(_get_method('_WebTabBar', name))


def test_favicon_close_and_remote_tab_stay_untouched():
    for token in ('self.tabs.setTabIcon(index, icon)',
                  'self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide,',
                  'self.tabs.setMovable(True)',
                  'def select_tab(self, step):',
                  'def tab_context_menu(self):'):
        assert token in SOURCE
