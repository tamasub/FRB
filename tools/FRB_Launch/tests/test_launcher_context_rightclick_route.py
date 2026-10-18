"""Qt-free event dispatch regression: first right click resolves the actual row."""
import ast
import pathlib
import types
import unittest

APP = pathlib.Path(__file__).resolve().parents[1] / 'app.py'


def load_guard():
    tree = ast.parse(APP.read_text(encoding='utf-8'))
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if cls.name == 'Launcher'
                  and isinstance(node, ast.FunctionDef) and node.name == 'eventFilter')
    # Run the exact opening right-button guard without importing the Qt runtime.
    # The first viewport guard dismisses non-grabbing cascades, the second
    # dispatches the same right-button click to the context menu.
    right_button_guards = method.body[:2]
    assert all(isinstance(guard, ast.If) for guard in right_button_guards)
    fn = ast.FunctionDef(name='guard', args=method.args,
                         body=[*right_button_guards, ast.Return(value=ast.Constant(False))],
                         decorator_list=[])
    module = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(module)
    class EventTypes:
        MouseButtonPress = 1
        MouseButtonRelease = 2
        ContextMenu = 3
    qt = types.SimpleNamespace(MouseButton=types.SimpleNamespace(RightButton=2, LeftButton=1),
                               ItemDataRole=types.SimpleNamespace(UserRole=32))
    scope = {'QEvent': types.SimpleNamespace(Type=EventTypes), 'Qt': qt}
    exec(compile(module, str(APP), 'exec'), scope)
    return scope['guard'], EventTypes


class MouseEvent:
    def __init__(self, kind, pos=8):
        self.kind = kind
        self.xy = pos
        self.accepted = False
    def type(self): return self.kind
    def button(self): return 2
    def position(self): return types.SimpleNamespace(toPoint=lambda: self.xy)
    def globalPosition(self): return types.SimpleNamespace(toPoint=lambda: (100, self.xy))
    def accept(self): self.accepted = True


class Widget:
    def __init__(self, row):
        self.row = row
        self.viewport_object = object()
        self.calls = []
        self.current = None
        self.list = self
        self.dismissed = 0
    def close_cascade_for_main_interaction(self): self.dismissed += 1
    def page_empty_area_can_open_context(self, position): return position == 9
    def viewport(self): return self.viewport_object
    def itemAt(self, pos): return self.row if pos == 8 else None
    def setCurrentItem(self, row): self.current = row
    def show_launch_context_menu(self, pos, row):
        self.calls.append((pos, row))
        return True


class Row:
    def data(self, col, role): return {'item_id': 'exact-id'}


class RightClickRoutingTests(unittest.TestCase):
    def test_first_right_click_on_row_opens_properties_target(self):
        guard, typ = load_guard()
        ctx = Widget(Row())
        self.assertTrue(guard(ctx, ctx.viewport_object, MouseEvent(typ.MouseButtonPress)))
        self.assertEqual(ctx.calls, [])
        self.assertTrue(guard(ctx, ctx.viewport_object, MouseEvent(typ.MouseButtonRelease)))
        self.assertEqual(ctx.calls[0], ((100, 8), {'item_id': 'exact-id'}))
        self.assertIsNotNone(ctx.current)
        self.assertEqual(ctx.dismissed, 1)

    def test_first_right_click_on_empty_area_opens_page_menu(self):
        guard, typ = load_guard()
        ctx = Widget(Row())
        guard(ctx, ctx.viewport_object, MouseEvent(typ.MouseButtonPress, 9))
        guard(ctx, ctx.viewport_object, MouseEvent(typ.MouseButtonRelease, 9))
        self.assertEqual(ctx.calls, [((100, 9), None)])
        self.assertIsNone(ctx.current)

    def test_following_native_context_event_is_consumed(self):
        guard, typ = load_guard()
        ctx = Widget(Row())
        evt = MouseEvent(typ.ContextMenu)
        self.assertTrue(guard(ctx, ctx.viewport_object, evt))
        self.assertTrue(evt.accepted)
        self.assertFalse(ctx.calls)


if __name__ == '__main__': unittest.main()
