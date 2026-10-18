"""Keyboard focus cue for the modern FRB Launch Page tabs.

Qt stylesheets can style :selected tabs, but they do not reliably draw a
per-tab keyboard-focus indicator on all Windows Qt styles.  Keep the normal
QTabBar selection/navigation, then paint a thin inner outline only when the
bar actually owns focus.  The outline is *not* the selected-page marker.
"""

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QTabBar


class FocusPageTabBar(QTabBar):
    """A normal QTabBar with a visible inner outline on its focused tab."""

    def set_light_theme(self, light):
        """Make keyboard focus visible over either Page-tab palette."""
        self._light_theme = bool(light)
        self.update()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        index = self.currentIndex()
        if not self.hasFocus() or index < 0:
            return
        tab_rect = self.tabRect(index)
        if tab_rect.isEmpty():
            return

        # Draw *inside* the styled tab: neither its rounded border nor the
        # blue selection underline should move when keyboard focus changes.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(QPen(QColor('#82958c' if getattr(self, '_light_theme', False) else '#d2e6ff'), 1.8))
        # QSS gives each tab a 5px right margin to separate Page buttons.
        # QTabBar.tabRect() includes that reserved gap, so drawing directly
        # against its right edge makes the focus outline stick out past the
        # *visible button*.  Remove the gap first, then inset equally from
        # the actual button's left/right sides.
        button_rect = QRectF(tab_rect).adjusted(0, 0, -5.0, 0)
        inner = button_rect.adjusted(4.0, 4.0, -4.0, -5.0)
        if inner.width() > 0 and inner.height() > 0:
            painter.drawRoundedRect(inner, 4, 4)
        painter.end()
