"""Files first-column wheel browsing: selection + preview, no execution.

The real handler is executed without PySide6, which is absent on the Linux
build machine. Native Windows dispatch must still be exercised manually.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from expanded_view_model import root_wheel_target


def real_wheel_method():
    source = ROOT / 'src/expanded_view.py'
    module = ast.parse(source.read_text(encoding='utf-8'))
    view = next(node for node in module.body if isinstance(node, ast.ClassDef)
                and node.name == 'ExpandedLauncherView')
    handler = next(node for node in view.body if isinstance(node, ast.FunctionDef)
                   and node.name == 'wheel_files_first_column')
    wrapper = ast.ClassDef(name='FilesWheelHandler', bases=[], keywords=[],
                           body=[handler], decorator_list=[])
    qt = SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                         FocusReason=SimpleNamespace(MouseFocusReason='mouse'))
    namespace = {'Qt': qt, 'root_wheel_target': root_wheel_target}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[])),
                 str(source), 'exec'), namespace)
    return namespace['FilesWheelHandler']


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
    def __init__(self, items):
        self.items, self.current = list(items), items[0] if items else None
        self.scrolled, self.focuses = [], []
    def topLevelItemCount(self):
        return len(self.items)
    def currentItem(self):
        return self.current
    def indexOfTopLevelItem(self, item):
        return self.items.index(item) if item in self.items else -1
    def topLevelItem(self, index):
        return self.items[index]
    def setCurrentItem(self, item):
        self.current = item
    def scrollToItem(self, item):
        self.scrolled.append(item['title'])
    def setFocus(self, reason):
        self.focuses.append(reason)


class Demo(real_wheel_method()):
    __test__ = False
    def __init__(self, rows=None):
        if rows is None:
            rows = [{'title': f'folder_{i}', 'item_kind': 'directory'} for i in range(5)]
        self.left = SimpleNamespace(tree=Tree(rows))
        self._wheel_files_delta = 0
        self.previews = []
        self.executed = []
    def row_data(self, item):
        return item
    def choose_files(self, item, column):
        self.previews.append(item['title'])


def test_wheel_down_up_previews_and_updates_current():
    demo = Demo()
    assert demo.wheel_files_first_column(Event(angle=-120))
    assert demo.left.tree.currentItem()['title'] == 'folder_1'
    assert demo.previews == ['folder_1']
    assert demo.left.tree.scrolled == ['folder_1']
    assert demo.left.tree.focuses == ['mouse']
    assert demo.wheel_files_first_column(Event(angle=120))
    assert demo.left.tree.currentItem()['title'] == 'folder_0'
    assert demo.previews[-1] == 'folder_0'


def test_wheel_large_steps_clamps_at_ends_and_does_not_loop():
    demo = Demo()
    assert demo.wheel_files_first_column(Event(angle=-12000))
    assert demo.left.tree.currentItem()['title'] == 'folder_4'
    assert demo.wheel_files_first_column(Event(angle=-120))
    assert demo.previews == ['folder_4']
    assert demo.wheel_files_first_column(Event(angle=12000))
    assert demo.left.tree.currentItem()['title'] == 'folder_0'


def test_trackpad_accumulates_and_ctrl_wheel_is_not_intercepted():
    demo = Demo()
    for _ in range(3):
        assert demo.wheel_files_first_column(Event(angle=-30))
    assert demo.previews == []
    assert demo.wheel_files_first_column(Event(angle=-30))
    assert demo.previews == ['folder_1']
    assert demo.wheel_files_first_column(Event(pixels=-40))
    assert demo.previews == ['folder_1', 'folder_2']
    assert not demo.wheel_files_first_column(Event(angle=-120, modifiers=1))
    assert demo.previews == ['folder_1', 'folder_2']


def test_commands_never_execute_or_replace_folder_preview():
    rows = [{'title': 'folder', 'item_kind': 'directory'},
            {'title': 'unsafe_command', 'item_kind': 'command'},
            {'title': 'other_folder', 'item_kind': 'category'}]
    demo = Demo(rows)
    assert demo.wheel_files_first_column(Event(angle=-120))
    assert demo.previews == []
    assert demo.executed == []
    assert demo.wheel_files_first_column(Event(angle=-120))
    assert demo.previews == ['other_folder']
    assert demo.executed == []


def test_empty_tree_does_not_intercept_wheel():
    demo = Demo([])
    assert not demo.wheel_files_first_column(Event(angle=-120))


def test_event_filter_only_hooks_files_first_column():
    source = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'self.left.tree.viewport().installEventFilter(self)' in source
    assert 'self.left.tree.installEventFilter(self)' in source
    assert 'obj in (self.left.tree, self.left.tree.viewport())' in source
    assert 'self.wheel_files_first_column(event)' in source
    assert 'self.choose_files(item, 0)' in source
    assert 'tree.scrollToItem(item)' in source
    # Middle stays native.  Right bookmarks now have their own wheel selector.
    assert 'self.middle.tree.viewport().installEventFilter(self)' not in source
    assert 'self.right.tree.viewport().installEventFilter(self)' in source
