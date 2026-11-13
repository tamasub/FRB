"""Taskbar-safe cascade popup geometry. Does not require a GUI session."""
import unittest

from menu_viewport import place_popup, main_cascade_anchor_x, MENU_SCREEN_MARGIN


class PopupPlacementTests(unittest.TestCase):
    def test_oversized_menu_ends_above_taskbar(self):
        # 1080px display, 40px Windows taskbar -> working area bottom=1040.
        result = place_popup(555, 330, 310, 1700, 0, 0, 1920, 1040)
        self.assertTrue(result.scroll)
        self.assertEqual(result.y + result.height, 1040 - MENU_SCREEN_MARGIN)
        self.assertEqual(result.height, 1040 - 2 * MENU_SCREEN_MARGIN)

    def test_normal_menu_keeps_its_anchor(self):
        result = place_popup(300, 340, 220, 180, 0, 0, 1920, 1040)
        self.assertEqual((result.x, result.y, result.height), (300, 340, 180))
        self.assertFalse(result.scroll)

    def test_popup_above_taskbar_when_anchor_is_low(self):
        result = place_popup(300, 1000, 220, 260, 0, 0, 1920, 1040)
        self.assertEqual(result.y, 1040 - MENU_SCREEN_MARGIN - 260)
        self.assertFalse(result.scroll)

    def test_negative_monitor_coordinates(self):
        result = place_popup(-1900, -200, 350, 1500, -1920, -120, 0, 940)
        self.assertGreaterEqual(result.x, -1920 + MENU_SCREEN_MARGIN)
        self.assertGreaterEqual(result.y, -120 + MENU_SCREEN_MARGIN)
        self.assertLessEqual(result.y + result.height, 940 - MENU_SCREEN_MARGIN)
        self.assertTrue(result.scroll)

    def test_right_edge_clamped(self):
        result = place_popup(1900, 300, 320, 200, 0, 0, 1920, 1040)
        self.assertEqual(result.x, 1920 - MENU_SCREEN_MARGIN - 320)

    def test_short_monitor_height(self):
        result = place_popup(100, 100, 220, 400, 0, 0, 800, 300)
        self.assertTrue(result.scroll)
        self.assertEqual(result.y + result.height, 300 - MENU_SCREEN_MARGIN)


class MainCascadeAnchorTests(unittest.TestCase):
    def test_main_page_opens_at_second_column_start(self):
        self.assertEqual(main_cascade_anchor_x(680, 235, main_columns=True), 234)

    def test_resized_column_updates_anchor(self):
        self.assertEqual(main_cascade_anchor_x(680, 310, main_columns=True), 309)

    def test_non_main_mode_keeps_viewport_right_edge(self):
        self.assertEqual(main_cascade_anchor_x(680, 235, main_columns=False), 679)

    def test_unavailable_divider_falls_back_to_right_edge(self):
        for divider in (None, 0, -10, 680, 9999):
            with self.subTest(divider=divider):
                self.assertEqual(main_cascade_anchor_x(680, divider, main_columns=True), 679)

    def test_popup_screen_clamping_still_applies(self):
        anchor = main_cascade_anchor_x(680, 235, main_columns=True)
        result = place_popup(anchor, 220, 560, 230, 0, 0, 700, 500)
        self.assertLessEqual(result.x + 560, 700 - MENU_SCREEN_MARGIN)


if __name__ == '__main__':
    unittest.main()
