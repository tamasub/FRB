"""Keyboard focus cue for the modern FRB Launch Page tabs.

Qt stylesheets can style :selected tabs, but they do not reliably draw a
per-tab keyboard-focus indicator on all Windows Qt styles.  Keep the normal
QTabBar selection/navigation, then paint a thin inner outline only when the
bar actually owns focus.  The outline is *not* the selected-page marker.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QTabBar


class FocusPageTabBar(QTabBar):
    """A normal QTabBar with a visible inner outline on its focused tab."""

    def set_light_theme(self, light):
        """Make keyboard focus visible over either Page-tab palette."""
        self._light_theme = bool(light)
        self.update()

    def mousePressEvent(self, event):
        """A left click on unused Page-tab space focuses the first tab.

        QTabBar is expanded to fill the header row; QTabBar's built-in
        mouse handler does not select a tab when tabAt() returns -1.
        Leave clicks on real tabs (and right/middle clicks) to Qt.
        """
        if (event.button() == Qt.MouseButton.LeftButton
                and self.count() > 0
                and self.tabAt(event.position().toPoint()) == -1):
            self.setCurrentIndex(0)
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            event.accept()
            return
        super().mousePressEvent(event)

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
        # Slim the dark keyboard-focus stroke; keep the original light theme.
        focus_width = 1.8 if getattr(self, '_light_theme', False) else 0.75
        painter.setPen(QPen(QColor('#82958c' if getattr(self, '_light_theme', False) else '#d2e6ff'), focus_width))
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
