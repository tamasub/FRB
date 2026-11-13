"""Move frameless windows by dragging existing, noninteractive header surfaces.

Install only on decorative widgets or a header background. QLineEdit,
QPushButton, and other active controls deliberately receive no filter, so
selection, editing, and clicks retain their existing behavior.
"""

from PySide6.QtCore import QObject, QEvent, Qt


class PassiveHeaderDrag(QObject):
    """Move by a passive header; toggle maximize on workspace blank-band double-click."""

    _WORKSPACE_DRAG_HANDLE = 'expandedWorkspaceDragHandle'
    _DRAG_THRESHOLD = 5

    def __init__(self, window, on_header_press=None):
        super().__init__(window)
        self.window = window
        self._on_header_press = on_header_press
        self._origin_pointer = None
        self._origin_window = None
        self._active = False
        self._pending_workspace_drag = False

    def _reset_drag(self):
        self._active = False
        self._pending_workspace_drag = False
        self._origin_pointer = None
        self._origin_window = None

    def eventFilter(self, widget, event):
        kind = event.type()
        is_workspace_blank = (getattr(widget, 'objectName', lambda: '')()
                              == self._WORKSPACE_DRAG_HANDLE)
        # This is an Explorer/Chrome-style blank tab-strip surface. Never
        # interpret a double-click on an actual Files/Browser/Page button.
        if (is_workspace_blank
                and kind == getattr(QEvent.Type, 'MouseButtonDblClick', None)
                and event.button() == Qt.MouseButton.LeftButton):
            self._reset_drag()
            self.window.toggle_maximize_restore()
            event.accept()
            return True

        if kind == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if self._on_header_press is not None:
                self._on_header_press()
            self._reset_drag()
            self._origin_pointer = event.globalPosition().toPoint()
            self._origin_window = self.window.pos()
            if is_workspace_blank:
                # Do not call startSystemMove on a simple press: on Windows
                # that can consume the second click before Qt recognizes a
                # MouseButtonDblClick. Start moving only after real motion.
                self._pending_workspace_drag = True
            else:
                handle = self.window.windowHandle()
                if handle and handle.startSystemMove():
                    self._origin_pointer = None
                    self._origin_window = None
                else:
                    self._active = True
            event.accept()
            return True

        if self._pending_workspace_drag and kind == QEvent.Type.MouseMove:
            if not event.buttons() & Qt.MouseButton.LeftButton:
                self._reset_drag()
                return False
            point = event.globalPosition().toPoint()
            delta = point - self._origin_pointer
            if abs(delta.x()) + abs(delta.y()) < self._DRAG_THRESHOLD:
                event.accept()
                return True
            self._pending_workspace_drag = False
            handle = self.window.windowHandle()
            if handle and handle.startSystemMove():
                self._origin_pointer = None
                self._origin_window = None
            else:
                self._active = True
                self.window.move(self._origin_window + delta)
            event.accept()
            return True

        if self._active and kind == QEvent.Type.MouseMove:
            if self._origin_pointer is not None and event.buttons() & Qt.MouseButton.LeftButton:
                self.window.move(self._origin_window + event.globalPosition().toPoint() - self._origin_pointer)
            event.accept()
            return True

        if (self._active or self._pending_workspace_drag) and kind == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            self._reset_drag()
            event.accept()
            return True

        return False
