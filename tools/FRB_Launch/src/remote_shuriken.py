"""Mouse-only round flick guide for FRB Remote (no keyboard injection).

Press: a fixed circle appears above the button. Three-menu mode uses the
same 120-degree geometry for label positions and flick hit-testing.
Release without movement cancels. Captions may overrun the constant circle.
"""
import math
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QPushButton

from shuriken_model import (choose_entry, uses_three_sector_guide,
                            three_sector_slot, THREE_SECTOR_DIVIDERS)
from launch_appearance import theme_family

# Icon provided for the experiment; retain the same asset in the packaged app.
ICON_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'remote_shuriken.png'


class ShurikenPreview(QWidget):
    """Passive, button-anchored round preview for the two-action baseline.

    A press shows the guide immediately. Pointer delta selects an action but
    never repositions the guide. Three entries use a left-up / right-up /
    bottom wedge guide and captions with readable, independently sized boxes.
    """
    CANVAS_WIDTH = 520        # Transparent window; NOT the circular guide size.
    CANVAS_HEIGHT = 320
    RADIUS = 72               # Constant visual radius, independent of captions.
    GAP_ABOVE_BUTTON = 15     # Visible gap between ring and the button.
    CURRENT_RADIUS = 24       # Reduced marker (diameter 48px) for a quieter guide.
    LABEL_FONT_PX = 12        # Readable; long titles extend beyond the ring.

    def __init__(self, owner):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus |
                 Qt.WindowType.WindowTransparentForInput)
        super().__init__(owner, flags)
        self.setObjectName('remoteShurikenPreview')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        self.circle_center = QPointF(self.CANVAS_WIDTH / 2, self.CANVAS_HEIGHT / 2)
        self.entries = []
        self.selected_id = ''

    def present(self, button, entries, selected):
        """Show the complete circle ABOVE the shuriken button, not at cursor."""
        if not entries:
            self.hide()
            return
        self.entries = list(entries)
        self.selected_id = selected.item_id if selected is not None else ''
        button_top = button.mapToGlobal(QPoint(button.width() // 2, 0))
        cx = button_top.x()
        cy = button_top.y() - self.GAP_ABOVE_BUTTON - self.RADIUS

        screen = QApplication.screenAt(button_top)
        if screen is None:
            screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        # Clamp only if the button is too close to the desktop edge. Under
        # normal conditions the ring center stays aligned to the button.
        cx = max(avail.left() + self.RADIUS + 3,
                 min(cx, avail.right() - self.RADIUS - 3))
        cy = max(avail.top() + self.RADIUS + 3, cy)
        canvas_x = max(avail.left(), min(cx - self.CANVAS_WIDTH // 2,
                                        avail.right() - self.CANVAS_WIDTH + 1))
        canvas_y = max(avail.top(), min(cy - self.CANVAS_HEIGHT // 2,
                                       avail.bottom() - self.CANVAS_HEIGHT + 1))
        self.move(int(canvas_x), int(canvas_y))
        self.circle_center = QPointF(cx - canvas_x, cy - canvas_y)
        if not self.isVisible():
            self.show()
        self.update()

    def paintEvent(self, event):
        if not self.entries:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.translate(self.circle_center)
        radius = self.RADIUS
        font = QFont('Yu Gothic UI', 11)
        font.setPixelSize(self.LABEL_FONT_PX)
        painter.setFont(font)
        metrics = QFontMetrics(font)

        # One round menu guide. The ring NEVER grows to fit a long label.
        painter.setPen(QPen(QColor(154, 196, 119, 210), 1.2))
        painter.setBrush(QColor(228, 244, 215, 255))  # Solid circular background.
        painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))

        count = len(self.entries)
        triad = uses_three_sector_guide(self.entries)
        band = (radius * 2.0) / count
        max_text_width = min(230, self.width() - 20)

        # Draw the *same* three 120-degree dividers used by choose_entry().
        # The ring stays one fixed circle, even if the captions overrun it.
        painter.setPen(QPen(QColor(159, 195, 133, 185), 1.0))
        if triad:
            for angle in THREE_SECTOR_DIVIDERS:
                theta = math.radians(angle)
                painter.drawLine(QPointF(0, 0), QPointF(radius * math.cos(theta),
                                                        radius * math.sin(theta)))
        else:
            for index in range(1, count):
                y = -radius + index * band
                half_width = math.sqrt(max(0.0, radius * radius - y * y))
                painter.drawLine(QPointF(-half_width, y), QPointF(half_width, y))

        for index, entry in enumerate(self.entries):
            if triad:
                text_cx, text_cy, mark_x, mark_y = three_sector_slot(entry)
            else:
                text_cx = mark_x = 0.0
                text_cy = mark_y = -radius + (index + 0.5) * band

            caption = entry.title
            text_w = min(max_text_width, metrics.horizontalAdvance(caption) + 18)
            text_h = max(18, metrics.height() + 6)
            text_rect = QRectF(text_cx - text_w / 2.0, text_cy - text_h / 2.0,
                               text_w, text_h)
            active = entry.item_id == self.selected_id
            if active:
                # Keep 48px for the 120° wedges. At r=42px it fits wholly
                # inside a radius-72px circular sector (the min clearance
                # to an edge is >24px).
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(150, 203, 121, 125))
                painter.drawEllipse(QPointF(mark_x, mark_y),
                                    self.CURRENT_RADIUS, self.CURRENT_RADIUS)

            # Soft green semi-transparent textbox, centered on each segment.
            # Keep its width independent of the circular guide's radius.
            for grow, alpha in ((6, 26), (3, 44)):
                shadow = text_rect.adjusted(-grow, -grow / 2.0,
                                            grow, grow / 2.0)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(181, 214, 160, alpha))
                painter.drawRoundedRect(shadow, 8, 8)
            painter.setPen(QPen(QColor(130, 179, 105, 210) if active
                                else QColor(150, 190, 129, 170), 1.0))
            painter.setBrush(QColor(220, 243, 204, 227) if active
                             else QColor(236, 248, 228, 208))
            painter.drawRoundedRect(text_rect, 7, 7)
            if metrics.horizontalAdvance(caption) > (text_w - 10):
                caption = metrics.elidedText(caption, Qt.TextElideMode.ElideRight,
                                            int(text_w - 10))
            painter.setPen(QColor('#254c35'))
            painter.drawText(text_rect,
                             int(Qt.AlignmentFlag.AlignCenter |
                                 Qt.AlignmentFlag.AlignVCenter), caption)
        painter.end()


class ShurikenButton(QPushButton):
    triggered = Signal(str)  # item ID from the current main Launch JSON
    DRAG_DEADZONE = 14

    def __init__(self, launcher, remote, hand_index=1):
        super().__init__('', remote)
        self.launcher = launcher
        self.hand_index = int(hand_index)
        self.setObjectName('remoteShurikenButton')
        self.setProperty('role', 'quick')
        self.setToolTip('手裏剣 1の手：押したまま方向へフリック、離して実行')
        self.setFixedSize(50, 46)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preview = None
        self._drag_start = None
        self._entries = []
        self._direction = ''
        self._confirmation_on_press = None
        self._pixmap = QPixmap(str(ICON_PATH))

    def wheelEvent(self, event):
        # The button inherits Remote's original wheel-navigation guarantee.
        pad = getattr(self.parentWidget(), 'pad', None)
        if pad is not None:
            pad.wheelEvent(event)
        else:
            event.ignore()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        if not self._pixmap.isNull():
            painter.drawPixmap(QRect(15, 3, 20, 20), self._pixmap)
        family = theme_family(getattr(self.parentWidget(), 'files_exp_theme', 'light'))
        painter.setPen(QColor('#24483d' if family == 'light' else '#e4f6ee'))
        font = QFont('Yu Gothic UI', 9)
        font.setPixelSize(10)
        painter.setFont(font)
        painter.drawText(QRect(1, 25, 48, 16), Qt.AlignmentFlag.AlignCenter,
                         f'{self.hand_index}の手')
        painter.end()

    def _active_confirmation(self):
        """Only Launch-owned dialogs are eligible for confirmation clicks.

        The same controllers already receive Remote's central CLICK.  A
        Shuriken click must NOT act like an Enter key sent to the desktop.
        """
        return (getattr(self.launcher, '_remote_text_dialog', None)
                or getattr(self.launcher, '_remote_confirmation', None))

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        self._confirmation_on_press = self._active_confirmation()
        if self._confirmation_on_press is not None:
            # With a dialog open, this SAME button becomes its confirm button.
            # Never show the shuriken guide or start a new background action.
            self._drag_start = None
            self._entries = []
            if self._preview is not None:
                self._preview.hide()
            super().mousePressEvent(event)
            return
        self._entries = self.launcher.shuriken_items(self.hand_index)
        self._drag_start = event.globalPosition().toPoint()
        self._direction = ''
        if self._preview is None:
            self._preview = ShurikenPreview(self)
        # PRESS only shows the guide; it must NOT preselect an action.
        self._preview.present(self, self._entries, None)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            point = event.globalPosition().toPoint()
            dx, dy = point.x() - self._drag_start.x(), point.y() - self._drag_start.y()
            # The guide stays ABOVE the button. The pointer only controls
            # the current mark; two rows or three 120° wedges never move.
            choice = choose_entry(self._entries, dx, dy,
                                  min_release_distance=self.DRAG_DEADZONE)
            if self._preview is not None:
                self._preview.present(self, self._entries, choice)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._confirmation_on_press is not None:
            controller = self._confirmation_on_press
            self._confirmation_on_press = None
            # Match a normal button click: releasing away from the button
            # cancels.  Revalidate the very SAME dialog in case it closed
            # between press and release; never fall through to a file action.
            inside = self.rect().contains(event.position().toPoint())
            super().mouseReleaseEvent(event)
            if inside and self._active_confirmation() is controller:
                controller.remote_command('CLICK')
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start is not None:
            point = event.globalPosition().toPoint()
            dx, dy = point.x() - self._drag_start.x(), point.y() - self._drag_start.y()
            chosen = choose_entry(self._entries, dx, dy)
            self._drag_start = None
            self._entries = []
            self._direction = ''
            if self._preview is not None:
                self._preview.hide()
            super().mouseReleaseEvent(event)
            if chosen is not None:
                # A dialog that appeared mid-drag blocks new Launch actions.
                if self._active_confirmation() is None:
                    self.triggered.emit(chosen.item_id)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def hideEvent(self, event):
        self._confirmation_on_press = None
        self._drag_start = None
        if self._preview is not None:
            self._preview.hide()
        super().hideEvent(event)
