"""v0.3 modifier and punctuation behavior regression tests (no GUI required)."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from frb_kana_core import (
    DIRECTIONS, KEY_LAYOUT, MODIFIER_KEY, PUNCTUATION_KEY,
    KanaInputModel, flick_hint, transform_last_kana,
)


class ModifierTests(unittest.TestCase):
    def modify(self, text, gesture="center"):
        model = KanaInputModel(text=text)
        result = model.special_input(MODIFIER_KEY, gesture)
        return model.text, result

    def test_small_and_large_round_trip(self):
        for large, small in zip("あいうえおつやゆよわ", "ぁぃぅぇぉっゃゅょゎ"):
            with self.subTest(large=large):
                self.assertEqual(self.modify(large, "right")[0], small)
                self.assertEqual(self.modify(small, "right")[0], large)
                self.assertEqual(self.modify(small, "down")[0], large)

    def test_click_prioritizes_small_tsuna(self):
        self.assertEqual(self.modify("つ"), ("っ", "っ"))
        self.assertEqual(self.modify("っ"), ("づ", "づ"))
        self.assertEqual(self.modify("づ"), ("つ", "つ"))
        self.assertEqual(self.modify("や"), ("ゃ", "ゃ"))

    def test_dakuten_click_cycle(self):
        self.assertEqual(self.modify("か"), ("が", "が"))
        self.assertEqual(self.modify("が"), ("か", "か"))
        self.assertEqual(self.modify("は"), ("ば", "ば"))
        self.assertEqual(self.modify("ば"), ("ぱ", "ぱ"))
        self.assertEqual(self.modify("ぱ"), ("は", "は"))

    def test_explicit_dakuten_and_handakuten(self):
        for a, b in [("か", "が"), ("し", "じ"), ("つ", "づ"), ("ひ", "び"), ("う", "ゔ")]:
            with self.subTest(a=a):
                self.assertEqual(self.modify(a, "left")[0], b)
                self.assertEqual(self.modify(b, "left")[0], a)
        self.assertEqual(self.modify("は", "up")[0], "ぱ")
        self.assertEqual(self.modify("ば", "up")[0], "ぱ")
        self.assertEqual(self.modify("ぱ", "up")[0], "は")
        self.assertEqual(self.modify("ぱ", "down")[0], "は")

    def test_does_not_add_stray_marks_to_empty_or_non_kana(self):
        for value in ("", "abc", "あ、", "！", "漢"):
            for direction in DIRECTIONS:
                self.assertEqual(self.modify(value, direction), (value, None))

    def test_only_final_character_is_modified(self):
        self.assertEqual(self.modify("こんにちはは"), ("こんにちはば", "ば"))
        self.assertEqual(self.modify("あっ", "down"), ("あつ", "つ"))

    def test_explicit_unsupported_is_not_used_as_a_character(self):
        self.assertEqual(self.modify("さ", "up"), ("さ", None))
        with self.assertRaises(ValueError):
            transform_last_kana("あ", "diagonal")


class PunctuationTests(unittest.TestCase):
    def test_all_five_flick_directions(self):
        expected = ("、", "。", "？", "！", "…")
        m = KanaInputModel()
        self.assertEqual([m.special_input(PUNCTUATION_KEY, d) for d in DIRECTIONS], list(expected))
        self.assertEqual(m.text, "".join(expected))

    def test_guide_matches_direct_actions(self):
        for direction, result in zip(DIRECTIONS, ("、", "。", "？", "！", "…")):
            self.assertEqual(flick_hint(PUNCTUATION_KEY, direction), result)
        for label in ("変", "゛", "゜", "小", "大"):
            self.assertIn(label, [flick_hint(MODIFIER_KEY, d) for d in DIRECTIONS])
        self.assertIsNone(flick_hint("や", "left"))

    def test_layout_has_correct_special_keys(self):
        self.assertEqual(KEY_LAYOUT[3], (MODIFIER_KEY, "わ", PUNCTUATION_KEY))
        self.assertEqual(len(KEY_LAYOUT), 4)
        self.assertTrue(all(len(row) == 3 for row in KEY_LAYOUT))


if __name__ == "__main__":
    unittest.main()
