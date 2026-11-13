"""Mini size and gesture boundary tests (do not require PySide6)."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from frb_kana_core import classify_flick
from mini_config import SIZE_PRESETS, DEFAULT_SIZE_INDEX, THRESHOLD_OPTIONS


class MiniSizingTests(unittest.TestCase):
    def test_remote_sized_initial_preset(self):
        remote = SIZE_PRESETS[DEFAULT_SIZE_INDEX]
        self.assertEqual((remote.outer_width, remote.outer_height), (200, 272))
        self.assertEqual(remote.threshold, 10)

    def test_other_sizes_and_legibility(self):
        self.assertEqual(len(SIZE_PRESETS), 4)
        self.assertEqual([x.outer_width for x in SIZE_PRESETS], [174, 186, 200, 222])
        self.assertEqual(sorted(x.outer_height for x in SIZE_PRESETS),
                         [x.outer_height for x in SIZE_PRESETS])
        for preset in SIZE_PRESETS:
            self.assertGreaterEqual(preset.key_height, 25)
            self.assertGreaterEqual(preset.guide_size, 68)
            self.assertIn(preset.threshold, THRESHOLD_OPTIONS)

    def test_all_thresholds_have_exact_transition(self):
        for threshold in THRESHOLD_OPTIONS:
            with self.subTest(threshold=threshold):
                self.assertEqual(classify_flick(threshold - 1, 0, threshold), 'center')
                self.assertEqual(classify_flick(-threshold, 0, threshold), 'left')
                self.assertEqual(classify_flick(threshold, 0, threshold), 'right')
                self.assertEqual(classify_flick(0, -threshold, threshold), 'up')
                self.assertEqual(classify_flick(0, threshold, threshold), 'down')
                self.assertIsNone(classify_flick(threshold, threshold, threshold))

    def test_default_sensitivity_reduced_from_original(self):
        self.assertLess(SIZE_PRESETS[DEFAULT_SIZE_INDEX].threshold, 18)


if __name__ == '__main__':
    unittest.main()
