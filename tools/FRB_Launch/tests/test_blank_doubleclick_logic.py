"""Pure-Python tests for the launcher's mouse-event decision path (no Qt runtime)."""
import ast
from pathlib import Path
import types
import unittest


class _Base:
    def eventFilter(self, obj, event):
        return False


source = ast.parse((Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8'))
launcher = next(c for c in source.body if isinstance(c, ast.ClassDef) and c.name == 'Launcher')
method = next(n for n in launcher.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
code = compile(ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name='TestLauncher', bases=[ast.Name(id='_Base', ctx=ast.Load())], keywords=[], body=[method], decorator_list=[])], type_ignores=[])), '<launcher-event-filter>', 'exec')
# Only the mouse-doubleclick early branch is executed here.
Qt = types.SimpleNamespace(MouseButton=types.SimpleNamespace(LeftButton='left'))
QEvent = types.SimpleNamespace(Type=types.SimpleNamespace(MouseButtonDblClick='double', KeyPress='key', InputMethod='ime'))
namespace = dict(_Base=_Base, Qt=Qt, QEvent=QEvent)
exec(code, namespace)


class _Click:
    def __init__(self, button='left', hit=False):
        self._button = button
        self.hit = hit
        self.accepted = False
    def type(self): return 'double'
    def button(self): return self._button
    def position(self): return self
    def toPoint(self): return self
    def accept(self): self.accepted = True


class BlankDoubleClickLogicTests(unittest.TestCase):
    def setUp(self):
        self.w = namespace['TestLauncher']()
        self.viewport = object()
        self.w.list = types.SimpleNamespace(viewport=lambda: self.viewport, itemAt=lambda e: object() if e.hit else None)
        self.w.tabs = object()
        self.w.search = object()
        self.w.stack = ['parent']
        self.w.selection = None
        self.w.calls = 0
        self.w.go_back = lambda: setattr(self.w, 'calls', self.w.calls + 1)

    def check(self, click, should_back):
        result = self.w.eventFilter(self.viewport, click)
        self.assertEqual(result, should_back)
        self.assertEqual(click.accepted, should_back)
        self.assertEqual(self.w.calls, int(should_back))

    def test_left_on_empty_submenu_goes_back(self): self.check(_Click(), True)
    def test_left_on_row_is_ignored(self): self.check(_Click(hit=True), False)
    def test_right_on_empty_is_ignored(self): self.check(_Click(button='right'), False)
    def test_root_empty_is_ignored(self):
        self.w.stack = []
        self.check(_Click(), False)
    def test_selection_goes_back(self):
        self.w.stack = []
        self.w.selection = object()
        self.check(_Click(), True)
    def test_other_widgets_are_ignored(self):
        result = self.w.eventFilter(object(), _Click())
        self.assertFalse(result)
        self.assertEqual(self.w.calls, 0)


if __name__ == '__main__': unittest.main()
