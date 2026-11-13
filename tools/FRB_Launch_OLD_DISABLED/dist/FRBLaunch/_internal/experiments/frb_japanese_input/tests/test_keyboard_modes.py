"""Four-mode keyboard contracts, independent of Qt/Windows."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from keyboard_modes import (MODES, MODE_COLUMNS, MODE_LABELS,
    layout_for, validate_layout, ime_key_for, request_ime_mode)


class FakeSender:
    def __init__(self):
        self.calls = []
    def send_tokens(self, tokens):
        self.calls.append(list(tokens))


class TestKeyboardModes(unittest.TestCase):
    def test_all_four_modes(self):
        self.assertEqual(MODES, ('kana','latin','symbols','numeric'))
        self.assertEqual(len(MODE_LABELS), 4)

    def test_ime_key_is_explicit_on_off(self):
        self.assertEqual(ime_key_for('kana'), 'IME_ON')
        for m in ('latin','symbols','numeric'):
            with self.subTest(mode=m):
                self.assertEqual(ime_key_for(m), 'IME_OFF')
        with self.assertRaises(ValueError):
            ime_key_for('unknown')

    def test_ime_mode_sent_to_focused_editor_only(self):
        sender = FakeSender()
        request_ime_mode('kana', sender, lambda:True)
        request_ime_mode('latin',sender,lambda:True)
        self.assertEqual(sender.calls,[['IME_ON'],['IME_OFF']])
        with self.assertRaises(RuntimeError):
            request_ime_mode('numeric',sender,lambda:False)
        self.assertEqual(len(sender.calls),2)

    def test_layouts_cover_no_overlapping_grid_cells(self):
        for mode in MODE_COLUMNS:
            with self.subTest(mode=mode):
                self.assertTrue(validate_layout(mode))
                keys=layout_for(mode)
                self.assertEqual(len(set((k.row,k.col) for k in keys)), len(keys))
                self.assertEqual(max(k.row for k in keys),3)
                self.assertLessEqual(max(k.col+k.span for k in keys),MODE_COLUMNS[mode])

    def test_latin_qwerty_plus_shift_and_delete(self):
        keys=layout_for('latin')
        line0=''.join(k.label for k in keys if k.row==0)
        self.assertEqual(line0,'qwertyuiop')
        self.assertEqual(''.join(k.label for k in keys if k.row==1),'asdfghjkl')
        self.assertTrue(any(k.action=='shift' for k in keys))
        self.assertTrue(any(k.action=='backspace' for k in keys))
        self.assertTrue(any(k.text==' ' and k.span>=5 for k in keys))

    def test_symbol_mode_includes_digit_row_and_punctuation(self):
        keys=layout_for('symbols')
        self.assertEqual(''.join(k.text for k in keys if k.row==0),'1234567890')
        chars={k.text for k in keys if k.text}
        for symbol in ('@','#','¥','%','&','/','+','(',')','!','?','…','.'):
            # Full-width punctuation is normalized on editor insertion.
            self.assertIn(symbol, chars)

    def test_numeric_telephone_grid(self):
        keys=layout_for('numeric')
        for row, chars in enumerate(('123','456','789')):
            for c, ch in enumerate(chars):
                self.assertTrue(any(k.row==row and k.col==c+1 and k.text==ch for k in keys))
        self.assertTrue(any(k.text=='0' and k.row==3 for k in keys))
        self.assertTrue(any(k.action=='backspace' for k in keys))

    def test_no_unassigned_text_in_mode_actions(self):
        for mode in MODE_COLUMNS:
            for k in layout_for(mode):
                with self.subTest(mode=mode,label=k.label):
                    self.assertIn(k.action,('spacer','insert','shift','backspace','enter'))
                    if k.action=='insert':
                        self.assertTrue(k.text)

    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError):
            layout_for('kana')  # kana uses the existing flick dictionary

    def test_sendinput_virtual_key_tokens_are_present(self):
        source=(Path(__file__).resolve().parent.parent / 'ime_bridge.py').read_text(encoding='utf8')
        self.assertIn("'IME_ON': 0x16",source)
        self.assertIn("'IME_OFF': 0x1A",source)


if __name__=='__main__':
    unittest.main()
