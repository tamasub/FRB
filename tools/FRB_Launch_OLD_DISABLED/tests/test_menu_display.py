"""Cascade text-formatting rules do not require GUI/PySide6 to test."""
import unittest
from menu_display import cascade_label


def measure(value):
    return len(value) * 8  # fixed-width fake font, for deterministic tests


def elide(value, max_width):
    if measure(value) <= max_width:
        return value
    return value[:max(0, max_width // 8 - 1)] + '…'


class CascadeDisplayTests(unittest.TestCase):
    def test_regular_description_truncates_with_tooltip(self):
        description = 'https://example.com/' + 'very-long-address/' * 40
        row = {'title': 'ZIPを作る', 'description': description, 'item_kind': 'command'}
        visible, tip = cascade_label(row, 'category', 320, elide, measure)
        self.assertTrue(visible.startswith('ZIPを作る'))
        self.assertTrue(visible.endswith('…'))
        self.assertEqual(tip, 'ZIPを作る\n' + description)
        self.assertLessEqual(measure(visible), 320)

    def test_bookmark_url_only_in_tooltip(self):
        row = {'title': 'FRB Studio', 'description': 'https://example.com/verylong',
               'item_kind': 'command', '_browser_bookmark': True}
        visible, tip = cascade_label(row, 'category', 320, elide, measure)
        self.assertEqual(visible, 'FRB Studio')
        self.assertNotIn('https:', visible)
        self.assertIn('https:', tip)

    def test_long_bookmark_title_is_clipped(self):
        row = {'title': '長い名前' * 100, 'item_kind': 'command', '_browser_bookmark': True}
        visible, tip = cascade_label(row, 'category', 320, elide, measure)
        self.assertTrue(visible.endswith('…'))
        self.assertEqual(tip, row['title'])
        self.assertLessEqual(measure(visible), 320)

    def test_folder_chevron_survives_elision(self):
        row = {'title': '資料保管' * 100, 'item_kind': 'category'}
        visible, tip = cascade_label(row, 'category', 320, elide, measure)
        self.assertTrue(visible.endswith('  ›'))
        self.assertIn('…', visible)
        self.assertEqual(tip, row['title'])
        self.assertLessEqual(measure(visible), 320)

    def test_filesystem_child_only_name(self):
        row = {'title': 'note.txt', 'description': r'C:\very\long\path\note.txt', 'item_kind': 'command'}
        visible, tip = cascade_label(row, 'directory', 320, elide, measure)
        self.assertEqual(visible, 'note.txt')
        self.assertIn('path', tip)

    def test_short_standard_item_keeps_existing_description(self):
        row = {'title': 'FRB ZIP作成', 'description': '日時付きZIP', 'item_kind': 'command'}
        visible, tip = cascade_label(row, 'category', 320, elide, measure)
        self.assertEqual(visible, 'FRB ZIP作成    日時付きZIP')
        self.assertEqual(tip, 'FRB ZIP作成\n日時付きZIP')


if __name__ == '__main__':
    unittest.main()
