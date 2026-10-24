"""Prevent first-level popup positioning from drifting to the next button.

Use the real Launcher method via AST extraction to test positions without
requiring PySide6 or a Windows desktop in CI.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


class FakeMenu:
    def __init__(self, parent=None, launcher=None):
        self.position = None
        self.open_mode = None
        self.return_focus_widget = None
        self.return_focus_item = None
        self.focused = False

    def popup(self, position):
        self.position = position

    def setFocus(self):
        self.focused = True


class Button:
    def __init__(self, x=80, y=130, width=68, height=30):
        self.x, self.y, self._width, self._height = x, y, width, height

    def width(self):
        return self._width

    def height(self):
        return self._height

    def mapToGlobal(self, point):
        return Point(self.x + point.x, self.y + point.y)


class Tree:
    def __init__(self, viewport):
        self._viewport = viewport

    def viewport(self):
        return self._viewport

    def visualItemRect(self, item):
        return SimpleNamespace(top=lambda: 17)


def open_cascade_method():
    src = ast.parse((ROOT / 'src/app.py').read_text(encoding='utf-8'))
    launcher = next(node for node in src.body if isinstance(node, ast.ClassDef)
                    and node.name == 'Launcher')
    method = next(node for node in launcher.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == 'open_expanded_cascade')
    fake_class = ast.ClassDef(name='Target', bases=[], keywords=[],
                              body=[method], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[fake_class], type_ignores=[]))
    env = {'QTreeWidget': Tree, 'QPoint': Point,
           'AppCascadeMenu': FakeMenu, 'CascadeMenu': FakeMenu}
    exec(compile(module, '<expanded-cascade>', 'exec'), env)
    return env['Target'].open_expanded_cascade


def make_launcher():
    launcher = SimpleNamespace(menu=None,
                               hover_timer=SimpleNamespace(stop=lambda: None),
                               fill_cascade=lambda menu, row: None)
    return launcher


def test_root_popup_starts_at_its_own_button_left_edge():
    launcher = make_launcher()
    root_button = Button(x=80, y=130, width=68, height=30)
    open_cascade_method()(launcher, {'item_kind': 'category'}, root_button)
    assert (launcher.menu.position.x, launcher.menu.position.y) == (80, 160)
    assert launcher.menu.return_focus_widget is root_button
    assert launcher.menu.focused


def test_right_side_root_button_does_not_snap_to_neighbor():
    launcher = make_launcher()
    button = Button(x=320, y=130, width=125, height=30)
    open_cascade_method()(launcher, {'item_kind': 'category'}, button)
    assert (launcher.menu.position.x, launcher.menu.position.y) == (320, 160)


def test_panel_rows_continue_using_right_edge_anchor():
    launcher = make_launcher()
    viewport = Button(x=270, y=235, width=310, height=450)
    tree = Tree(viewport)
    item = object()
    open_cascade_method()(launcher, {'item_kind': 'category'}, tree, item)
    assert (launcher.menu.position.x, launcher.menu.position.y) == (578, 252)
    assert launcher.menu.return_focus_widget is tree
    assert launcher.menu.return_focus_item is item
