"""Move frameless windows by dragging existing, noninteractive header surfaces.

Install only on decorative widgets or a header background.  QLineEdit,
QPushButton, and other active controls deliberately receive no filter, so
selection, editing, and clicks retain their existing behavior.
"""

from PySide6.QtCore import QObject, QEvent, Qt


class PassiveHeaderDrag(QObject):
    """Translate a left drag on the host's decorative header into window move."""

    def __init__(self, window, on_header_press=None):
        super().__init__(window)
        self.window = window
        self._on_header_press = on_header_press
        self._origin_pointer = None
        self._origin_window = None
        self._active = False

    def eventFilter(self, widget, event):
        kind = event.type()
        if kind == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            # The native API follows the cursor across widget boundaries and
            # behaves correctly under Windows display scaling.  Fall back to
            # manual moving when native system move is unavailable.
            if self._on_header_press is not None:
                self._on_header_press()
            self._active = False
            self._origin_pointer = event.globalPosition().toPoint()
            self._origin_window = self.window.pos()
            handle = self.window.windowHandle()
            if handle and handle.startSystemMove():
                # Native moving owns the interaction; some platforms consume
                # mouse release, so do not leave a fallback drag armed.
                self._origin_pointer = None
                self._origin_window = None
            else:
                self._active = True
            event.accept()
            return True

        if self._active and kind == QEvent.Type.MouseMove:
            if self._origin_pointer is not None and event.buttons() & Qt.MouseButton.LeftButton:
                self.window.move(self._origin_window + event.globalPosition().toPoint() - self._origin_pointer)
            event.accept()
            return True

        if self._active and kind == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            self._active = False
            self._origin_pointer = None
            self._origin_window = None
            event.accept()
            return True

        return False
