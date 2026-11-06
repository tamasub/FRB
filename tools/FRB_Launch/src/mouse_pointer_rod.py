"""Mouse Pointer Rod v0.9: an unobtrusive, hover-activated aiming overlay.

Only wheel gestures over the blue surface change length (15px/notch, or
60px/notch while the left button is held there). The embedded ぐりぐり retains
its native List/Exp/Browser wheel, click, right-click and hold commands.
The rod fades into view after an intentional 250ms hover, and disappears
when leaving the blue surface or entering the native ぐりぐり. No system cursor
is moved or clicked.
"""

from PySide6.QtCore import Qt, QEvent, QTimer, QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QFrame, QWidget

from mouse_pointer_rod_model import (
    DEFAULT_DIRECTION, DEFAULT_LENGTH, NORMAL_WHEEL_STEP_PX,
    FAST_WHEEL_STEP_PX, direction_from_pointer, length_after_wheel,
    rod_endpoint,
)


class MousePointerRodOverlay(QWidget):
    """Desktop-sized drawing layer; never receive mouse/focus/keyboard input."""

    def __init__(self, parent):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus |
                 Qt.WindowType.WindowTransparentForInput)
        super().__init__(parent, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._origin = None
        self._tip = None
        self._emphasized = False

    def set_emphasis(self, emphasized):
        """Highlight only the line briefly after an intentional wheel gesture."""
        emphasized = bool(emphasized)
        if self._emphasized != emphasized:
            self._emphasized = emphasized
            bounds = self._paint_bounds()
            if bounds is not None:
                self.update(bounds)

    def _paint_bounds(self):
        if self._origin is None or self._tip is None:
            return None
        offset = QPointF(self.geometry().topLeft())
        a, b = self._origin - offset, self._tip - offset
        margin = 14.0
        return QRectF(min(a.x(), b.x()) - margin,
                      min(a.y(), b.y()) - margin,
                      abs(a.x() - b.x()) + 2 * margin,
                      abs(a.y() - b.y()) + 2 * margin).toAlignedRect()

    def show_rod(self, origin, tip):
        old_bounds = self._paint_bounds()
        self._origin = QPointF(*origin)
        self._tip = QPointF(*tip)
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        # Qt's virtual geometry can start at negative X on secondary displays.
        geometry = screen.virtualGeometry()
        if self.geometry() != geometry:
            self.setGeometry(geometry)
            old_bounds = None  # The desktop coordinate system changed.
        if not self.isVisible():
            self.show()
        else:
            new_bounds = self._paint_bounds()
            # Repaint only the previous/new line. Full desktop repaints on
            # every pixel of mouse travel make aiming noticeably sluggish.
            if old_bounds is None:
                self.update()
            elif new_bounds is not None:
                self.update(old_bounds.united(new_bounds))

    def paintEvent(self, event):
        if self._origin is None or self._tip is None:
            return
        painter = QPainter(self)
        try:
            # Clear the previous thin rod in the dirty region before drawing
            # the new position; Windows layered windows retain old pixels.
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.fillRect(event.rect(), Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            offset = self.geometry().topLeft()
            start = self._origin - QPointF(offset)
            tip = self._tip - QPointF(offset)
            # Keep the 25-30% guide unobtrusive; temporarily accent it after
            # a wheel adjustment. The tip remains more visible than the line.
            line_alpha = 130 if self._emphasized else 72
            painter.setPen(QPen(QColor(62, 119, 219, line_alpha), 1.7))
            painter.drawLine(start, tip)
            painter.setPen(QPen(QColor(46, 106, 215, 190), 1.4))
            painter.setBrush(QColor(197, 224, 255, 85))
            painter.drawEllipse(tip, 5.5, 5.5)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(50, 111, 223, 200))
            painter.drawEllipse(tip, 2.2, 2.2)
        finally:
            painter.end()


class MousePointerRodPad(QFrame):
    """Blue region: delayed aim overlay and native direct List/Exp selection."""
    PAD_HEIGHT = 180
    BASE_BOTTOM_MARGIN = 19
    HOVER_REVEAL_MS = 250
    WHEEL_EMPHASIS_MS = 650

    def __init__(self, remote):
        super().__init__(remote)
        self.setObjectName('mousePointerRodPad')
        self.setFixedHeight(self.PAD_HEIGHT)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip(
            '青い部分：方向／ホイール15px、押しながら60px／左クリックでカレント指定。'
            'Expだけダブルクリックで展開。右クリック無効。'
            '中央ぐりぐりは従来操作。')
        self._enabled = False
        self._length = DEFAULT_LENGTH
        self._direction = DEFAULT_DIRECTION
        self._double_pending = False
        self._wheel_during_press = False
        self._wheel_angle_remainder = 0
        self._wheel_pixel_remainder = 0
        self._left_pressed = False
        self._wheel_pad = None
        self._remote = remote
        self._overlay = None
        self._aim_hovering = False
        self._aim_visible = False
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_after_hover)
        self._wheel_emphasis_timer = QTimer(self)
        self._wheel_emphasis_timer.setSingleShot(True)
        self._wheel_emphasis_timer.timeout.connect(self._end_wheel_emphasis)
        self._theme = 'light'
        self.hide()

    def set_mode_enabled(self, enabled):
        self._enabled = bool(enabled)
        self._double_pending = False
        self._wheel_during_press = False
        self._left_pressed = False
        self._stop_aiming()
        self.setVisible(self._enabled)
        if self._enabled:
            # Defer the pointer check until Qt has laid out/reparented the
            # native central button. Merely enabling must not reveal the rod.
            QTimer.singleShot(0, self._sync_hover)

    def set_wheel_pad(self, pad):
        """Watch native central-button entry without stealing its events."""
        if self._wheel_pad is not None:
            self._wheel_pad.removeEventFilter(self)
        self._wheel_pad = pad
        if pad is not None:
            pad.installEventFilter(self)
        self._position_wheel_pad()

    def _position_wheel_pad(self):
        pad = self._wheel_pad
        if pad is not None:
            # Keep the green rod origin at the original bottom-center, NOT
            # underneath the ぐりぐり widget. Leave the top hint unobstructed.
            x = round((self.width() - pad.width()) / 2)
            y = max(0, round((self.height() - pad.height()) / 2))
            pad.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_wheel_pad()
        self.refresh_position()

    def eventFilter(self, obj, event):
        # The native ぐりぐり is a child of the blue pad. Parent leaveEvent
        # is not guaranteed on all Qt platforms when entering a child.
        if obj is self._wheel_pad:
            if event.type() == QEvent.Type.Enter:
                self._stop_aiming()
            elif event.type() == QEvent.Type.Leave:
                # After leaving the child, check whether the cursor returned
                # to the blue surface; never change the native pad's action.
                QTimer.singleShot(0, self._sync_hover)
        return super().eventFilter(obj, event)

    def set_theme(self, theme):
        self._theme = theme
        self.update()

    def origin_local(self):
        return (self.width() / 2.0, self.height() - self.BASE_BOTTOM_MARGIN)

    def origin_global(self):
        x, y = self.origin_local()
        point = self.mapToGlobal(QPoint(round(x), round(y)))
        return (point.x(), point.y())

    def tip_global(self):
        return rod_endpoint(self.origin_global(), self._direction, self._length)

    def adjust_length(self, steps, *, fast=False):
        """Wheel only: left button held selects the 60px fast gear."""
        if not self._enabled:
            return
        new_length = length_after_wheel(self._length, steps, fast=fast)
        if new_length != self._length:
            self._length = new_length
            self.refresh_position()

    def _in_blue(self, local_point):
        return (self.rect().contains(local_point) and
                (self._wheel_pad is None or
                 not self._wheel_pad.geometry().contains(local_point)))

    def _cursor_on_blue(self):
        return (self._enabled and self.isVisible() and
                self._in_blue(self.mapFromGlobal(QCursor.pos())))

    def _sync_hover(self):
        """Start one delay per blue entry; do not restart on every move."""
        if not self._cursor_on_blue():
            self._stop_aiming()
        else:
            # Entering the area without moving must still aim at the actual
            # cursor position rather than at the previous stored direction.
            here = self.mapFromGlobal(QCursor.pos())
            self._direction = direction_from_pointer(
                self.origin_local(), (here.x(), here.y()), self._direction)
            if not self._aim_hovering:
                self._aim_hovering = True
                self._hover_timer.start(self.HOVER_REVEAL_MS)

    def _show_after_hover(self):
        if not self._aim_hovering or not self._cursor_on_blue():
            self._stop_aiming()
            return
        self._aim_visible = True
        self.refresh_position()

    def _show_on_wheel(self):
        """Actual rod input is intentional: show immediately, temporarily darker."""
        if not self._cursor_on_blue():
            return
        self._sync_hover()
        self._aim_hovering = True
        self._aim_visible = True
        self._hover_timer.stop()
        self.refresh_position()
        if self._overlay is not None:
            self._overlay.set_emphasis(True)
        self._wheel_emphasis_timer.start(self.WHEEL_EMPHASIS_MS)

    def _end_wheel_emphasis(self):
        if self._overlay is not None:
            self._overlay.set_emphasis(False)

    def _stop_aiming(self):
        self._hover_timer.stop()
        self._wheel_emphasis_timer.stop()
        self._aim_hovering = False
        self._aim_visible = False
        self.hide_overlay()
        if self._overlay is not None:
            self._overlay.set_emphasis(False)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._sync_hover()

    def mouseMoveEvent(self, event):
        if self._enabled:
            origin = self.origin_local()
            pointer = (event.position().x(), event.position().y())
            # Moving across the central native pad must not change aim.
            if not self._in_blue(event.position().toPoint()):
                self._stop_aiming()
                event.accept()
                return
            # Mouse movement ONLY changes aim. Radius changes nothing.
            self._direction = direction_from_pointer(
                origin, pointer, self._direction)
            self._sync_hover()
            self.refresh_position()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._stop_aiming()
        super().leaveEvent(event)

    def _dispatch_tip_action(self, action):
        if not self._enabled:
            return False
        remote = self.parentWidget()
        launcher = remote.parent() if remote is not None else None
        if launcher is None:
            return False
        from mouse_pointer_rod_direct import direct_files_action
        return direct_files_action(launcher, self.tip_global(), action)

    def mousePressEvent(self, event):
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._left_pressed = True
            self._wheel_during_press = False
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._left_pressed = False
            # A held-left + wheel was length control, NOT a selection click.
            should_select = (not self._wheel_during_press and
                             self.rect().contains(event.position().toPoint()) and
                             (self._wheel_pad is None or not self._wheel_pad.geometry().contains(event.position().toPoint())))
            if should_select:
                self._dispatch_tip_action('double' if self._double_pending else 'select')
            self._double_pending = False
            self._wheel_during_press = False
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            # A List double-click is selection-only. Exp still toggles its
            # branch on the second release (through the direct adapter).
            self._left_pressed = True
            self._wheel_during_press = False
            self._double_pending = True
        event.accept()

    def contextMenuEvent(self, event):
        # Blue region has no context action; central ぐりぐり owns it.
        self._double_pending = False
        event.accept()

    def wheelEvent(self, event):
        # Only the blue region owns length adjustment. Keep high-resolution
        # wheel deltas across events, as the native ぐりぐり pad already does.
        angle = event.angleDelta().y()
        if angle:
            self._wheel_angle_remainder += angle
            steps = int(self._wheel_angle_remainder / 120)
            self._wheel_angle_remainder -= steps * 120
        else:
            self._wheel_pixel_remainder += event.pixelDelta().y()
            steps = int(self._wheel_pixel_remainder / 36)
            self._wheel_pixel_remainder -= steps * 36
        fast = self._left_pressed or bool(event.buttons() & Qt.MouseButton.LeftButton)
        if steps:
            self.adjust_length(steps, fast=fast)
            self._show_on_wheel()
            if fast:
                self._wheel_during_press = True
        event.accept()

    def refresh_position(self):
        # Remote movement, resizing and mode activation must not resurrect
        # an inactive guide. Only the delayed-hover/wheel gates may show it.
        if not self._enabled or not self.isVisible() or not self._aim_visible:
            return
        if not self._cursor_on_blue():
            self._stop_aiming()
            return
        if self._overlay is None:
            self._overlay = MousePointerRodOverlay(self.window())
        self._overlay.show_rod(self.origin_global(), self.tip_global())
        self.update()

    def hide_overlay(self):
        if self._overlay is not None:
            self._overlay.hide()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_hover)

    def hideEvent(self, event):
        self._double_pending = False
        self._left_pressed = False
        self._wheel_during_press = False
        self._stop_aiming()
        super().hideEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            is_light = self._theme == 'light'
            painter.setBrush(QColor('#e5f0f8' if is_light else '#304357'))
            painter.setPen(QPen(QColor('#8fb7a4' if is_light else '#688d7d'), 1.0))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), 4, 4)
            x, y = self.origin_local()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor('#6aa94a'))
            painter.drawEllipse(QPointF(x, y), 11.0, 11.0)
            painter.setPen(QColor('#365d53' if is_light else '#d9eee3'))
            painter.drawText(QRectF(6, 5, self.width() - 12, 23),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             'マウス差し棒  実験')
            painter.drawText(QRectF(6, 26, self.width() - 12, 19),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f'長さ：{round(self._length)} px')
            # Single line stays ABOVE the centered ぐりぐり button.
            painter.drawText(QRectF(6, 46, self.width() - 12, 19),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f'通常：{NORMAL_WHEEL_STEP_PX}px / 押下：{FAST_WHEEL_STEP_PX}px')
        finally:
            painter.end()
