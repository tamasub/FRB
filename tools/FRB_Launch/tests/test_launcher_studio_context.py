"""Direct Launch->Studio context commands without requiring a Qt display."""
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1].joinpath('src/app.py').read_text(encoding='utf-8')

class LauncherStudioContextTests(unittest.TestCase):
    def test_context_event_uses_hit_test(self):
        self.assertIn('self.list.itemAt(event.position().toPoint())', SOURCE)
        self.assertIn('def contextMenuEvent(self, event):', SOURCE)
        self.assertIn('event.button() == Qt.MouseButton.RightButton', SOURCE)
        self.assertIn('QEvent.Type.MouseButtonRelease', SOURCE)

    def test_empty_creates_category_in_current_page(self):
        self.assertIn('launch_configuration_studio(new_category=True)', SOURCE)
        self.assertIn("'--launch-new-category=' + str(self.page_id)", SOURCE)

    def test_page_properties_targets_the_page_group_not_an_item(self):
        self.assertIn("'--launch-page-id=' + str(self.page_id)", SOURCE)
        self.assertIn('launch_configuration_studio(page_properties=True)', SOURCE)
        self.assertIn("menu.addAction('プロパティ',", SOURCE)

    def test_item_properties_by_stable_item_id(self):
        self.assertIn("'--launch-item-id=' + str(item_id)", SOURCE)
        self.assertIn("elif origin == 'studio':", SOURCE)
        self.assertIn('resolve_context_target(row, self.authored_items)', SOURCE)

    def test_exclude_virtual_search_results(self):
        self.assertIn("self.authored_items = fresh['items']", SOURCE)
        self.assertIn("elif origin in ('file', 'folder'):", SOURCE)

    def test_launches_studio_native_shell_without_touching_json(self):
        self.assertIn("'launch_action_type': 'Run'", SOURCE)
        self.assertIn("'--open-json=' + str(CONFIG)", SOURCE)
        self.assertIn("'launch_wait_for_exit': False", SOURCE)

if __name__=='__main__': unittest.main()
