"""Wheel selection/preview only in expanded Bookmarks' FIRST level.

Execute the real handler method with a small Qt-free view fake; native Windows
focus/painting and scrollbar-drag interactions remain manual smoke tests.
"""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_view_model import root_wheel_target


def real_method():
    p = ROOT / 'src/expanded_view.py'
    source = ast.parse(p.read_text(encoding='utf-8'))
    view = next(n for n in source.body if isinstance(n, ast.ClassDef)
                and n.name == 'ExpandedLauncherView')
    method = next(n for n in view.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'wheel_bookmarks_first_level')
    wrapper = ast.ClassDef(name='Wheel', bases=[], keywords=[], body=[method], decorator_list=[])
    qt = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                         FocusReason=SimpleNamespace(MouseFocusReason='mouse'))
    env = dict(Qt=qt, root_wheel_target=root_wheel_target)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[])),
                 str(p), 'exec'), env)
    return env['Wheel']


class Event:
    def __init__(self, angle=0, pixels=0, modifiers=0):
        self.angle, self.pixels, self.mods = angle, pixels, modifiers
    def angleDelta(self):
        return SimpleNamespace(y=lambda: self.angle)
    def pixelDelta(self):
        return SimpleNamespace(y=lambda: self.pixels)
    def modifiers(self):
        return self.mods


class Tree:
    def __init__(self, rows):
        self.rows = list(rows)
        self.current = self.rows[0] if rows else None
        self.scrolled = []
        self.focuses = []
    def topLevelItemCount(self):
        return len(self.rows)
    def topLevelItem(self, index):
        return self.rows[index]
    def currentItem(self):
        return self.current
    def indexOfTopLevelItem(self, item):
        return self.rows.index(item) if item in self.rows else -1
    def setCurrentItem(self, item):
        self.current = item
    def scrollToItem(self, item):
        self.scrolled.append(item['title'])
    def setFocus(self, reason):
        self.focuses.append(reason)


class Demo(real_method()):
    __test__ = False
    def __init__(self, kinds=('category', 'command', 'category', 'command', 'directory')):
        rows = [dict(title=f'item-{i}', item_kind=k) for i, k in enumerate(kinds)]
        self.right = SimpleNamespace(tree=Tree(rows))
        self._wheel_bookmark_delta = 0
        self.previewed = []
        self.closed = []
        self.executed = []
        self.launcher = SimpleNamespace(close_cascade_for_main_interaction=lambda: self.closed.append(True))
    def row_data(self, item):
        return item
    def choose_bookmark(self, item, col):
        assert col == 0
        self.previewed.append(item['title'])


def test_urls_selected_but_not_launched_and_old_preview_is_closed():
    demo = Demo()
    assert demo.wheel_bookmarks_first_level(Event(angle=-120))
    assert demo.right.tree.current['title'] == 'item-1'
    assert demo.closed == [True]
    assert demo.previewed == []
    assert demo.executed == []
    assert demo.right.tree.scrolled == ['item-1']


def test_category_and_directory_preview_but_not_execute():
    demo = Demo()
    assert demo.wheel_bookmarks_first_level(Event(angle=-240))
    assert demo.previewed == ['item-2']
    assert demo.right.tree.focuses[-1] == 'mouse'
    assert demo.wheel_bookmarks_first_level(Event(angle=-240))
    assert demo.previewed == ['item-2', 'item-4']
    assert demo.executed == []


def test_up_down_and_clamp_edges_no_wrap_or_repeated_preview():
    demo = Demo()
    assert demo.wheel_bookmarks_first_level(Event(angle=-20000))
    assert demo.right.tree.current['title'] == 'item-4'
    assert demo.wheel_bookmarks_first_level(Event(angle=-120))
    assert demo.previewed == ['item-4']
    assert demo.wheel_bookmarks_first_level(Event(angle=20000))
    assert demo.right.tree.current['title'] == 'item-0'
    assert demo.previewed[-1] == 'item-0'


def test_precision_trackpad_accumulation_and_pixel_delta():
    demo = Demo()
    for _ in range(3):
        assert demo.wheel_bookmarks_first_level(Event(angle=-30))
    assert demo.right.tree.current['title'] == 'item-0'
    assert demo.wheel_bookmarks_first_level(Event(angle=-30))
    assert demo.right.tree.current['title'] == 'item-1'
    assert demo.wheel_bookmarks_first_level(Event(pixels=-40))
    assert demo.right.tree.current['title'] == 'item-2'


def test_empty_and_modified_wheel_do_not_fall_through_to_native_scroll():
    assert not Demo(kinds=()).wheel_bookmarks_first_level(Event(angle=-120))
    demo = Demo()
    assert demo.wheel_bookmarks_first_level(Event(angle=-120, modifiers=1))
    assert demo.right.tree.current['title'] == 'item-0'
    assert demo.previewed == []


def test_no_wheel_on_middle_or_child_columns_and_scrollbar_remains_native():
    view = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'self.right.tree.installEventFilter(self)' in view
    assert 'self.right.tree.viewport().installEventFilter(self)' in view
    assert 'obj in (self.right.tree, self.right.tree.viewport())' in view
    assert 'self.wheel_bookmarks_first_level(event)' in view
    assert 'self.middle.tree.viewport().installEventFilter(self)' not in view
    # No right.verticalScrollBar() event filter; dragging the thumb is normal.
    assert 'self.right.tree.verticalScrollBar().installEventFilter(self)' not in view
    assert 'self._wheel_bookmark_delta = 0' in view


def test_page_tab_dark_focus_only_lighter_weight():
    focus = (ROOT / 'src/page_tab_focus.py').read_text(encoding='utf-8')
    assert "focus_width = 1.8 if getattr(self, '_light_theme', False) else 0.75" in focus
    assert "else '#d2e6ff'" in focus
