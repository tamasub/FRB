"""Regression tests independent of PySide6 installation."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'src' / 'web_console_policy.py'
spec = importlib.util.spec_from_file_location('web_console_policy_for_test', POLICY)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class WebConsoleNoiseTests(unittest.TestCase):
    def test_repeated_google_font_error_suppressed(self):
        self.assertTrue(policy.should_suppress_console_message(
            'Failed to decode downloaded font: https://fonts.gstatic.com/l/font?kit=abc'))

    def test_ots_error_suppressed(self):
        self.assertTrue(policy.should_suppress_console_message(
            'OTS parsing error: Unable to instantiate font face from font data.'))

    def test_webgpu_error_suppressed(self):
        self.assertTrue(policy.should_suppress_console_message(
            'Failed to create WebGPU Context Provider'))

    def test_other_font_error_preserved(self):
        self.assertFalse(policy.should_suppress_console_message(
            'Failed to decode downloaded font: https://example.com/asset.ttf'))

    def test_other_console_error_preserved(self):
        self.assertFalse(policy.should_suppress_console_message(
            'Uncaught TypeError: Cannot read properties of undefined'))

    def test_similarly_named_messages_preserved(self):
        self.assertFalse(policy.should_suppress_console_message(
            'Warning: OTS parsing error elsewhere'))

    def test_switch_to_diagnostics(self):
        initial = policy.SUPPRESS_KNOWN_WEB_CONSOLE_NOISE
        try:
            policy.SUPPRESS_KNOWN_WEB_CONSOLE_NOISE = False
            self.assertFalse(policy.should_suppress_console_message(
                'Failed to create WebGPU Context Provider'))
        finally:
            policy.SUPPRESS_KNOWN_WEB_CONSOLE_NOISE = initial

    def test_correct_web_page_integration(self):
        source = (ROOT / 'src' / 'launch_web_view.py').read_text(encoding='utf-8')
        self.assertIn('class QWebEnginePage(_QtWebEnginePage):', source)
        self.assertIn('view.setPage(QWebEnginePage(self.profile, view))', source)
        self.assertIn('if should_suppress_console_message(message):', source)
        self.assertIn('super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)', source)

    def test_cache_reset_renames_only_local_launch_cache(self):
        source = (ROOT / 'reset_frb_web_cache.bat').read_text(encoding='ascii')
        self.assertIn(r'FRBLaunch\web_profile\cache', source)
        self.assertIn('Rename-Item',source)
        self.assertNotIn('Remove-Item',source)
        self.assertNotIn('rmdir',source.lower())


if __name__ == '__main__':
    unittest.main()
