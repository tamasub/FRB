"""Static wiring checks: runnable even without PySide6/Windows."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'src' / 'app.py').read_text(encoding='utf-8')


def test_browser_buttons_wired_without_stealing_keyboard_focus():
    for button, handler in (
        ('nav_back_button', 'navigate_back'),
        ('nav_home_button', 'navigate_home')):
        assert f'self.{button}.clicked.connect(self.{handler})' in SOURCE
    assert "button.setFocusPolicy(Qt.FocusPolicy.NoFocus)" in SOURCE
    assert 'nav_forward_button' not in SOURCE
    assert 'navForwardButton' not in SOURCE
    assert 'def navigate_forward(self):' not in SOURCE
    assert "search_row.addWidget(self.nav_toolbar)" in SOURCE
    assert "search_row.addWidget(self.search, 1)" in SOURCE


def test_query_history_coalesced_and_keyboard_tabs_left_right_untouched():
    assert 'self._nav_search_timer.setInterval(600)' in SOURCE
    assert 'self._nav_search_timer.start()' in SOURCE
    assert 'self._nav_search_timer.timeout.connect(self._nav_flush_search)' in SOURCE
    assert 'if key in (Qt.Key.Key_Left,Qt.Key.Key_Right):' in SOURCE
    assert 'self.show_root_left_feedback()' in SOURCE


def test_history_reset_and_navigation_transition_hooks_present():
    assert 'self._nav_reset()' in SOURCE
    assert 'def _nav_restore(self, state):' in SOURCE
    assert 'def navigate_home(self):' in SOURCE
    assert 'self._nav_before_change()' in SOURCE
    assert 'self._nav_after_change()' in SOURCE
    assert 'self.nav_toolbar.setStyleSheet' in SOURCE
