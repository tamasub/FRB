"""Run with standard-library Python; exercise Qt-independent launcher methods."""
import ast
import types
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / 'src/app.py'
source = APP.read_text(encoding='utf-8')
module = ast.parse(source)
launcher = next(node for node in module.body if isinstance(node, ast.ClassDef) and
                any(method.name == 'set_list_column_mode' for method in node.body if isinstance(method, ast.FunctionDef)))
method_names = ('set_list_column_mode', 'fill_main_second_column', 'save_result_column_width', '_main_divider_hit', 'handle_main_column_resize')
methods = {}
for name in method_names:
    node = next(method for method in launcher.body if isinstance(method, ast.FunctionDef) and method.name == name)
    code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(APP), 'exec')
    from types import SimpleNamespace
    env = {
        'QEvent': SimpleNamespace(Type=SimpleNamespace(
            Resize='resize', Leave='leave', MouseMove='move', MouseButtonPress='press',
            MouseButtonRelease='release', MouseButtonDblClick='double')),
        'Qt': SimpleNamespace(CursorShape=SimpleNamespace(SplitHCursor='split'),
                              MouseButton=SimpleNamespace(LeftButton='left')),
    }
    exec(code, env)
    methods[name] = env[name]


class FakeSettings:
    def __init__(self):
        self.data = {}
    def value(self, key, default=None):
        return self.data.get(key, default)
    def setValue(self, key, value):
        self.data[key] = value


class FakeViewport:
    def __init__(self, width=500):
        self._width = width
    def width(self):
        return self._width
    def unsetCursor(self):
        pass
    def update(self):
        pass
    def setCursor(self, value):
        self.cursor = value
    def grabMouse(self):
        self.grabbed = True
    def releaseMouse(self):
        self.grabbed = False


class FakeList:
    def __init__(self):
        self.widths = [100, 100]
        self.vp = FakeViewport()
    def viewport(self):
        return self.vp
    def columnWidth(self, index):
        return self.widths[index]
    def setColumnWidth(self, index, width):
        self.widths[index] = width
    def columnViewportPosition(self, index):
        return sum(self.widths[:index])


class FakeLauncher:
    def __init__(self):
        self.settings = FakeSettings()
        self.list = FakeList()
        self._column_mode = None
        self._main_width_drag = None
        self._main_column_hover = False
        self._applying_column_layout = False
        self.selection = None
        self.hover_timer = type('FakeTimer', (), {'stop': lambda self: None})()
        self.pending_menu_item = None
    def saved_dimension(self, value, default, minimum, maximum):
        try:
            return max(minimum, min(int(value), maximum))
        except (TypeError, ValueError):
            return default


for name, method in methods.items():
    setattr(FakeLauncher, name, method)


class MainColumnLogicTests(unittest.TestCase):
    def setUp(self):
        self.w = FakeLauncher()

    def test_main_first_column_and_second_fill(self):
        self.w.set_list_column_mode(False)
        self.assertEqual(self.w.list.widths, [235, 265])
        self.w.list.setColumnWidth(0, 300)
        self.w.save_result_column_width(0, 235, 300)
        self.assertEqual(self.w.list.widths, [300, 200])
        self.assertEqual(self.w.settings.value('main_width_0'), 300)
        self.assertIsNone(self.w.settings.value('result_width_0'))

    def test_search_and_normal_widths_persist_independently(self):
        self.w.set_list_column_mode(False)
        self.w.list.setColumnWidth(0, 320)
        self.w.save_result_column_width(0, 235, 320)
        self.w.set_list_column_mode(True)
        self.assertEqual(self.w.list.widths, [180, 180])
        self.w.list.setColumnWidth(0, 230)
        self.w.save_result_column_width(0, 180, 230)
        self.w.list.setColumnWidth(1, 270)
        self.w.save_result_column_width(1, 180, 270)
        self.w.set_list_column_mode(False)
        self.assertEqual(self.w.list.widths, [320, 180])
        self.w.set_list_column_mode(True)
        self.assertEqual(self.w.list.widths, [230, 270])
        self.assertEqual(self.w.settings.value('main_width_0'), 320)
        self.assertEqual(self.w.settings.value('result_width_0'), 230)
        self.assertEqual(self.w.settings.value('result_width_1'), 270)

    def test_settings_not_overwritten_by_programmatic_mode_switch(self):
        self.w.settings.setValue('result_width_0', 330)
        self.w.settings.setValue('result_width_1', 190)
        self.w.settings.setValue('main_width_0', 260)
        self.w.set_list_column_mode(True)
        self.w.set_list_column_mode(False)
        self.assertEqual(self.w.settings.data, dict(result_width_0=330, result_width_1=190, main_width_0=260))

    def test_main_width_clamps_on_viewport_shrink(self):
        self.w.settings.setValue('main_width_0', 420)
        self.w.list.vp._width = 340
        self.w.set_list_column_mode(False)
        self.assertEqual(self.w.list.widths, [270, 70])
        self.w.list.vp._width = 650
        self.w.fill_main_second_column()
        self.assertEqual(self.w.list.widths, [270, 380])

    def test_invisible_divider_hit_only_in_main(self):
        self.w.set_list_column_mode(False)
        self.assertTrue(self.w._main_divider_hit(233))
        self.assertFalse(self.w._main_divider_hit(210))
        self.w.set_list_column_mode(True)
        self.assertFalse(self.w._main_divider_hit(180))

    def test_popup_anchored_to_viewport_not_item_width(self):
        cascade = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == 'cascade')
        body = ast.get_source_segment(source, cascade)
        self.assertIn('viewport.width() - 1', body)
        self.assertNotIn('visualItemRect(q or self.list.currentItem()).topRight()', body)
        # Existing keyboard/hover cascade behavior is preserved.
        self.assertIn('self.menu.popup(pos)', body)
        self.assertIn('self.menu.setFocus()', body)

    def test_headerless_main_divider_mouse_drag_changes_only_main_width(self):
        self.w.set_list_column_mode(False)
        class Event:
            def __init__(self, kind, x):
                self.kind, self.x, self.accepted = kind, x, False
            def type(self):
                return self.kind
            def position(self):
                return self
            def toPoint(self):
                return type('Point', (), {'x': lambda _: self.x})()
            def button(self):
                return 'left'
            def accept(self):
                self.accepted = True
        def emit(kind, x):
            event = Event(kind, x)
            result = self.w.handle_main_column_resize(event)
            return result, event.accepted
        self.assertEqual(emit('press', 235), (True, True))
        self.assertEqual(emit('move', 275), (True, True))
        self.assertEqual(self.w.list.columnWidth(0), 275)
        self.assertEqual(emit('release', 275), (True, True))
        self.assertEqual(self.w.settings.value('main_width_0'), 275)
        self.assertFalse(self.w.list.viewport().grabbed)
        self.assertIsNone(self.w.settings.value('result_width_0'))

    def test_main_drag_ignores_regular_row_clicks(self):
        self.w.set_list_column_mode(False)
        class Event:
            def type(self): return 'press'
            def position(self): return self
            def toPoint(self): return type('P', (), {'x': lambda _: 15})()
            def button(self): return 'left'
        self.assertFalse(self.w.handle_main_column_resize(Event()))
        self.assertIsNone(self.w._main_width_drag)

    def test_hidden_header_event_filter_wired(self):
        filter_node = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == 'eventFilter')
        body = ast.get_source_segment(source, filter_node)
        self.assertIn('handle_main_column_resize(event)', body)
        resize_node = next(node for node in launcher.body if isinstance(node, ast.FunctionDef) and node.name == 'handle_main_column_resize')
        resize = ast.get_source_segment(source, resize_node)
        self.assertIn('MouseButtonPress', resize)
        self.assertIn('MouseMove', resize)
        self.assertIn('MouseButtonRelease', resize)


if __name__ == '__main__':
    unittest.main()
