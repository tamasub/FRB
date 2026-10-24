"""Selection <- must restore the originating expanded first-level button.

Run the actual Launcher.go_back method without Windows or PySide6: tests the
keyboard/back-button shared contract and leaves classic/nested behaviour alone.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def real_go_back():
    source = ast.parse((ROOT / 'src' / 'app.py').read_text(encoding='utf-8'))
    launcher = next(node for node in source.body
                    if isinstance(node, ast.ClassDef) and node.name == 'Launcher')
    method = next(node for node in launcher.body
                  if isinstance(node, ast.FunctionDef) and node.name == 'go_back')
    cls = ast.ClassDef(name='BackHandler', bases=[], keywords=[], body=[method], decorator_list=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
                 str(ROOT / 'src' / 'app.py'), 'exec'), namespace)
    return namespace['BackHandler']


class FakeView:
    def __init__(self, root_ids, visible=True):
        self.root_rows = [{'item_id': value} for value in root_ids]
        self.visible = visible
        self.focuses = []

    def isVisible(self):
        return self.visible

    def focus_root(self, **kwargs):
        self.focuses.append(kwargs)


class FakeSearch:
    def __init__(self, value=''):
        self.value = value

    def text(self):
        return self.value

    def clear(self):
        self.value = ''


class TestLauncher(real_go_back()):
    __test__ = False
    def __init__(self, *, mode='expanded', parent='mail', stack=(), query='', visible=True):
        self.selection = {'item_id': 'sales', 'parent_item_id': parent}
        self.view_mode = mode
        self.expanded_view = FakeView(['settings', 'zip', 'mail'], visible)
        self.stack = list(stack)
        self.search = FakeSearch(query)
        self.checked = {'a'}
        self.classic_focuses = 0
        self.list = SimpleNamespace(setFocus=self._classic_focus)
        self.changes = []

    def _classic_focus(self):
        self.classic_focuses += 1

    def _nav_before_change(self):
        self.changes.append('before')

    def _nav_after_change(self):
        self.changes.append('after')

    def render(self):
        self.changes.append('render')


def test_first_level_mail_selection_returns_to_mail_button():
    launcher = TestLauncher()
    launcher.go_back()
    assert launcher.selection is None
    assert launcher.checked == set()
    assert launcher.expanded_view.focuses == [{'item_id': 'mail'}]
    assert launcher.classic_focuses == 0
    assert launcher.changes == ['before', 'render', 'after']


def test_other_first_level_selection_returns_to_its_own_parent():
    launcher = TestLauncher(parent='zip')
    launcher.go_back()
    assert launcher.expanded_view.focuses == [{'item_id': 'zip'}]


def test_classic_selection_keeps_original_classic_focus():
    launcher = TestLauncher(mode='classic')
    launcher.go_back()
    assert launcher.expanded_view.focuses == []
    assert launcher.classic_focuses == 1


def test_nested_selection_does_not_jump_multiple_levels_to_first_level():
    launcher = TestLauncher(parent='nested_organization')
    launcher.go_back()
    assert launcher.expanded_view.focuses == []
    assert launcher.classic_focuses == 1


def test_search_result_selection_does_not_hijack_focus():
    launcher = TestLauncher(query='田中')
    launcher.go_back()
    assert launcher.expanded_view.focuses == []
    assert launcher.classic_focuses == 1


def test_hidden_expanded_view_falls_back_safely():
    launcher = TestLauncher(visible=False)
    launcher.go_back()
    assert launcher.expanded_view.focuses == []
    assert launcher.classic_focuses == 1


def test_stack_navigation_remains_separate_from_first_level_focus():
    launcher = TestLauncher(stack=[{'item_id': 'inside-mail'}])
    launcher.go_back()
    assert launcher.expanded_view.focuses == []
    assert launcher.classic_focuses == 1
    # First Back exits the choice grid; the existing category stack remains.
    assert launcher.stack == [{'item_id': 'inside-mail'}]
