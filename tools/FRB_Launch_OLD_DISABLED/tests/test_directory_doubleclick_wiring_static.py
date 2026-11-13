"""Source integration checks runnable without a desktop Qt installation."""
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'src/app.py'


class FolderMouseWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.menu = next(n for n in cls.tree.body if isinstance(n, ast.ClassDef) and n.name == 'CascadeMenu')

    def function(self, name):
        return next(n for n in self.menu.body if isinstance(n, ast.FunctionDef) and n.name == name)

    def test_first_mouse_release_intercepts_folder_action(self):
        body = ast.get_source_segment(self.source, self.function('mouseReleaseEvent'))
        self.assertIn('_queue_folder_single_click(action)', body)
        self.assertIn('event.accept()', body)

    def test_double_click_queues_open_after_mouse_release(self):
        method = ast.get_source_segment(self.source, self.function('mouseDoubleClickEvent'))
        self.assertIn('_folder_double_click_row', method)
        released = ast.get_source_segment(self.source, self.function('_open_folder_after_release'))
        self.assertIn('QTimer.singleShot(0', released)
        self.assertIn('self.launcher.run_menu_item(r)', released)

    def test_long_scroll_view_uses_dedicated_double_clicked_handler(self):
        method = ast.get_source_segment(self.source, self.function('_enable_scroll_tree'))
        self.assertIn('tree.itemDoubleClicked.connect(self._scroll_double_clicked)', method)
        self.assertNotIn('tree.itemActivated.connect(self._scroll_activate)', method)
        filtered = ast.get_source_segment(self.source, self.function('eventFilter'))
        self.assertIn('self._folder_double_click_row is not None', filtered)

    def test_folders_use_existing_launcher_dispatch(self):
        method = ast.get_source_segment(self.source, self.function('_open_folder_after_release'))
        self.assertIn('self.launcher.run_menu_item', method)
        self.assertIn("'directory'", ast.get_source_segment(self.source, self.function('_folder_row')))


if __name__ == '__main__':
    unittest.main()
