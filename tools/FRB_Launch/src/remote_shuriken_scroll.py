"""Experimental mouse-only Shuriken Scroll button for FRB Remote.

Starts live scrolling on a held vertical gesture and stops immediately on
release. A very fast flick sends one bounded impulse; plain click does nothing.
No QWheelEvent, fake keystroke, cursor warp or scroll-target focus transfer.
"""
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QApplication

from shuriken_scroll_model import (TICK_MS, pixels_per_tick, release_impulse)


class ShurikenScrollPad(QFrame):
    scroll_requested = Signal(int)  # Signed *pixel* change to the target scrollbar.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('remoteShurikenScrollPad')
        self.setFixedSize(68, 46)  # Exactly the compact ぐりぐり button size.
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip('手裏剣スクロール（試作）：押したまま上下へシュッ／離すと停止。Files List限定')
        self._pressed = False
        self._press_y = 0.0
        self._dy = 0.0
        self._ticks_emitted = 0
        self._timer = QTimer(self)
        self._timer.setInterval(TICK_MS)
        self._timer.timeout.connect(self._scroll_tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        caption = QLabel('手裏剣↕', self)
        caption.setObjectName('remoteShurikenScrollLabel')
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        glyph = QLabel('⇅', self)
        glyph.setObjectName('remoteShurikenScrollGlyph')
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(caption)
        layout.addWidget(glyph)

    def wheelEvent(self, event):
        # The new surface must not break ordinary Remote wheel navigation.
        pad = getattr(self.parentWidget(), 'pad', None)
        if pad is not None:
            pad.wheelEvent(event)
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        self._pressed = True
        self._press_y = event.position().y()
        self._dy = 0.0
        self._ticks_emitted = 0
        self._timer.start()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._pressed and (event.buttons() & Qt.MouseButton.LeftButton):
            # Local pointer coordinates are relative to the fixed widget even
            # after Qt's implicit grab carries the pointer outside its bounds.
            self._dy = event.position().y() - self._press_y
            event.accept()
            return
        event.ignore()

    def _scroll_tick(self):
        # Implicit mouse grab can be lost when another window interrupts a
        # drag. Never leave an orphan timer scrolling the file list forever.
        if not self._pressed or not (QApplication.mouseButtons() & Qt.MouseButton.LeftButton):
            self._stop()
            return
        pixels = pixels_per_tick(self._dy)
        if pixels:
            self._ticks_emitted += 1
            self.scroll_requested.emit(pixels)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        if self._pressed:
            dy = event.position().y() - self._press_y
            pixels = release_impulse(dy, self._ticks_emitted)
            self._stop()
            if pixels:
                self.scroll_requested.emit(pixels)
        event.accept()

    def _stop(self):
        self._timer.stop()
        self._pressed = False
        self._dy = 0.0
        self._ticks_emitted = 0

    def hideEvent(self, event):
        self._stop()
        super().hideEvent(event)
