"""Tests for the v0.7 local editor IME session (without a GUI or Windows)."""
import unittest
from local_ime_bridge import LocalImeSession


class FakeSender:
    def __init__(self):
        self.events = []
    def send_tokens(self, tokens):
        self.events.append(list(tokens))


class TestLocalIme(unittest.TestCase):
    def setUp(self):
        self.sender = FakeSender()
        self.focus = [True]
        self.session = LocalImeSession(self.sender, lambda: self.focus[0])

    def test_local_first_character_romaji(self):
        self.session.sync('た')
        self.assertEqual(self.sender.events, [['t', 'a']])
        self.assertEqual(self.session.synced_preedit, 'た')

    def test_same_key_cycle_replaces_uncommitted_character(self):
        self.session.sync('た')
        self.session.sync('ち')
        self.assertEqual(self.sender.events[-1], ['BACKSPACE', 'c', 'h', 'i'])

    def test_dakuten_toggle(self):
        self.session.sync('た')
        self.session.sync('だ')
        self.session.sync('た')
        self.assertEqual(self.sender.events[1], ['BACKSPACE', 'd', 'a'])
        self.assertEqual(self.sender.events[2], ['BACKSPACE', 't', 'a'])

    def test_multi_character_append(self):
        self.session.sync('たま')
        self.session.sync('たまい')
        self.assertEqual(self.sender.events[-1], ['i'])

    def test_punctuation_cycle(self):
        self.session.sync('、')
        self.session.sync('。')
        self.assertEqual(self.sender.events[-1], ['BACKSPACE', '.'])

    def test_cannot_send_when_focus_lost(self):
        self.focus[0] = False
        with self.assertRaises(RuntimeError):
            self.session.sync('あ')
        self.assertEqual(self.sender.events, [])
        self.assertEqual(self.session.synced_preedit, '')

    def test_unsupported_character_is_atomic(self):
        self.session.sync('あ')
        with self.assertRaises(ValueError):
            self.session.sync('あ…')
        self.assertEqual(len(self.sender.events), 1)
        self.assertEqual(self.session.synced_preedit, 'あ')

    def test_enter_commits_and_new_word_starts(self):
        self.session.sync('か')
        self.session.commit()
        self.session.sync('な')
        self.assertEqual(self.sender.events, [['k','a'], ['ENTER'], ['n','a']])
        self.assertEqual(self.session.synced_preedit, 'な')

    def test_no_enter_if_nothing_pending(self):
        self.session.commit()
        self.assertEqual(self.sender.events, [])

    def test_clear_cancel(self):
        self.session.sync('あ')
        self.session.cancel()
        self.assertEqual(self.sender.events[-1], ['ESCAPE'])
        self.assertEqual(self.session.synced_preedit, '')

    def test_direct_candidate_commit_resets_tracking(self):
        self.session.sync('たまい')
        self.session.forget()
        self.session.sync('わ')
        self.assertEqual(self.sender.events[-1], ['w','a'])

    def test_backspace_committed(self):
        self.session.backspace_committed()
        self.assertEqual(self.sender.events, [['BACKSPACE']])


if __name__ == '__main__':
    unittest.main()
