"""Taskbar-safe cascade popup geometry. Does not require a GUI session."""
import unittest

from menu_viewport import place_popup, MENU_SCREEN_MARGIN


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


if __name__ == '__main__':
    unittest.main()
