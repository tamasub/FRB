"""v0.5 local preedit: never auto-commit, all center taps cycle without timeouts."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from frb_kana_core import KanaInputModel, MODIFIER_KEY, PUNCTUATION_KEY


class CompositionTests(unittest.TestCase):
    def test_aa_cycles_without_appending_or_time_limit(self):
        m = KanaInputModel()
        self.assertEqual(m.type_kana(0, 'center', now_ms=0), 'あ')
        self.assertEqual(m.type_kana(0, 'center', now_ms=100_000), 'い')
        self.assertEqual(m.text, 'い')
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.preedit_text, 'い')

    def test_five_kana_and_wrap_with_slow_clicks(self):
        m = KanaInputModel()
        for t, expected in enumerate('あいうえおあ'):
            self.assertEqual(m.type_kana(0, 'center', now_ms=t*100_000), expected)
            self.assertEqual(m.text, expected)
        self.assertTrue(m.has_preedit)

    def test_different_key_keeps_entire_text_unconfirmed(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.type_kana(1, 'center')
        self.assertEqual(m.text, 'あか')
        self.assertEqual(m.preedit_text, 'あか')
        m.type_kana(1, 'center')
        self.assertEqual(m.preedit_text, 'あき')
        self.assertEqual(m.committed_text, '')

    def test_same_key_after_different_key_appends(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.type_kana(1, 'center')
        m.type_kana(0, 'center')
        self.assertEqual(m.text, 'あかあ')

    def test_ya_wa_skip_blank_slots(self):
        m = KanaInputModel()
        for expected in 'やゆよや':
            self.assertEqual(m.type_kana(7, 'center'), expected)
        m.type_kana(8, 'center')
        for expected in 'わをんーわ':
            self.assertEqual(m.type_kana(9, 'center'), expected)

    def test_flick_after_center_appends_but_never_commits(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.type_kana(0, 'left')
        self.assertEqual(m.text, 'あい')
        self.assertTrue(m.has_preedit)
        m.type_kana(0, 'center')
        self.assertEqual(m.text, 'あいあ')

    def test_time_expiry_is_inert(self):
        m = KanaInputModel()
        m.type_kana(0, 'center', now_ms=0)
        self.assertFalse(m.expire_preedit(now_ms=50_000_000))
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.type_kana(0, 'center', now_ms=50_000_001), 'い')

    def test_punctuation_center_repeats_as_single_preedit_character(self):
        m = KanaInputModel()
        for value in ('、', '。', '？', '！', '…', '、'):
            self.assertEqual(m.special_input(PUNCTUATION_KEY, 'center'), value)
            self.assertEqual(m.text, value)
            self.assertEqual(m.preedit_char, value)
            self.assertTrue(m.has_preedit)

    def test_punctuation_after_kana_and_modifier(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.special_input(PUNCTUATION_KEY, 'center')
        m.special_input(PUNCTUATION_KEY, 'center')
        self.assertEqual(m.text, 'あ。')
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.preedit_text, 'あ。')

    def test_punctuation_flick_is_direct_preedit_append(self):
        m = KanaInputModel()
        self.assertEqual(m.special_input(PUNCTUATION_KEY, 'left'), '。')
        self.assertEqual(m.text, '。')
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.special_input(PUNCTUATION_KEY, 'center'), '、')
        self.assertEqual(m.text, '。、')

    def test_ta_dakuten_round_trip_stays_unconfirmed(self):
        m = KanaInputModel()
        m.type_kana(3, 'center')
        self.assertEqual(m.special_input(MODIFIER_KEY, 'center'), 'だ')
        self.assertEqual(m.text, 'だ')
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.special_input(MODIFIER_KEY, 'center'), 'た')
        self.assertEqual(m.text, 'た')
        self.assertTrue(m.has_preedit)

    def test_ha_variants_stay_preedit(self):
        m = KanaInputModel()
        m.type_kana(5, 'center')
        for char in ['ば', 'ぱ', 'は']:
            self.assertEqual(m.special_input(MODIFIER_KEY, 'center'), char)
            self.assertEqual(m.preedit_char, char)

    def test_small_letter_after_flick_stays_unconfirmed(self):
        m = KanaInputModel()
        m.type_kana(3, 'up')
        self.assertEqual(m.special_input(MODIFIER_KEY, 'right'), 'っ')
        self.assertTrue(m.has_preedit)
        self.assertEqual(m.text, 'っ')

    def test_enter_commit_does_not_append_or_delete_text(self):
        m = KanaInputModel()
        m.type_kana(3, 'center')
        m.special_input(MODIFIER_KEY, 'center')
        m.special_input(PUNCTUATION_KEY, 'center')
        m.special_input(PUNCTUATION_KEY, 'center')
        self.assertEqual(m.text, 'だ。')
        self.assertEqual(m.committed_text, '')
        self.assertTrue(m.commit())
        self.assertEqual(m.committed_text, 'だ。')
        self.assertFalse(m.has_preedit)
        self.assertFalse(m.commit())
        self.assertIsNone(m.special_input(MODIFIER_KEY, 'center'))
        self.assertEqual(m.text, 'だ。')

    def test_after_enter_new_input_composes_separately(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.commit()
        m.type_kana(0, 'center')
        self.assertEqual(m.committed_text, 'あ')
        self.assertEqual(m.preedit_text, 'あ')
        m.type_kana(0, 'center')
        self.assertEqual(m.text, 'あい')
        self.assertEqual(m.preedit_text, 'い')

    def test_backspace_and_clear_preserve_consistent_boundaries(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        m.commit()
        m.special_input(PUNCTUATION_KEY, 'center')
        m.backspace()
        self.assertEqual(m.text, 'あ')
        self.assertFalse(m.has_preedit)
        m.backspace()
        self.assertEqual(m.text, '')
        self.assertFalse(m.has_preedit)
        m.type_kana(0, 'center')
        m.clear()
        self.assertEqual(m.committed_length, 0)
        self.assertEqual(m.text, '')

    def test_invalid_direction_preserves_state(self):
        m = KanaInputModel()
        m.type_kana(0, 'center')
        self.assertIsNone(m.type_kana(7, 'left'))
        self.assertEqual(m.preedit_text, 'あ')
        with self.assertRaises(IndexError):
            m.type_kana(-1, 'center')
        with self.assertRaises(ValueError):
            m.type_kana(0, 'diagonal')

    def test_legacy_input_remains_immediate(self):
        m = KanaInputModel()
        self.assertEqual(m.input('center'), 'あ')
        self.assertEqual(m.input('center'), 'あ')
        self.assertEqual(m.text, 'ああ')
        self.assertFalse(m.has_preedit)


if __name__ == '__main__':
    unittest.main()
