"""Mouse-only round flick guide for FRB Remote (no keyboard injection).

Press: a fixed circle appears above the button. With two to four actions,
a white center ring and one green indicator show the current gesture sector.
Four actions use an X divider and cardinal kana-style flick directions.
Release without movement cancels. Captions may overrun the constant circle.
"""
import math
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QPushButton

from shuriken_model import (choose_entry, uses_three_sector_guide,
                            uses_four_sector_guide, three_sector_slot,
                            four_sector_slot, current_indicator_position,
                            THREE_SECTOR_DIVIDERS)
from launch_appearance import theme_family

# Icon provided for the experiment; retain the same asset in the packaged app.
ICON_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'remote_shuriken.png'


class ShurikenPreview(QWidget):
    """Button-anchored preview; selection is indicated, never executed here.

    Idle: green indicator at the white center ring. Dragging: green indicator
    moves to the currently selected sector. Gesture and preview share the
    same angles, and the guide never follows the pointer.
    """
    CANVAS_WIDTH = 520        # Transparent window; NOT the circular guide size.
    CANVAS_HEIGHT = 320
    RADIUS = 72               # Constant visual radius, independent of captions.
    GAP_ABOVE_BUTTON = 15     # Visible gap between ring and the button.
    CURRENT_RADIUS = 24       # White central origin ring (diameter 48 px).
    MARKER_RADIUS = 12.5      # Single green current indicator, center or sector.
    MARKER_DISTANCE = 42      # 24 + 12.5 < 42 < 72 - 12.5.
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
        quad = uses_four_sector_guide(self.entries)
        band = (radius * 2.0) / count
        max_text_width = min(230, self.width() - 20)

        # Draw dividers from the same geometry used by choose_entry().
        painter.setPen(QPen(QColor(159, 195, 133, 185), 1.0))
        if triad:
            for angle in THREE_SECTOR_DIVIDERS:
                theta = math.radians(angle)
                painter.drawLine(QPointF(0, 0), QPointF(radius * math.cos(theta),
                                                        radius * math.sin(theta)))
        elif quad:
            # The cardinal four-way guide uses an X (not the old +).
            # Endpoints stop exactly on the circumference (no spillover).
            diagonal = radius / math.sqrt(2.0)
            painter.drawLine(QPointF(-diagonal, -diagonal),
                             QPointF(diagonal, diagonal))
            painter.drawLine(QPointF(-diagonal, diagonal),
                             QPointF(diagonal, -diagonal))
        else:
            for index in range(1, count):
                y = -radius + index * band
                half_width = math.sqrt(max(0.0, radius * radius - y * y))
                painter.drawLine(QPointF(-half_width, y), QPointF(half_width, y))

        # The same origin is visible for 2-, 3- and 4-menu guides.
        # Paint it *after* dividers to hide crossings in the center.
        if 2 <= count <= 4:
            painter.setPen(QPen(QColor('#385e56'), 1.2))
            painter.setBrush(QColor('#ffffff'))
            painter.drawEllipse(QPointF(0, 0), self.CURRENT_RADIUS, self.CURRENT_RADIUS)

            # The model owns the marker location, including the idle center.
            marker_x, marker_y = current_indicator_position(
                self.entries, self.selected_id, self.MARKER_DISTANCE)
            painter.setPen(QPen(QColor('#426d59'), 1.0))
            painter.setBrush(QColor('#aed2a0'))
            painter.drawEllipse(QPointF(marker_x, marker_y),
                                self.MARKER_RADIUS, self.MARKER_RADIUS)

        TEXT_SIDE_PADDING = 8
        for index, entry in enumerate(self.entries):
            if triad:
                text_anchor_x, text_cy, mark_x, mark_y, text_align = three_sector_slot(entry)
            elif quad:
                text_anchor_x, text_cy, mark_x, mark_y, text_align = four_sector_slot(entry)
            else:
                # Two entries remain vertically ordered: up then down.
                # Keep their captions beyond the indicator, not on top of it.
                text_anchor_x = mark_x = 0.0
                if count == 2:
                    is_up = (entry.direction == 'up'
                             if {row.direction for row in self.entries} == {'up', 'down'}
                             else index == 0)
                    text_cy = -62.0 if is_up else 62.0
                    mark_y = -self.MARKER_DISTANCE if is_up else self.MARKER_DISTANCE
                else:
                    text_cy = mark_y = -radius + (index + 0.5) * band
                text_align = 'center'

            caption = entry.title
            text_w = min(max_text_width, metrics.horizontalAdvance(caption) + 18 + TEXT_SIDE_PADDING * 2)
            text_h = max(18, metrics.height() + 6)
            if text_align == 'right':
                text_rect = QRectF(text_anchor_x - text_w, text_cy - text_h / 2.0, text_w, text_h)
                draw_flags = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif text_align == 'left':
                text_rect = QRectF(text_anchor_x, text_cy - text_h / 2.0, text_w, text_h)
                draw_flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            else:
                text_rect = QRectF(text_anchor_x - text_w / 2.0, text_cy - text_h / 2.0,
                                   text_w, text_h)
                draw_flags = int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            text_draw_rect = text_rect.adjusted(TEXT_SIDE_PADDING, 0, -TEXT_SIDE_PADDING, 0)
            active = entry.item_id == self.selected_id
            # For the general 5+ fallback retain the original row highlight.
            if active and count > 4:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(150, 203, 121, 125))
                painter.drawEllipse(QPointF(mark_x, mark_y),
                                    self.CURRENT_RADIUS, self.CURRENT_RADIUS)

            for grow, alpha in ((6, 26), (3, 44)):
                shadow = text_rect.adjusted(-grow, -grow / 2.0, grow, grow / 2.0)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(181, 214, 160, alpha))
                painter.drawRoundedRect(shadow, 8, 8)
            painter.setPen(QPen(QColor(130, 179, 105, 210) if active
                                else QColor(150, 190, 129, 170), 1.0))
            painter.setBrush(QColor(220, 243, 204, 227) if active
                             else QColor(236, 248, 228, 208))
            painter.drawRoundedRect(text_rect, 7, 7)
            available_text_width = max(12, int(text_draw_rect.width()) - 2)
            if metrics.horizontalAdvance(caption) > available_text_width:
                caption = metrics.elidedText(caption, Qt.TextElideMode.ElideRight,
                                             available_text_width)
            painter.setPen(QColor('#254c35'))
            painter.drawText(text_draw_rect, draw_flags, caption)
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
