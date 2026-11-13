"""Window resize calculations can be validated even without PySide6."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from frame_geometry import resize_frame


class FrameGeometryTests(unittest.TestCase):
    def drag(self, edge, dx, dy=0, width=390, height=440):
        return resize_frame(edge, 100, 80, width, height, dx, dy, 300, 240, 800, 600)

    def test_right_and_bottom_keep_origin(self):
        self.assertEqual(self.drag('right', 80), (100,80,470,440))
        self.assertEqual(self.drag('bottom', 0, 80), (100,80,390,520))

    def test_left_and_top_keep_opposite_edges_fixed(self):
        self.assertEqual(self.drag('left', -50), (50,80,440,440))
        self.assertEqual(self.drag('top', 0, -70), (100,10,390,510))

    def test_minimum_width_and_height_clamp_anchored_edges(self):
        self.assertEqual(self.drag('left', 400), (190,80,300,440))
        self.assertEqual(self.drag('top', 0,400), (100,280,390,240))

    def test_maximum_width_and_height_clamp(self):
        self.assertEqual(self.drag('right', 10000), (100,80,800,440))
        self.assertEqual(self.drag('bottom', 0,10000), (100,80,390,600))

    def test_corner_changes_both_dimensions(self):
        self.assertEqual(self.drag('bottom-right', 40,50), (100,80,430,490))
        self.assertEqual(self.drag('top-left', -50,-70), (50,10,440,510))


if __name__ == '__main__':
    unittest.main()
