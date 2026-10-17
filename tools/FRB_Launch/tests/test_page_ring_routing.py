"""Regression that the Page tab participates only in root navigation."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')


class PageRingRoutingTest(unittest.TestCase):
    def test_root_predicate_excludes_search_submenus_and_selection(self):
        self.assertIn('not self.search.text().strip() and not self.stack', SOURCE)
        self.assertIn('and self.selection is None', SOURCE)

    def test_page_tab_focus_used_at_endpoint(self):
        self.assertIn('self.tabs.setFocus(Qt.FocusReason.TabFocusReason)', SOURCE)
        self.assertIn('self.move_root_page_selection(direction, from_tab=True)', SOURCE)
        self.assertIn('self.move_root_page_selection(direction)', SOURCE)

    def test_search_and_submenus_keep_list_only_wrap(self):
        self.assertIn('move_tree_selection(self.list, direction)', SOURCE)


if __name__ == '__main__':
    unittest.main()
