"""Regression checks for the v0.9 compact keyboard/bottom editor layout."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mini_config import DEFAULT_SIZE_INDEX, SIZE_PRESETS, compact_client_height


class BottomImeEditorTests(unittest.TestCase):
    def test_remote_size_is_compact_again(self):
        spec = SIZE_PRESETS[DEFAULT_SIZE_INDEX]
        self.assertEqual(spec.outer_width, 200)
        self.assertEqual(spec.outer_height, 272)
        self.assertEqual(compact_client_height(spec, 27), 245)

    def test_presets_do_not_include_candidate_blank_space(self):
        for spec in SIZE_PRESETS:
            with self.subTest(size=spec.name):
                self.assertEqual(compact_client_height(spec, 27), max(195, spec.outer_height - 27))

    def test_editor_is_last_and_keyboard_is_unchanged(self):
        source = (ROOT / 'frb_japanese_input.py').read_text(encoding='utf-8')
        start = source.index('    def _build_ui(self):')
        end = source.index('    def _change_size(self,', start)
        ui = source[start:end]
        self.assertLess(ui.index('root.addWidget(keyboard)'), ui.index('root.addLayout(actions)'))
        self.assertLess(ui.index('root.addLayout(actions)'), ui.index('root.addLayout(footer)'))
        self.assertLess(ui.index('root.addLayout(footer)'), ui.index('root.addWidget(self.output)'))
        self.assertNotIn('candidateGap', ui)
        self.assertNotIn('gap_button', ui)
        self.assertIn('QLineEdit', source)


if __name__ == '__main__':
    unittest.main()
