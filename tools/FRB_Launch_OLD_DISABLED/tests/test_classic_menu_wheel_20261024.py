"""Old-view wheel page flipping; exercise the actual methods without GUI bindings.

PySide6 is optional in CI, so these fakes use AST-extracted *production* methods.
The final event-routing and QMenu native focus still need Windows smoke testing.
"""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from menu_wheel import wheel_motion, wheel_neighbor


def method(class_name, method_name, namespace):
    src = ROOT / 'src' / 'app.py'
    root = ast.parse(src.read_text(encoding='utf-8'))
    cls = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    tree = ast.Module(body=[fn], type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), str(src), 'exec'), namespace)
    return namespace[method_name]


class Event:
    def __init__(self, angle=0, pixels=0, mods=0):
        self.angle, self.pixels, self.mods = angle, pixels, mods

    def modifiers(self):
        return self.mods

    def angleDelta(self):
        return SimpleNamespace(y=lambda: self.angle)

    def pixelDelta(self):
        return SimpleNamespace(y=lambda: self.pixels)


class Timer:
    def __init__(self):
        self.count = 0
    def stop(self):
        self.count += 1


class Item:
    def __init__(self, kind='category', *, hidden=False, disabled=False):
        self.row = {'item_kind': kind}
        self.hidden = hidden
        self.disabled = disabled

    def isHidden(self):
        return self.hidden

    def isDisabled(self):
        return self.disabled

    def data(self, *args):
        return self.row


class Tree:
    def __init__(self, items):
        self.items = items
        self.current = items[0] if items else None
        self.scrolled = []

    def isVisible(self):
        return True

    def topLevelItemCount(self):
        return len(self.items)

    def topLevelItem(self, i):
        return self.items[i]

    def currentItem(self):
        return self.current

    def setCurrentItem(self, item):
        self.current = item

    def scrollToItem(self, item):
        self.scrolled.append(item)


class Pop:
    def __init__(self):
        self.closed = 0
    def isVisible(self):
        return True
    def close(self):
        self.closed += 1


class Classic:
    wheel_classic_menu = method('Launcher', 'wheel_classic_menu', {
        'Qt': SimpleNamespace(KeyboardModifier=SimpleNamespace(NoModifier=0),
                              ItemDataRole=SimpleNamespace(UserRole=42)),
        'wheel_motion': wheel_motion, 'wheel_neighbor': wheel_neighbor,
    })

    def __init__(self, kinds=('category', 'command', 'directory', 'command')):
        self.list = Tree([Item(kind) for kind in kinds])
        self.view_mode = 'classic'
        self.hover_timer = Timer()
        self.pending_menu_item = 'previous_hover'
        self.menu = Pop()
        self.opened = []

    def cascade(self, row, item, mode):
        self.opened.append((row['item_kind'], item, mode))


def test_wheel_motion_accumulates_trackpad_and_reverses():
    assert wheel_motion(120, 50) == (1, 0)  # Native angle wins over pixel delta.
    assert wheel_motion(-240, 0) == (-2, 0)
    assert wheel_motion(0, 20) == (0, 60)
    assert wheel_motion(0, 20, 60) == (1, 0)
    assert wheel_motion(0, -15, -90) == (-1, -15)


def test_wheel_neighbor_clamps_and_skips_missing_selection():
    items = ['a', 'b', 'c']
    assert wheel_neighbor(items, 'b', 1) == 'c'
    assert wheel_neighbor(items, 'b', -1) == 'a'
    assert wheel_neighbor(items, 'a', -20) == 'a'
    assert wheel_neighbor(items, 'c', 20) == 'c'
    assert wheel_neighbor(items, None, 1) == 'a'
    assert wheel_neighbor(items, None, -1) == 'c'


def test_main_wheel_opens_directories_but_never_executes_commands():
    ui = Classic()
    assert ui.wheel_classic_menu(Event(angle=-120)) is True
    assert ui.list.currentItem() is ui.list.items[1]
    assert ui.opened == []  # command row: select only
    assert ui.menu.closed == 1
    assert ui.wheel_classic_menu(Event(angle=-120)) is True
    assert ui.list.currentItem() is ui.list.items[2]
    assert [row[0] for row in ui.opened] == ['directory']
    assert ui.opened[0][2] == 'keyboard'  # No hover-expiry while wheeling.
    assert ui.list.scrolled[-1] is ui.list.currentItem()
    assert ui.pending_menu_item is None


def test_main_wheel_ignores_modifiers_and_expanded_mode():
    ui = Classic()
    assert ui.wheel_classic_menu(Event(angle=-120, mods=1)) is False
    assert ui.list.currentItem() is ui.list.items[0]
    ui.view_mode = 'expanded'
    assert ui.wheel_classic_menu(Event(angle=-120)) is False
    assert not ui.opened


def test_main_wheel_skips_hidden_rows_and_stops_at_ends():
    ui = Classic()
    ui.list.items[1].hidden = True
    assert ui.wheel_classic_menu(Event(angle=-120))
    assert ui.list.currentItem() is ui.list.items[2]
    assert ui.wheel_classic_menu(Event(angle=-9999))
    assert ui.list.currentItem() is ui.list.items[3]
    assert ui.wheel_classic_menu(Event(angle=-120))
    assert ui.list.currentItem() is ui.list.items[3]


def test_classic_wheel_only_in_first_level_and_popup_keeps_native_scroll():
    """Wheel preview stays at Launcher root; nested QMenu/tree has native wheel."""
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    methods = {cls: {n.name: ast.unparse(n)
                     for n in node.body if isinstance(n, ast.FunctionDef)}
               for cls, node in classes.items()
               if cls in ('Launcher', 'CascadeMenu', 'AppCascadeMenu')}

    assert 'wheel_classic_menu' in methods['Launcher']
    assert 'self.wheel_classic_menu(event)' in methods['Launcher']['eventFilter']
    assert 'self.cascade(row, selected' in methods['Launcher']['wheel_classic_menu']
    # No intercept on child popup, including a scrollable directory column.
    assert 'wheel_select_preview' not in methods['CascadeMenu']
    assert 'wheelEvent' not in methods['CascadeMenu']
    assert 'Wheel' not in methods['CascadeMenu']['eventFilter']
    init_source = methods['CascadeMenu']['__init__']
    assert '_menu_wheel_remainder' not in init_source
    # App catalogs retain their independent native-scroll implementation.
    assert 'bar.setValue(bar.value() - round(delta))' in methods['AppCascadeMenu']['eventFilter']
    # Modern horizontal first-level toolbar has its own independent wheel logic.
    modern = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
    assert 'def wheel_first_level(self, event, source):' in modern


def test_nested_popup_keeps_hover_and_keyboard_openers():
    tree = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    cls = next(n for n in tree.body
               if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    methods = {n.name: ast.unparse(n) for n in cls.body
               if isinstance(n, ast.FunctionDef)}
    assert 'self._scroll_hover(' in methods['eventFilter']
    assert 'self._move_filtered_selection(' in methods['eventFilter']
    assert 'self.keyPressEvent(event)' in methods['eventFilter']
