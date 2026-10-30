from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RemoteExclusiveHighlightTests(unittest.TestCase):
    def test_remote_mode_has_priority_over_actual_focus(self):
        source = (ROOT / "src" / "expanded_view.py").read_text(encoding="utf-8")
        self.assertIn("self.remote_highlight_mode = False", source)
        self.assertIn("focused = (self.remote_logical_active if self.remote_highlight_mode", source)
        self.assertNotIn("self._column_is_focused() or self.remote_logical_active", source)

    def test_remote_lifecycle_enforces_exclusive_active_pane(self):
        source = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
        self.assertIn("pane.tree.remote_highlight_mode = True", source)
        self.assertIn("pane.tree.remote_logical_active = (area == name)", source)
        self.assertIn("pane.tree.remote_highlight_mode = False", source)

if __name__ == '__main__':
    unittest.main()
