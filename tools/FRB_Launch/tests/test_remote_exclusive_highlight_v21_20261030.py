from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RemoteExclusiveHighlightTests(unittest.TestCase):
    def test_remote_sets_inactive_property_for_other_panes(self):
        app = (ROOT / 'src/app.py').read_text(encoding='utf-8')
        self.assertIn("inactive = area != name", app)
        self.assertIn("pane.tree.setProperty('remoteInactive', inactive)", app)
        self.assertIn("pane.tree.setProperty('remoteInactive', False)", app)

    def test_stylesheet_disables_selected_fill_on_inactive_panes(self):
        src = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
        self.assertIn('QTreeWidget#expandedTree[remoteInactive="true"]::item:selected', src)
        self.assertIn('::item:selected:!active {{background:transparent', src)

if __name__ == '__main__':
    unittest.main()
