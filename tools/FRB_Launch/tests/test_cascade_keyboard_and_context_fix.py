"""Regression for Tool-window cascade keyboard ownership and anchored Properties.

Pure-code tests run on CI/Linux with no Qt.  Native integration tests run when
PySide6 is available (use QT_QPA_PLATFORM=offscreen outside Windows).
"""
import ast
import os
import pathlib
import types
import unittest
from unittest.mock import Mock, patch

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'app.py'
CODE = SOURCE.read_text(encoding='utf-8')
PARSED = ast.parse(CODE)


def isolated_method(cls, name, extras):
    node = next(n for n in PARSED.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == name)
    mod = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = dict(extras)
    exec(compile(mod, str(SOURCE), 'exec'), ns)
    return ns[name]


class PureRegressionTests(unittest.TestCase):
    def test_right_click_opens_context_without_dismissing_tool_column(self):
        fn = isolated_method('CascadeMenu', '_open_context_properties', {})
        launcher = Mock()
        launcher.isVisible.return_value = True
        column = types.SimpleNamespace(launcher=launcher)
        row = {'item_id': 'zip_create'}
        fn(column, row, (10, 20))
        launcher.show_launch_context_menu.assert_called_once_with(
            (10, 20), row, context_parent=column)
        launcher.close_cascade_for_main_interaction.assert_not_called()

    def test_deepest_visible_cascade_owns_main_keyboard(self):
        fn = isolated_method('Launcher', 'visible_cascade_for_keyboard', {})
        inner = types.SimpleNamespace(isVisible=lambda: True, child=None)
        outer = types.SimpleNamespace(isVisible=lambda: True, child=inner)
        holder = types.SimpleNamespace(menu=outer)
        self.assertIs(fn(holder), inner)
        inner.isVisible = lambda: False
        self.assertIs(fn(holder), outer)
        outer.isVisible = lambda: False
        self.assertIsNone(fn(holder))

    def test_actual_launcher_event_filter_routes_main_enter_to_column(self):
        node = next(n for n in PARSED.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
        # Compile the real first three if blocks: main right-click, viewport
        # context menu, then keyboard relay (no copy of implementation).
        guarded = ast.FunctionDef(name='dispatch', args=fn.args,
                                  body=[*fn.body[:3], ast.Return(value=ast.Constant(False))],
                                  decorator_list=[])
        mod = ast.Module(body=[guarded], type_ignores=[])
        ast.fix_missing_locations(mod)
        event_kinds = types.SimpleNamespace(KeyPress=8, MouseButtonPress=1,
                                            MouseButtonRelease=2, ContextMenu=3)
        qt = types.SimpleNamespace(MouseButton=types.SimpleNamespace(LeftButton=1, RightButton=2))
        ns = {'Qt': qt, 'QEvent': types.SimpleNamespace(Type=event_kinds),
              'QApplication': types.SimpleNamespace(activePopupWidget=lambda: None)}
        exec(compile(mod, str(SOURCE), 'exec'), ns)
        class List:
            def viewport(self): return object()
        column = types.SimpleNamespace(keyPressEvent=Mock())
        dummy = types.SimpleNamespace(list=List(), tabs=object(), search=object(),
                                      visible_cascade_for_keyboard=lambda: column)
        evt = types.SimpleNamespace(type=lambda: 8, accept=Mock())
        self.assertTrue(ns['dispatch'](dummy, dummy.list, evt))
        column.keyPressEvent.assert_called_once_with(evt)
        evt.accept.assert_called_once()

    def test_launcher_key_filter_intercepts_before_main_enter(self):
        node = next(n for n in PARSED.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
        src = ast.get_source_segment(CODE, fn)
        self.assertLess(src.index('column.keyPressEvent(event)'),
                        src.index('if k in (Qt.Key.Key_Return,Qt.Key.Key_Enter):'))
        self.assertIn('QApplication.activePopupWidget() is None', src)

    def test_enter_runs_highlighted_command_without_main_selection(self):
        # Execute the actual CascadeMenu handler with lightweight Qt stand-ins.
        class Key:
            Key_Return = 16777220
            Key_Enter = 16777221
            Key_Down = 16777237
            Key_Up = 16777235
            Key_Escape = 16777216
            Key_Left = 16777234
            Key_Right = 16777236
        qt = types.SimpleNamespace(Key=Key, KeyboardModifier=types.SimpleNamespace(
            ControlModifier=1, AltModifier=2))
        fn = isolated_method('CascadeMenu', 'keyPressEvent',
                             {'Qt': qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {})})
        row = {'item_id': 'zip_create', 'item_kind': 'command'}
        class Action:
            def data(self): return row
            def isEnabled(self): return True
        action = Action()
        menu = types.SimpleNamespace(hover_timer=Mock(), scroll_tree=None,
                                     launcher=types.SimpleNamespace(run_menu_item=Mock()),
                                     activeAction=lambda: action, openers={}, filter_action=None,
                                     page_key=lambda event: False)
        menu.launcher.page_key = Mock(return_value=False)
        event = types.SimpleNamespace(key=lambda: Key.Key_Return, modifiers=lambda: 0,
                                      accept=Mock())
        fn(menu, event)
        menu.launcher.run_menu_item.assert_called_once_with(row)
        event.accept.assert_called_once()

    def test_enter_opens_category_child_instead_of_executing(self):
        class Key:
            Key_Return = 16777220
            Key_Enter = 16777221
            Key_Down = 16777237
            Key_Up = 16777235
            Key_Escape = 16777216
            Key_Left = 16777234
            Key_Right = 16777236
        qt = types.SimpleNamespace(Key=Key, KeyboardModifier=types.SimpleNamespace(
            ControlModifier=1, AltModifier=2))
        fn = isolated_method('CascadeMenu', 'keyPressEvent',
                             {'Qt': qt, 'AppCascadeMenu': type('AppCascadeMenu', (), {})})
        row = {'item_id': 'zip_category', 'item_kind': 'category'}
        class Action:
            def data(self): return row
            def isEnabled(self): return True
        action = Action()
        menu = types.SimpleNamespace(hover_timer=Mock(), scroll_tree=None,
                                     launcher=types.SimpleNamespace(page_key=lambda ev: False,
                                                                    run_menu_item=Mock()),
                                     activeAction=lambda: action, openers={action: lambda: None},
                                     open_current=Mock(), filter_action=None)
        event = types.SimpleNamespace(key=lambda: Key.Key_Return, modifiers=lambda: 0,
                                      accept=Mock())
        fn(menu, event)
        menu.open_current.assert_called_once_with()
        menu.launcher.run_menu_item.assert_not_called()

    def test_context_menu_uses_source_column_as_parent(self):
        node = next(n for n in PARSED.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
        fn = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'show_launch_context_menu')
        self.assertIn('context_parent if context_parent is not None else self',
                      ast.get_source_segment(CODE, fn))


try:
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    import app
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication is not None, 'Requires PySide6 for native Qt regression')
class NativeCascadeRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.w = app.Launcher()
        self.w.show()
        self.qt.processEvents()

    def tearDown(self):
        self.w.close_cascade_for_main_interaction()
        self.w.tray.hide()
        self.w.close()
        self.qt.processEvents()

    def test_enter_from_main_list_executes_cascade_row(self):
        parent = next(r for r in self.w.data['items'] if r.get('item_id') == 'dates')
        self.w.cascade(parent)
        menu = self.w.menu
        action = next(a for a in menu.actions()
                      if isinstance(a.data(), dict) and a.data().get('item_id') == 'today')
        menu.setActiveAction(action)
        self.w.list.setFocus()
        with patch.object(self.w, 'run_menu_item') as execute:
            QTest.keyClick(self.w.list, Qt.Key.Key_Return)
            self.qt.processEvents()
            execute.assert_called_once_with(action.data())

    def test_cascade_context_retains_displayed_menu(self):
        parent = next(r for r in self.w.data['items'] if r.get('item_id') == 'dates')
        self.w.cascade(parent)
        menu = self.w.menu
        action = next(a for a in menu.actions()
                      if isinstance(a.data(), dict) and a.data().get('item_id') == 'today')
        with patch.object(self.w, 'show_launch_context_menu', return_value=True) as context:
            QTest.mouseClick(menu, Qt.MouseButton.RightButton,
                             pos=menu.actionGeometry(action).center())
            self.qt.processEvents()
            self.assertTrue(menu.isVisible())
            context.assert_called_once()


if __name__ == '__main__':
    unittest.main()
