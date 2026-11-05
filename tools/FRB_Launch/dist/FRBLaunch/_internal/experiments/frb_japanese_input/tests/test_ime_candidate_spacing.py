"""Pure model tests for adjustable native IME candidate-popup clearance."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mini_config import (
    DEFAULT_SIZE_INDEX, SIZE_PRESETS,
    DEFAULT_IME_CANDIDATE_GAP, IME_CANDIDATE_GAP_OPTIONS,
    candidate_spaced_client_height,
)


class CandidateSpacingTests(unittest.TestCase):
    def test_default_is_spacious_within_a_compact_width(self):
        spec = SIZE_PRESETS[DEFAULT_SIZE_INDEX]
        self.assertEqual(spec.outer_width, 200)
        self.assertEqual(DEFAULT_IME_CANDIDATE_GAP, 260)
        self.assertEqual(candidate_spaced_client_height(spec, 260, 27),
                         spec.outer_height - 27 + 260)

    def test_gap_presets_allow_full_compact_mode(self):
        self.assertIn(0, IME_CANDIDATE_GAP_OPTIONS)
        self.assertIn(320, IME_CANDIDATE_GAP_OPTIONS)
        self.assertEqual(tuple(sorted(set(IME_CANDIDATE_GAP_OPTIONS))),
                         IME_CANDIDATE_GAP_OPTIONS)

    def test_gap_extends_only_height_for_all_sizes(self):
        for spec in SIZE_PRESETS:
            for gap in IME_CANDIDATE_GAP_OPTIONS:
                with self.subTest(preset=spec.name, gap=gap):
                    base = candidate_spaced_client_height(spec, 0, 27)
                    self.assertEqual(candidate_spaced_client_height(spec, gap, 27), base + gap)

    def test_invalid_gap_rejected(self):
        with self.assertRaises(ValueError):
            candidate_spaced_client_height(SIZE_PRESETS[DEFAULT_SIZE_INDEX], 17, 27)


if __name__ == "__main__":
    unittest.main()
