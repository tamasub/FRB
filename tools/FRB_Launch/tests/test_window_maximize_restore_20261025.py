"""Regression: titlebar controls and maximized geometry must not poison state.ini.

Uses real Launcher method bodies with fake Qt state so it runs on CI without
PySide6. Windows GUI verification is still required for native frame behavior.
"""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text('utf-8')
TREE = ast.parse(SOURCE)
LAUNCHER = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Launcher')
METHODS = {n.name: n for n in LAUNCHER.body if isinstance(n, ast.FunctionDef)}

# Compile only actual app.py methods, no Qt import or replaced business logic.
NAMES = ('can_save_normal_window_geometry', 'view_size_keys', 'saved_dimension',
         'restore_window_size', 'save_window_size', 'save_window_height',
         'restore_normal_window_geometry', 'show_launcher_normal_or_saved',
         'toggle_maximize_restore', 'dismiss')
probe_class = ast.ClassDef(name='WindowProbe', bases=[], keywords=[],
                           body=[copy.deepcopy(METHODS[n]) for n in NAMES], decorator_list=[])
module = ast.fix_missing_locations(ast.Module(body=[probe_class], type_ignores=[]))
namespace = {'Qt': SimpleNamespace(WindowState=SimpleNamespace(WindowMaximized=2))}
exec(compile(module, '<Launcher window methods>', 'exec'), namespace)
WindowProbe = namespace['WindowProbe']


class FakeSettings:
    def __init__(self):
        self.values = {}
    def setValue(self, key, value):
        self.values[key] = value
    def value(self, key, default=None):
        return self.values.get(key, default)
    def sync(self):
        pass


class Probe(WindowProbe):
    def __init__(self, view_mode='expanded'):
        self.view_mode = view_mode
        self.settings = FakeSettings()
        self._w = 845
        self._h = 560
        self._normal_size = (self._w, self._h)
        self._pos = (127, 84)
        self._state = 0
        self._visible = True
        self.page_id = 'work'
        self.expanded_view = SimpleNamespace(hide_favorite_popup=lambda: None)
        self.hover_timer = SimpleNamespace(stop=lambda: None)
        self.menu = None
        self.icon_updates = 0

    def isMaximized(self):
        return bool(self._state & 2)
    def isMinimized(self):
        return False  # This fixture exercises maximize/restore, not native minimize.
    def minimumWidth(self):
        return 300
    def minimumHeight(self):
        return 240
    def screen(self):
        return SimpleNamespace(availableGeometry=lambda: SimpleNamespace(width=lambda: 1920, height=lambda: 1040))
    def resize(self, width, height):
        self._w, self._h = width, height
    def windowState(self):
        return self._state
    def width(self):
        return self._w
    def height(self):
        return self._h
    def pos(self):
        return self._pos
    def move(self, pos):
        self._pos = pos
    def isVisible(self):
        return self._visible
    def showMaximized(self):
        # Native resize can be emitted before or after WindowMaximized is set.
        # During either ordering, maximized size must not overwrite state.ini.
        self._w, self._h = (1920, 1080)
        self.save_window_size()
        self._state = 2
        self.save_window_size()
        self._pos = (0, 0)
    def showNormal(self):
        self._state = 0
        self._w, self._h = self._normal_size
    def update_header_icons(self):
        self.icon_updates += 1
    def hide(self):
        self._visible = False
    def show(self):
        self._visible = True
    def setWindowState(self, state):
        self._state = state
        if not self._state:
            self._w, self._h = self._normal_size
    def save_last_current(self):
        pass
    def finish_cloud_link_handoff(self):
        pass  # Existing dismiss() dependency, independent of window geometry.
    def hide_history_popup(self):
        pass


class WindowMaximizePersistenceTests(unittest.TestCase):
    def test_titlebar_minimize_button_is_available_only_in_normal_mode(self):
        source = SOURCE
        self.assertIn('self.minimize_button.clicked.connect(self.minimize_launcher)', source)
        self.assertIn('self.minimize_button.setVisible(not self.dismiss_on_outside_click)', source)
        self.assertIn('self.maximize_button.clicked.connect(self.toggle_maximize_restore)', source)
        self.assertIn('self.close_button.clicked.connect(self.dismiss)', source)

    def test_maximize_saves_only_normal_size_and_position(self):
        w = Probe()
        w.toggle_maximize_restore()
        self.assertEqual((w.width(), w.height()), (1920, 1080))
        self.assertEqual(w.settings.values['expanded_window_width'], 845)
        self.assertEqual(w.settings.values['expanded_window_height'], 560)
        self.assertEqual(w.settings.values['position'], (127, 84))
        self.assertTrue(w.isMaximized())
        self.assertEqual(w.icon_updates, 1)
        w.save_window_size()
        self.assertEqual(w.settings.values['expanded_window_width'], 845)
        self.assertEqual(w.settings.values['expanded_window_height'], 560)

    def test_hide_maximized_does_not_save_maximized_geometry_and_reopens_normally(self):
        w = Probe()
        w.toggle_maximize_restore()
        w.dismiss()
        self.assertFalse(w.isVisible())
        self.assertFalse(w.isMaximized())
        self.assertEqual(w.settings.values['expanded_window_width'], 845)
        self.assertEqual(w.settings.values['expanded_window_height'], 560)
        self.assertEqual(w.settings.values['position'], (127, 84))
        w.show()
        self.assertFalse(w.isMaximized())
        self.assertEqual((w.width(), w.height()), (845, 560))

    def test_restore_button_forces_saved_normal_geometry_after_qt_restore(self):
        w = Probe()
        w.toggle_maximize_restore()
        # Some native Qt.Tool windows retain their maximized rectangle even
        # when showNormal clears WindowMaximized; the fix must resize them.
        def native_show_normal_that_keeps_huge_rectangle():
            w._state = 0
        w.showNormal = native_show_normal_that_keeps_huge_rectangle
        w.toggle_maximize_restore()
        self.assertEqual((w.width(), w.height()), (845, 560))
        self.assertEqual(w.pos(), (127, 84))
        self.assertFalse(w.isMaximized())

    def test_hidden_maximized_geometry_is_reapplied_on_next_summon(self):
        w = Probe()
        w.toggle_maximize_restore()
        w.dismiss()
        self.assertTrue(w._restore_normal_on_show)
        w._w, w._h = (1920, 1080)  # A native HWND can retain the large frame.
        def native_show_normal_that_keeps_huge_rectangle():
            w._state = 0
            w._visible = True
        w.showNormal = native_show_normal_that_keeps_huge_rectangle
        w.show_launcher_normal_or_saved()
        self.assertEqual((w.width(), w.height()), (845, 560))
        self.assertEqual(w.pos(), (127, 84))
        self.assertFalse(w._restore_normal_on_show)

    def test_launcher_summon_and_menu_summon_use_safe_window_show(self):
        source = SOURCE
        self.assertIn('self.show_launcher_normal_or_saved();self.raise_();self.activateWindow()', source)
        self.assertIn('self.show_launcher_normal_or_saved()\n        self.raise_()', source)

    def test_normal_resizing_still_persists_for_both_views(self):
        for mode, w_key, h_key in (
                ('classic', 'window_width', 'window_height'),
                ('expanded', 'expanded_window_width', 'expanded_window_height')):
            w = Probe(view_mode=mode)
            w._w, w._h = (640, 475)
            w.save_window_size()
            self.assertEqual((w.settings.values[w_key], w.settings.values[h_key]), (640, 475))
            w._state = 2
            w._w, w._h = (1920, 1080)
            w.save_window_height()
            self.assertEqual((w.settings.values[w_key], w.settings.values[h_key]), (640, 475))

    def test_recovers_legacy_screen_sized_window_on_initial_restore(self):
        for mode, width_key, height_key, expected in (
                ('classic', 'window_width', 'window_height', (390, 440)),
                ('expanded', 'expanded_window_width', 'expanded_window_height', (1060, 670))):
            w = Probe(view_mode=mode)
            w.settings.setValue(width_key, 1920)
            w.settings.setValue(height_key, 1040)
            w.restore_window_size()
            self.assertEqual((w.width(), w.height()), expected)

    def test_resize_event_guards_maximized_geometry(self):
        code = ast.get_source_segment(SOURCE, METHODS['resizeEvent'])
        self.assertIn('self.can_save_normal_window_geometry()', code)
        self.assertIn('self.settings.setValue(key_w, self.width())', code)
        self.assertIn('self.settings.setValue(key_h, self.height())', code)


if __name__ == '__main__':
    unittest.main()
