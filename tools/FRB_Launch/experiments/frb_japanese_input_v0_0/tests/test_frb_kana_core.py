"""独立v0.0モデルの動作検証。PySide6不要。"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from frb_kana_core import (
    DIRECTIONS,
    KANA_ROWS,
    DRAG_THRESHOLD_PX,
    KanaInputModel,
    WheelStepper,
    classify_flick,
    get_kana,
    row_after_wheel,
)


class KanaMappingTests(unittest.TestCase):
    def test_all_rows_have_five_slots(self):
        self.assertEqual(len(KANA_ROWS), 10)
        self.assertEqual(len(DIRECTIONS), 5)
        for title, characters in KANA_ROWS:
            self.assertEqual(len(characters), 5, title)
            self.assertEqual(characters[0], title)

    def test_flick_is_ordinary_five_vowel_order(self):
        self.assertEqual([get_kana(1, d) for d in DIRECTIONS], list('かきくけこ'))
        self.assertEqual([get_kana(3, d) for d in DIRECTIONS], list('たちつてと'))

    def test_missing_ya_slots_never_make_up_characters(self):
        self.assertIsNone(get_kana(7, 'left'))
        self.assertIsNone(get_kana(7, 'right'))
        self.assertEqual(get_kana(7, 'up'), 'ゆ')
        self.assertEqual(get_kana(7, 'down'), 'よ')

    def test_wa_group(self):
        self.assertEqual([get_kana(9, d) for d in DIRECTIONS], ['わ', 'を', 'ん', 'ー', None])

    def test_unknown_direction(self):
        with self.assertRaises(ValueError):
            get_kana(0, 'diagonal')

    def test_unknown_row(self):
        with self.assertRaises(IndexError):
            get_kana(10, 'center')


class GestureTests(unittest.TestCase):
    def test_click_and_small_jitter(self):
        self.assertEqual(classify_flick(0, 0), 'center')
        self.assertEqual(classify_flick(17, 2), 'center')
        self.assertEqual(classify_flick(1, -17), 'center')

    def test_cardinal_directions(self):
        self.assertEqual(classify_flick(-18, 0), 'left')
        self.assertEqual(classify_flick(18, 0), 'right')
        self.assertEqual(classify_flick(0, -18), 'up')
        self.assertEqual(classify_flick(0, 18), 'down')

    def test_diagonals_cancel(self):
        self.assertIsNone(classify_flick(30, 30))
        self.assertIsNone(classify_flick(-20, 21))

    def test_direction_from_start_to_release(self):
        self.assertEqual(classify_flick(55, 5), 'right')
        self.assertEqual(classify_flick(5, -48), 'up')
        self.assertEqual(DRAG_THRESHOLD_PX, 18)


class WheelTests(unittest.TestCase):
    def test_rows_wrap(self):
        self.assertEqual(row_after_wheel(0, -1), 1)
        self.assertEqual(row_after_wheel(0, 1), 9)
        self.assertEqual(row_after_wheel(9, -1), 0)

    def test_half_step_accumulates(self):
        w = WheelStepper()
        self.assertEqual(w.feed(angle=-60), 0)
        self.assertEqual(w.feed(angle=-60), -1)
        self.assertEqual(w.feed(angle=120), 1)

    def test_pixel_accumulates(self):
        w = WheelStepper()
        self.assertEqual(w.feed(pixel=12), 0)
        self.assertEqual(w.feed(pixel=24), 1)
        self.assertEqual(w.feed(pixel=-36), -1)

    def test_burst_is_limited(self):
        w = WheelStepper()
        self.assertEqual(w.feed(angle=-120*20), -5)


class EditingTests(unittest.TestCase):
    def test_input_sequence_and_backspace(self):
        m = KanaInputModel()
        self.assertEqual(m.input('center'), 'あ')
        m.scroll(-1)
        self.assertEqual(m.input('left'), 'き')
        m.scroll(-1)
        self.assertEqual(m.input('up'), 'す')
        self.assertEqual(m.text, 'あきす')
        m.backspace()
        self.assertEqual(m.text, 'あき')
        m.clear()
        self.assertEqual(m.text, '')

    def test_missing_slot_makes_no_change(self):
        m = KanaInputModel()
        m.select(7)
        self.assertIsNone(m.input('left'))
        self.assertEqual(m.text, '')


if __name__ == '__main__':
    unittest.main()
