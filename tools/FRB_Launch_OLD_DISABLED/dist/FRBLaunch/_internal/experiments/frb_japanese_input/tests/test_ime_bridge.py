"""IME bridge tests are GUI/Windows-independent; fake keyboard target."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ime_bridge import (
    romaji_for, plan_preedit_transition, ExternalImeSession,
)
from frb_kana_core import KanaInputModel, MODIFIER_KEY, PUNCTUATION_KEY


class FakeKeyboard:
    def __init__(self):
        self.hwnd = 123
        self.ours = False
        self.calls = []

    def foreground_window(self):
        return self.hwnd

    def is_our_process(self, hwnd):
        return self.ours

    def send_tokens(self, keys):
        self.calls.append(list(keys))


class BridgeTests(unittest.TestCase):
    def test_romanization_for_all_flick_kana(self):
        from frb_kana_core import KANA_ROWS
        for _, chars in KANA_ROWS:
            for char in chars:
                if char:
                    self.assertTrue(romaji_for(char).isascii())

    def test_romanization_small_dakuten_and_kuten(self):
        expected = {'あ':'a','た':'ta','だ':'da','っ':'xtsu',
                    'ば':'ba','ぱ':'pa','ん':'nn','ー':'-',
                    '。':'.','、':',','！':'!','？':'?'}
        for kana, keys in expected.items():
            self.assertEqual(romaji_for(kana),keys)

    def test_unsupported_char_does_not_make_partial_plan(self):
        with self.assertRaises(ValueError):
            plan_preedit_transition('あか', 'あか…')

    def test_add_kana_into_existing_composition(self):
        self.assertEqual(plan_preedit_transition('た', 'たか'), list('ka'))

    def test_repeated_tap_changes_single_pending_char(self):
        self.assertEqual(plan_preedit_transition('あ', 'い'), ['BACKSPACE', 'i'])
        self.assertEqual(plan_preedit_transition('い', 'う'), ['BACKSPACE', 'u'])

    def test_dakuten_rewrites_last_not_whole_preedit(self):
        self.assertEqual(plan_preedit_transition('あた', 'あだ'),
                         ['BACKSPACE', 'd', 'a'])

    def test_punctuation_cycle(self):
        self.assertEqual(plan_preedit_transition('、', '。'), ['BACKSPACE', '.'])

    def test_backspace_and_clear(self):
        self.assertEqual(plan_preedit_transition('たか', 'た'), ['BACKSPACE'])
        self.assertEqual(plan_preedit_transition('たか', ''), ['BACKSPACE','BACKSPACE'])

    def test_session_keeps_target_until_commit(self):
        fake = FakeKeyboard()
        session = ExternalImeSession(fake)
        session.sync('た')
        self.assertEqual(fake.calls[0], list('ta'))
        self.assertEqual(session.target, 123)
        session.sync('だ')
        self.assertEqual(fake.calls[1], ['BACKSPACE', 'd', 'a'])
        session.commit()
        self.assertEqual(fake.calls[-1], ['ENTER'])
        self.assertIsNone(session.target)
        self.assertEqual(session.synced_preedit, '')

    def test_foreground_switch_fails_without_sending(self):
        fake = FakeKeyboard()
        session = ExternalImeSession(fake)
        session.sync('た')
        fake.hwnd = 333
        with self.assertRaisesRegex(RuntimeError, '送信先が変わりました'):
            session.sync('だ')
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(session.synced_preedit, 'た')

    def test_our_window_cannot_receive_external_input(self):
        fake = FakeKeyboard()
        fake.ours = True
        session = ExternalImeSession(fake)
        with self.assertRaisesRegex(RuntimeError, '送信先のエディタ'):
            session.sync('あ')
        self.assertFalse(fake.calls)

    def test_clear_before_typing_does_nothing(self):
        fake = FakeKeyboard()
        session = ExternalImeSession(fake)
        session.sync('')
        session.commit()
        self.assertFalse(fake.calls)

    def test_v05_model_works_with_external_plan(self):
        m = KanaInputModel()
        kb = FakeKeyboard()
        session = ExternalImeSession(kb)
        m.type_kana(3, 'center')
        session.sync(m.preedit_text)
        m.special_input(MODIFIER_KEY, 'center')
        session.sync(m.preedit_text)
        m.special_input(MODIFIER_KEY, 'center')
        session.sync(m.preedit_text)
        self.assertEqual(kb.calls, [list('ta'), ['BACKSPACE','d','a'], ['BACKSPACE','t','a']])
        session.commit()
        m.commit()
        self.assertFalse(m.has_preedit)
        m.special_input(PUNCTUATION_KEY,'center')
        session.sync(m.preedit_text)
        self.assertEqual(kb.calls[-1], [','])


if __name__ == '__main__':
    unittest.main()
