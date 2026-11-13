"""Regression guard: non-activating Remote retains the current pane fill."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RemoteCurrentHighlightTest(unittest.TestCase):
    def test_remote_logical_focus_used_for_row_paint(self):
        source = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
        self.assertIn('focused = (self.remote_logical_active if self.remote_highlight_mode', source)
        self.assertIn('::item:selected:!active {{background:{active};color:{text};}}', source)

    def test_remote_focus_switches_single_highlighted_pane(self):
        source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
        self.assertIn('pane.tree.remote_logical_active = (area == name)', source)
        self.assertIn('pane.tree.remote_logical_active = False', source)
        self.assertIn('pane.tree.viewport().update()', source)

if __name__ == '__main__':
    unittest.main()
