"""One-level Left-navigation contract, without requiring Windows/PySide6."""
import ast
from pathlib import Path
from types import SimpleNamespace

APP = Path(__file__).resolve().parents[1] / 'src' / 'app.py'


class FocusWidget:
    def __init__(self):
        self.focused = False
    def isVisible(self):
        return True
    def setFocus(self, reason=None):
        self.focused = True


class FocusTree(FocusWidget):
    def __init__(self):
        super().__init__()
        self.selected = None
        self.scrolled = None
    def setCurrentItem(self, item):
        self.selected = item
    def scrollToItem(self, item):
        self.scrolled = item


def extracted_cascade():
    source = ast.parse(APP.read_text(encoding='utf8'))
    original = next(n for n in source.body
                    if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')
    method = next(n for n in original.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'close_one_level')
    cls = ast.ClassDef(name='CascadeMenu', bases=[], keywords=[],
                       body=[method], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[]))
    ns = {'Qt': SimpleNamespace(FocusReason=SimpleNamespace(TabFocusReason=1)),
          'QTreeWidget': FocusTree}
    exec(compile(module, str(APP), 'exec'), ns)
    return ns['CascadeMenu']


def menu_stub(klass, parent, *, origin=None, origin_item=None, owner=None):
    class FakeMenu(klass):
        def __init__(self):
            self._parent = parent
            self.return_focus_widget = origin
            self.return_focus_item = origin_item
            self.owner_action = owner
            self.closed = False
            self.focused = False
            self.selected_action = None
            self.launcher = SimpleNamespace(
                expanded_view=SimpleNamespace(isVisible=lambda: False),
                list=FocusWidget())
        def parentWidget(self): return self._parent
        def close(self): self.closed = True
        def isVisible(self): return not self.closed
        def setActiveAction(self, action): self.selected_action = action
        def setFocus(self, reason=None): self.focused = True
    return FakeMenu()


def test_root_cascade_left_closes_just_one_and_focuses_its_button():
    cls = extracted_cascade()
    origin = FocusWidget()
    root = menu_stub(cls, object(), origin=origin)
    root.close_one_level()
    assert root.closed
    assert origin.focused


def test_left_from_second_cascade_retains_first_then_returns_to_root():
    cls = extracted_cascade()
    origin = FocusWidget()
    first = menu_stub(cls, object(), origin=origin)
    selected_parent_action = object()
    second = menu_stub(cls, first, owner=selected_parent_action)
    second.close_one_level()
    assert second.closed
    assert not first.closed  # Only the deepest level closes.
    assert first.selected_action is selected_parent_action
    assert first.focused
    assert not origin.focused
    first.close_one_level()
    assert first.closed
    assert origin.focused


def test_cascade_opened_from_bookmark_row_restores_selected_row():
    cls = extracted_cascade()
    tree = FocusTree()
    original_item = object()
    popup = menu_stub(cls, object(), origin=tree, origin_item=original_item)
    popup.close_one_level()
    assert popup.closed
    assert tree.selected is original_item
    assert tree.scrolled is original_item
    assert tree.focused


def test_root_origin_is_recorded_when_cascade_opened():
    s = APP.read_text(encoding='utf8')
    assert 'self.menu.return_focus_widget = widget' in s
    assert 'self.menu.return_focus_item = item' in s
    assert 'self.close_one_level()' in s
