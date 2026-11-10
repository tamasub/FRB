"""Mouse-only round flick guide for FRB Remote (no keyboard injection).

Press: a fixed circle appears above the first-hand button. Its eye shows
one of the common 1–4 geometric sectors. Returning to center cancels.
Releasing a chosen sector NEVER executes: the circle stays visible, and an
in-place confirmation starts at Cancel. Wheel on the SAME first-hand button
chooses Cancel/OK; a NEW click on that button confirms the chosen option.
No independent confirmation popup captures the pointer.
"""
import math
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, Signal, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QPushButton

from first_hand_confirmation import FirstHandConfirmation
from first_hand_trace import first_hand_trace
from shuriken_model import (choose_entry, uses_three_sector_guide,
                            uses_four_sector_guide, uses_two_horizontal_sector_guide,
                            two_horizontal_sector_slot, two_first_hand_sector_slot, three_sector_slot,
                            four_sector_slot, current_indicator_position,
                            THREE_SECTOR_DIVIDERS)
from launch_appearance import theme_family
from shuriken_assets import resource_root

# Icon provided for the experiment; retain the same asset in the packaged app.
ICON_PATH = resource_root(__file__) / 'assets' / 'remote_shuriken.png'


class ShurikenConfirmationHitLayer(QWidget):
    """Real, clickable confirmation buttons over the mouse-transparent guide.

    The big Pokeball stays a passive Tool window so it cannot steal drags from
    the small first-hand button. Only this 320x71 panel accepts clicks.
    """

    def __init__(self, preview, button):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowDoesNotAcceptFocus)
        super().__init__(button, flags)
        self._preview = preview
        self._button = button
        self.setObjectName('firstHandConfirmationClicks')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(320, 71)
        # Draw visible, nontransparent QPushButtons. Fully transparent child
        # surfaces in a layered Windows Tool window are not reliable hit areas.
        self.cancel_button = QPushButton('キャンセル', self)
        self.cancel_button.setObjectName('firstHandCancel')
        self.cancel_button.setGeometry(24, 35, 127, 27)
        self.cancel_button.setToolTip('一の手：キャンセル')
        self.cancel_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cancel_button.clicked.connect(
            lambda _checked=False: button.confirm_from_overlay('cancel'))
        self.ok_button = QPushButton('OK（実行）', self)
        self.ok_button.setObjectName('firstHandOK')
        self.ok_button.setGeometry(169, 35, 127, 27)
        self.ok_button.setToolTip('一の手：OK（実行）')
        self.ok_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ok_button.clicked.connect(
            lambda _checked=False: button.confirm_from_overlay('ok'))

    def hideEvent(self, event):
        if self._preview.confirmation is not None:
            first_hand_trace('confirmation_buttons_hidden', reason='qt_hide')
        super().hideEvent(event)

    def wheelEvent(self, event):
        # Rolling above the confirmation panel selects that confirmation too.
        self._button.wheelEvent(event)
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        dark = self._preview._theme == 'dark'
        painter.setPen(QPen(QColor('#67927c' if dark else '#597d64'), 1.5))
        painter.setBrush(QColor('#1b3439' if dark else '#f2fcf0'))
        painter.drawRoundedRect(QRectF(0, 0, 320, 71), 10, 10)
        font = QFont('Yu Gothic UI', 11)
        font.setPixelSize(12)
        painter.setFont(font)
        pending = self._preview.confirmation
        if pending is not None:
            caption = '実行候補：' + pending.candidate_title
            caption = QFontMetrics(font).elidedText(
                caption, Qt.TextElideMode.ElideRight, 293)
            painter.setPen(QColor('#e7f5ea' if dark else '#1f4932'))
            painter.drawText(QRectF(13, 6, 294, 24),
                             Qt.AlignmentFlag.AlignCenter, caption)
        painter.end()

    def show_at(self, preview):
        self._preview = preview
        pending = preview.confirmation
        dark = preview._theme == 'dark'
        for choice, button in (('cancel', self.cancel_button), ('ok', self.ok_button)):
            selected = pending is not None and pending.choice == choice
            background = ('#5e9d79' if dark else '#aad99b') if selected else ('#354950' if dark else '#ffffff')
            foreground = '#0e2a1e' if selected else ('#e3f3e7' if dark else '#35533c')
            button.setStyleSheet(
                'QPushButton { background: ' + background + '; color: ' + foreground +
                '; border: 1px solid #5c9878; border-radius: 6px; }'
                'QPushButton:hover { border: 2px solid #326b53; }')
        center = preview.circle_center
        top_left = QPoint(round(center.x() - 160), round(center.y() - 151))
        position = preview.mapToGlobal(top_left)
        if not self.isVisible():
            self.move(position)
            # Showing a second native Tool window on EVERY wheel notch can
            # produce a flash/reorder on Windows; show/raise only on recovery.
            self.show()
            self.raise_()
        elif self.pos() != position:
            # Reposition only if the Remote really moved, never per wheel step.
            self.move(position)
        self.update()


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
        self.confirmation = None  # Optional frozen candidate + wheel selection.
        self._confirmation_hit_layer = None
        self._theme = 'light'

    def set_theme(self, theme):
        self._theme = theme_family(theme)
        self.update()

    def present(self, button, entries, selected):
        """Show the complete circle ABOVE the shuriken button, not at cursor."""
        if not entries:
            self.hide()
            return
        self.entries = list(entries)
        self.selected_id = selected.item_id if selected is not None else ''
        # The 1st-hand button and Exp/List selector both use this preview.
        launcher = getattr(button, 'launcher', None)
        remote = button.parentWidget()
        # A WheelPad may be physically reparented inside the blue pointing
        # rod. Its immediate parent then has no theme and used to fall back
        # to light even when Launch/Remote were dark.
        current_theme = (getattr(launcher, 'color_theme', None)
                         or getattr(remote, 'files_exp_theme', 'light'))
        self.set_theme(current_theme)
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

    def set_confirmation(self, confirmation):
        """Overlay the confirmation without hiding, moving or re-opening the ring.

        Both the green eye and displayed confirmation refer to the SAME frozen
        item ID. The visual option only changes on the first-hand wheel.
        """
        if confirmation is not None and confirmation.candidate_id != self.selected_id:
            raise ValueError('Preview eye and confirmation candidate must match')
        self.confirmation = confirmation
        self.update()
        # Pure stand-ins used by the no-PySide6 tests have no native window;
        # only real previews create the small interactive window.
        if hasattr(self, '_confirmation_hit_layer'):
            if confirmation is None:
                if self._confirmation_hit_layer is not None:
                    self._confirmation_hit_layer.hide()
            else:
                if self._confirmation_hit_layer is None:
                    self._confirmation_hit_layer = ShurikenConfirmationHitLayer(
                        self, self.parentWidget())
                self._confirmation_hit_layer.show_at(self)

    def hideEvent(self, event):
        if self.confirmation is not None:
            first_hand_trace('confirmation_preview_hidden', reason='qt_hide')
        layer = getattr(self, '_confirmation_hit_layer', None)
        if layer is not None:
            layer.hide()
        super().hideEvent(event)

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

        # One round menu guide, using Remote's live light/dark palette.
        dark = self._theme == 'dark'
        painter.setPen(QPen(QColor('#667f82' if dark else '#9ac477'), 1.2))
        if dark:
            painter.setBrush(QColor('#25343a'))
        else:
            painter.setBrush(QColor(228, 244, 215, 255))  # Original light canvas.
        painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))

        count = len(self.entries)
        horizontal_pair = uses_two_horizontal_sector_guide(self.entries)
        triad = uses_three_sector_guide(self.entries)
        quad = uses_four_sector_guide(self.entries)
        band = (radius * 2.0) / count
        max_text_width = min(230, self.width() - 20)

        # Draw dividers from the same geometry used by choose_entry().
        painter.setPen(QPen(QColor('#52696f' if dark else '#9fc385'), 1.0))
        if horizontal_pair:
            painter.drawLine(QPointF(0, -radius), QPointF(0, radius))
        elif triad:
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
        if 1 <= count <= 4:
            painter.setPen(QPen(QColor('#a2bdb6' if dark else '#385e56'), 1.2))
            if dark:
                painter.setBrush(QColor('#192a30'))
            else:
                painter.setBrush(QColor('#ffffff'))  # Keep the established light center.
            painter.drawEllipse(QPointF(0, 0), self.CURRENT_RADIUS, self.CURRENT_RADIUS)

            # The model owns the marker location, including the idle center.
            marker_x, marker_y = current_indicator_position(
                self.entries, self.selected_id, self.MARKER_DISTANCE)
            painter.setPen(QPen(QColor('#96c79f' if dark else '#426d59'), 1.0))
            if dark:
                painter.setBrush(QColor('#7fb78d'))
            else:
                painter.setBrush(QColor('#aed2a0'))  # Original light indicator.
            painter.drawEllipse(QPointF(marker_x, marker_y),
                                self.MARKER_RADIUS, self.MARKER_RADIUS)

        TEXT_SIDE_PADDING = 8
        for index, entry in enumerate(self.entries):
            if horizontal_pair:
                text_anchor_x, text_cy, mark_x, mark_y, text_align = (
                    two_first_hand_sector_slot(entry) if entry.hand_index == 1
                    else two_horizontal_sector_slot(entry))
            elif triad:
                text_anchor_x, text_cy, mark_x, mark_y, text_align = three_sector_slot(entry)
            elif quad:
                text_anchor_x, text_cy, mark_x, mark_y, text_align = four_sector_slot(entry)
            else:
                # Two entries remain vertically ordered: up then down.
                # Keep their captions beyond the indicator, not on top of it.
                text_anchor_x = mark_x = 0.0
                if count == 1:
                    text_cy = -62.0
                    mark_y = -self.MARKER_DISTANCE
                elif count == 2:
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
                if dark:
                    painter.setBrush(QColor('#547e67'))
                else:
                    painter.setBrush(QColor(150, 203, 121, 125))
                painter.drawEllipse(QPointF(mark_x, mark_y),
                                    self.CURRENT_RADIUS, self.CURRENT_RADIUS)

            for grow, alpha in ((6, 26), (3, 44)):
                shadow = text_rect.adjusted(-grow, -grow / 2.0, grow, grow / 2.0)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(181, 214, 160, alpha))
                painter.drawRoundedRect(shadow, 8, 8)
            painter.setPen(QPen(QColor('#86b69a' if dark else '#82b369') if active
                                else QColor('#59767a' if dark else '#96be81'), 1.0))
            painter.setBrush(QColor('#426351' if dark else '#dcf3cc') if active
                             else QColor('#2d454b' if dark else '#ecf8e4'))
            painter.drawRoundedRect(text_rect, 7, 7)
            available_text_width = max(12, int(text_draw_rect.width()) - 2)
            if metrics.horizontalAdvance(caption) > available_text_width:
                caption = metrics.elidedText(caption, Qt.TextElideMode.ElideRight,
                                             available_text_width)
            painter.setPen(QColor('#eff7f2' if dark else '#254c35'))
            painter.drawText(text_draw_rect, draw_flags, caption)

        # Confirmation lives IN THIS SAME preview, above the still-visible
        # Pokeball. The original green eye remains frozen on the candidate.
        confirmation = self.confirmation
        if confirmation is not None:
            panel = QRectF(-160, -151, 320, 71)
            painter.setPen(QPen(QColor('#67927c' if dark else '#597d64'), 1.5))
            painter.setBrush(QColor('#1b3439' if dark else '#f2fcf0'))
            painter.drawRoundedRect(panel, 10, 10)
            painter.setPen(QColor('#e7f5ea' if dark else '#1f4932'))
            label = '実行候補：' + confirmation.candidate_title
            label = metrics.elidedText(label, Qt.TextElideMode.ElideRight, 293)
            painter.drawText(QRectF(-147, -145, 294, 24),
                             Qt.AlignmentFlag.AlignCenter, label)
            for choice, caption, rect in (
                ('cancel', 'キャンセル', QRectF(-136, -116, 127, 27)),
                ('ok', 'OK（実行）', QRectF(9, -116, 127, 27)),
            ):
                active = confirmation.choice == choice
                painter.setPen(QPen(QColor('#5c9878' if dark else '#4f835c'), 1))
                painter.setBrush(QColor('#5e9d79' if dark else '#aad99b') if active
                                 else QColor('#354950' if dark else '#ffffff'))
                painter.drawRoundedRect(rect, 6, 6)
                painter.setPen(QColor('#0e2a1e' if active else '#e3f3e7'
                                      if dark else '#35533c'))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, caption)
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
        self.setToolTip('手裏剣 1の手：フリックで候補 → 同じボタンでホイール選択（キャンセル／OK）→ クリック確定')
        self.setFixedSize(50, 46)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preview = None
        self._drag_start = None
        self._entries = []
        self._selected_entry = None  # The action whose eye is currently painted.
        self._confirmation_on_press = None
        self._pending_confirmation = None
        self._confirmation_click_armed = False
        self._confirmation_wheel_remainder = 0
        # A Qt.Tool preview can be hidden independently of the pending
        # confirmation (native activation, parent relayout, stacking). Keep
        # the dialog's *state* until an explicit OK/Cancel response. This
        # timer only restores visibility; it NEVER selects or executes.
        self._confirmation_visibility_timer = QTimer(self)
        self._confirmation_visibility_timer.setInterval(100)
        self._confirmation_visibility_timer.timeout.connect(
            self._ensure_confirmation_visibility)
        self._pixmap = QPixmap(str(ICON_PATH))

    def wheelEvent(self, event):
        pending = self._pending_confirmation
        if pending is not None:
            # The FIRST-HAND button itself is the only wheel selector for
            # its confirmation. Do not send any wheel to Files or the pad.
            angle = event.angleDelta().y()
            pixel = event.pixelDelta().y()
            self._confirmation_wheel_remainder += angle if angle else pixel * (120.0 / 36.0)
            if abs(self._confirmation_wheel_remainder) >= 120:
                pending.wheel(1 if self._confirmation_wheel_remainder > 0 else -1)
                self._confirmation_wheel_remainder = 0
                if self._preview is not None:
                    self._preview.set_confirmation(pending)
            event.accept()
            return
        # Otherwise preserve the button's original Remote wheel navigation.
        pad = getattr(self.parentWidget(), 'pad', None)
        if pad is not None:
            pad.wheelEvent(event)
        else:
            event.ignore()

    def confirmation_remote_command(self, command):
        """One owner while first-hand confirmation is open; never navigate Exp.

        The large ぐりぐり pad uses semantic UP/DOWN/CLICK commands, while a
        physical wheel on the first-hand button comes through wheelEvent.
        Both change/commit the SAME frozen candidate and painted option.
        """
        pending = self._pending_confirmation
        if pending is None:
            return False
        if command in ('UP', 'DOWN'):
            pending.wheel(1 if command == 'UP' else -1)
            if self._preview is not None:
                self._preview.set_confirmation(pending)
        elif command in ('CLICK', 'ENTER'):
            self._commit_first_hand_confirmation(clicked_inside=True)
        elif command in ('CANCEL', 'ESCAPE'):
            # Only an explicit cancellation response closes the confirmation.
            self._close_first_hand_confirmation(reason='cancel_command')
        # BACK, DOUBLE_CLICK and unrelated Remote commands must not dismiss
        # a confirmation that has already been displayed.
        # All commands are owned/consumed until confirmation is closed,
        # including unexpected target/menu navigation requests.
        return True

    def confirm_from_overlay(self, choice):
        """Real clicks on the painted Cancel/OK rectangles (not ghost Release)."""
        pending = self._pending_confirmation
        if pending is None or self._active_confirmation() is not None:
            return
        if choice == 'ok':
            pending.wheel(-1)  # Explicit OK click is equivalent to a deliberate choice.
        elif choice == 'cancel':
            pending.wheel(1)
        else:
            return
        self._commit_first_hand_confirmation(clicked_inside=True)

    def _commit_first_hand_confirmation(self, *, clicked_inside):
        pending = self._pending_confirmation
        if pending is None:
            return
        if not clicked_inside:
            # The original release outside this 50x46 button is NOT an
            # OK/Cancel answer. Do not silently close the confirmation.
            first_hand_trace('confirmation_commit_ignored', reason='release_outside')
            return
        if self._active_confirmation() is not None:
            # A separate Launch dialog arriving asynchronously cannot silently
            # dismiss the first-hand confirmation or execute the candidate.
            first_hand_trace('confirmation_commit_blocked', reason='other_dialog')
            return
        approved = pending.commit(clicked_inside)
        # Invariant: the marker, the confirmation, and the action ID are one.
        if (approved is not None and (self._selected_entry is None
                                     or self._selected_entry.item_id != approved
                                     or (self._preview is not None
                                         and hasattr(self._preview, 'selected_id')
                                         and self._preview.selected_id != approved))):
            # Never execute an action that differs from the on-screen eye.
            # Keep the prompt alive so the mismatch can be observed/cancelled.
            first_hand_trace('confirmation_commit_blocked', reason='eye_mismatch')
            return
        self._close_first_hand_confirmation(reason=('ok' if approved is not None else 'cancel'))
        if approved is not None:
            self.triggered.emit(approved)

    def _close_first_hand_confirmation(self, *, reason='explicit_cancel'):
        if self._pending_confirmation is not None:
            first_hand_trace('confirmation_closed', reason=reason)
        timer = getattr(self, '_confirmation_visibility_timer', None)
        if timer is not None:
            timer.stop()
        self._pending_confirmation = None
        self._confirmation_click_armed = False
        self._confirmation_wheel_remainder = 0
        self._drag_start = None
        self._selected_entry = None
        self._entries = []
        if self._preview is not None:
            self._preview.set_confirmation(None)
            self._preview.hide()

    def _ensure_confirmation_visibility(self):
        """Restore lost native Tool surfaces without ending/changing a dialog.

        This is a visibility safety net, not a replacement for blocking the
        automatic dismissal paths in app.py. Never synthesize user input here.
        """
        pending = self._pending_confirmation
        if pending is None:
            return
        preview = self._preview
        chosen = self._selected_entry
        if (preview is None or chosen is None or
                chosen.item_id != pending.candidate_id):
            first_hand_trace('confirmation_visibility_blocked', reason='candidate_mismatch')
            return
        selected = getattr(preview, 'selected_id', pending.candidate_id)
        if selected != pending.candidate_id:
            first_hand_trace('confirmation_visibility_blocked', reason='eye_mismatch')
            return
        # A genuinely hidden parent cannot host its owned Windows tool child.
        # Keep the pending answer intact and restore when the parent returns.
        parent = getattr(self, 'parentWidget', lambda: None)()
        for owner in (parent, self.launcher):
            visible = getattr(owner, 'isVisible', None)
            if callable(visible) and not visible():
                return
        preview_visible = getattr(preview, 'isVisible', None)
        if callable(preview_visible) and not preview_visible():
            first_hand_trace('confirmation_preview_restore', reason='native_hidden')
            preview.show()
            preview.raise_()
        layer = getattr(preview, '_confirmation_hit_layer', None)
        layer_visible = getattr(layer, 'isVisible', None)
        if layer is not None and callable(layer_visible) and not layer_visible():
            first_hand_trace('confirmation_buttons_restore', reason='native_hidden')
            preview.set_confirmation(pending)

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
        # The first-hand confirmation retains exclusive ownership until a
        # deliberate answer, even if another Launch dialog appears temporarily.
        if self._pending_confirmation is not None:
            # Confirmation is operated on this SAME 50x46 button: wheel to
            # choose, then a NEW press/release to commit. The original flick
            # release can never be mistaken for the confirmation click.
            self._confirmation_click_armed = True
            super().mousePressEvent(event)
            event.accept()
            return
        self._confirmation_on_press = self._active_confirmation()
        if self._confirmation_on_press is not None:
            # With a Launch-owned dialog open, this button confirms that
            # dialog, but does not start an unrelated shuriken action.
            self._drag_start = None
            self._entries = []
            self._selected_entry = None
            if self._preview is not None:
                self._preview.hide()
            super().mousePressEvent(event)
            return
        self._entries = self.launcher.shuriken_items(self.hand_index)
        self._drag_start = event.globalPosition().toPoint()
        self._selected_entry = None
        if self._preview is None:
            self._preview = ShurikenPreview(self)
        # PRESS only shows the guide; it must NOT preselect an action.
        self._preview.set_confirmation(None)
        self._preview.present(self, self._entries, None)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pending_confirmation is not None:
            # Keep the frozen candidate's marker and confirmation identical;
            # incidental pointer movement must not change either.
            event.accept()
            return
        if self._drag_start is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            point = event.globalPosition().toPoint()
            dx, dy = point.x() - self._drag_start.x(), point.y() - self._drag_start.y()
            # The guide stays ABOVE the button. The pointer only controls
            # the current mark; two rows or three 120° wedges never move.
            self._selected_entry = choose_entry(
                self._entries, dx, dy,
                min_release_distance=self.DRAG_DEADZONE)
            if self._preview is not None:
                # Draw exactly the committed choice; rendering and release
                # never use separate thresholds or timing rules.
                self._preview.present(self, self._entries, self._selected_entry)
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
        if event.button() == Qt.MouseButton.LeftButton and self._pending_confirmation is not None:
            armed = self._confirmation_click_armed
            self._confirmation_click_armed = False
            inside = self.rect().contains(event.position().toPoint())
            super().mouseReleaseEvent(event)
            if armed:
                self._commit_first_hand_confirmation(clicked_inside=inside)
            # A second ghost Release without a new Press is ignored.
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start is not None:
            # The displayed green eye is authoritative, even if the user
            # stops moving for several seconds or releases very slowly.
            # No separate release-time hit test may select an invisible
            # action or cancel a visible one.
            chosen = self._selected_entry
            self._drag_start = None
            super().mouseReleaseEvent(event)
            if chosen is not None and self._active_confirmation() is None:
                # This Release (even if Qt reports it spuriously) NEVER runs
                # the action. It ONLY freezes the exact eye-visible item.
                self._pending_confirmation = FirstHandConfirmation(
                    candidate_id=chosen.item_id, candidate_title=chosen.title)
                self._selected_entry = chosen
                if self._preview is not None:
                    # No new present()/show()/move(): the Pokeball remains
                    # visible. The green eye and prompt carry the SAME ID.
                    self._preview.set_confirmation(self._pending_confirmation)
                first_hand_trace('confirmation_open', reason='first_hand_flick')
                timer = getattr(self, '_confirmation_visibility_timer', None)
                if timer is not None:
                    timer.start()
            else:
                # Returning to the central cancel area closes normally.
                self._close_first_hand_confirmation()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def hideEvent(self, event):
        self._confirmation_on_press = None
        if self._pending_confirmation is not None:
            # A transient parent/widget hide must NEVER count as an answer.
            first_hand_trace('confirmation_owner_hidden', reason='qt_hide')
        else:
            self._close_first_hand_confirmation()
        super().hideEvent(event)
