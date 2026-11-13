"""Mouse Pointer Rod v0.9: an unobtrusive, hover-activated aiming overlay.

Only wheel gestures over the blue surface change length (15px/notch, or
60px/notch while the left button is held there). The embedded ぐりぐり retains
its native List/Exp/Browser wheel, click, right-click and hold commands.
The rod fades into view after an intentional 250ms hover, and disappears
when leaving the blue surface or entering the native ぐりぐり. The ORIGINAL
click adapter never moves the OS cursor. A separate explicit Windows-mode
adapter can temporarily move it to the tip, emit a native click, and restore it.
"""

from PySide6.QtCore import Qt, QEvent, QTimer, QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QCursor, QPainter, QPen, QFont
from PySide6.QtWidgets import QApplication, QFrame, QWidget, QMenu

from rod_foreground import foreground_owned_by_process
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
                 Qt.WindowType.WindowTransparentForInput |
                 Qt.WindowType.WindowStaysOnTopHint)
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
        # QMenu/popups can be a separate top-level native window.  Keep the
        # mouse-transparent guide above them without changing input focus.
        # Page/history QMenus deliberately use Qt.Tool rather than Qt.Popup
        # so the Remote remains clickable. activePopupWidget() is None for
        # those tool menus; still keep the rod line in FRONT of their items.
        top_levels = getattr(QApplication, 'topLevelWidgets', None)
        menu_open = (callable(top_levels) and any(
            isinstance(widget, QMenu) and widget.isVisible()
            for widget in top_levels()))
        if QApplication.activePopupWidget() is not None or menu_open:
            self.raise_()
        if self.isVisible():
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


class MousePointerRodOrigin(QWidget):
    """Real, mouse-transparent green anchor just ABOVE the native ぐりぐり.

    The marker is a child of the blue pad, not another full-width row.
    Its center is the one authoritative origin used for painting, pointing
    and SMART geometry. The remote's current-folder band stays separate.
    """
    DIAMETER = 22

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('mousePointerRodOrigin')
        self.setFixedSize(self.DIAMETER, self.DIAMETER)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.hide()

    def origin_global(self):
        point = self.mapToGlobal(QPoint(round(self.width() / 2),
                                        round(self.height() / 2)))
        return (point.x(), point.y())

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor('#6aa94a'))
            painter.drawEllipse(QPointF(self.width() / 2, self.height() / 2),
                                9.0, 9.0)
        finally:
            painter.end()


class MousePointerRodPad(QFrame):
    """Blue region: delayed aim overlay and independently selectable click adapter."""
    PAD_HEIGHT = 144  # +30 px of blue aiming room; folder band is still separate.
    BASE_BOTTOM_MARGIN = 66  # fallback: button 46 + bottom 4 + marker half 11 + gap 5
    ORIGIN_GAP_ABOVE_GRIGRI = 5  # Clear gap between marker bottom and button.
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
        self._windows_click_mode = False  # Existing direct List/Exp adapter by default.
        self._smart_mode = False  # Independent, opt-in vertical tracking experiment.
        self._smart_expected_cursor = None
        self._length = DEFAULT_LENGTH
        self._direction = DEFAULT_DIRECTION
        self._double_pending = False
        self._wheel_during_press = False
        self._native_warp_guard = False
        self._pending_native_tip = None
        self._native_single_timer = QTimer(self)
        self._native_single_timer.setSingleShot(True)
        self._native_single_timer.timeout.connect(self._flush_pending_native_click)
        # Native popups capture hover/leave events.  Only while the Windows
        # experiment is enabled, poll the REAL cursor to restore the guide.
        self._native_hover_watchdog = QTimer(self)
        self._native_hover_watchdog.setInterval(95)
        self._native_hover_watchdog.timeout.connect(self._watch_windows_hover)
        # Topmost transparent overlay must not outlive Launch foreground focus.
        self._foreground_watchdog = QTimer(self)
        self._foreground_watchdog.setInterval(100)
        self._foreground_watchdog.timeout.connect(self._watch_foreground)
        self._wheel_angle_remainder = 0
        self._wheel_pixel_remainder = 0
        self._left_pressed = False
        self._wheel_pad = None
        self._origin_marker = None
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

    def set_windows_click_mode(self, enabled):
        """Use native Windows clicks only when expressly selected in settings."""
        self._windows_click_mode = bool(enabled)
        self._cancel_pending_native_click()
        self._update_windows_watchdog()
        self.setToolTip(
            ('Windowsマウス方式：青い部分で照準、左クリックで先端にOSクリック。'
             'ダブルクリック可。カーソルは元の位置へ復帰。右クリック無効。'
             if self._windows_click_mode else
             '青い部分：方向／ホイール15px、押しながら60px／左クリックでカレント指定。'
             'Expだけダブルクリックで展開。右クリック無効。中央ぐりぐりは従来操作。'))
        self.update()

    def set_smart_mode(self, enabled):
        """Opt-in: wheel translates the tip vertically and warps the real cursor."""
        self._smart_mode = bool(enabled)
        self._smart_expected_cursor = None
        self.update()

    def set_mode_enabled(self, enabled):
        self._enabled = bool(enabled)
        self._double_pending = False
        self._wheel_during_press = False
        self._left_pressed = False
        cancel = getattr(self, '_cancel_pending_native_click', None)
        if callable(cancel):
            cancel()
        self._stop_aiming()
        self._smart_expected_cursor = None
        self.setVisible(self._enabled)
        update_watchdog = getattr(self, '_update_windows_watchdog', None)
        if callable(update_watchdog):
            update_watchdog()
        if self._enabled:
            # Defer the pointer check until Qt has laid out/reparented the
            # native central button. Merely enabling must not reveal the rod.
            QTimer.singleShot(0, self._sync_hover)

    def _update_windows_watchdog(self):
        if self._enabled and self._windows_click_mode and self.isVisible():
            if not self._native_hover_watchdog.isActive():
                self._native_hover_watchdog.start()
        else:
            self._native_hover_watchdog.stop()

    def _watch_windows_hover(self):
        """Recover aim even while Qt's native popup owns mouse tracking."""
        if not self._enabled or not self._windows_click_mode or not self.isVisible():
            self._native_hover_watchdog.stop()
            return
        if not self._cursor_on_blue():
            if not self._native_warp_guard:
                self._stop_aiming()
            return
        self._sync_hover()
        if self._aim_visible:
            self.refresh_position()

    def _cancel_pending_native_click(self):
        self._native_single_timer.stop()
        self._pending_native_tip = None

    def _queue_native_single_click(self):
        """Wait for Qt's double-click gesture before sending anything to OS.

        If we warp the real pointer out/back for the first click, Windows
        resets the double-click target/window; a later second click cannot
        reliably become a native double click.  Buffer the first release.
        """
        self._pending_native_tip = self.tip_global()
        delay_ms = max(1, QApplication.styleHints().mouseDoubleClickInterval())
        self._native_single_timer.start(delay_ms)

    def _flush_pending_native_click(self):
        tip = self._pending_native_tip
        self._pending_native_tip = None
        if tip is None or not (self._enabled and self._windows_click_mode):
            return
        remote = self.parentWidget()
        launcher = remote.parent() if remote is not None else None
        if launcher is not None and self._cursor_on_blue():
            self._dispatch_windows_click('select', remote, launcher, target_override=tip)

    def _finish_native_warp(self):
        """Qt does not always send Enter after a QMenu takes the grab."""
        if self._enabled and self._windows_click_mode and self._cursor_on_blue():
            self._aim_hovering = True
            self._aim_visible = True
            self._hover_timer.stop()
            self.refresh_position()
        self._native_warp_guard = False

    def set_origin_marker(self, marker):
        """Bind the actual green pivot to the blue pad above ぐりぐり."""
        self._origin_marker = marker
        self._position_origin_marker()
        self.refresh_position()

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
            x = round((self.width() - pad.width()) / 2)
            y = max(0, self.height() - pad.height() - 4)
            pad.move(x, y)
        self._position_origin_marker()

    def _position_origin_marker(self):
        """Place green anchor DIRECTLY above ぐりぐり, inside the blue pad.

        Run whenever the pad is resized or the button is reparented. The
        marker is click-through, so aiming still works right across it.
        """
        marker = self._origin_marker
        if marker is None:
            return
        pad = self._wheel_pad
        button_top = (pad.y() if pad is not None else
                      self.height() - 46 - 4)
        x = round((self.width() - marker.width()) / 2)
        y = max(0, button_top - marker.height() - self.ORIGIN_GAP_ABOVE_GRIGRI)
        marker.move(x, y)

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
        # The green marker is INSIDE blue, directly above ぐりぐり. Convert
        # the same physical center to local coordinates for all rod modes.
        if self._origin_marker is not None:
            gx, gy = self._origin_marker.origin_global()
            pt = self.mapFromGlobal(QPoint(round(gx), round(gy)))
            return (float(pt.x()), float(pt.y()))
        return (self.width() / 2.0, self.height() - self.BASE_BOTTOM_MARGIN)

    def origin_global(self):
        if self._origin_marker is not None:
            return self._origin_marker.origin_global()
        x, y = self.origin_local()
        point = self.mapToGlobal(QPoint(round(x), round(y)))
        return (point.x(), point.y())

    def tip_global(self):
        return rod_endpoint(self.origin_global(), self._direction, self._length)

    def adjust_length(self, steps, *, fast=False):
        """Original length wheel, or opt-in SMART vertical-tip wheel."""
        if not self._enabled:
            return
        if getattr(self, '_smart_mode', False):
            self._smart_adjust_vertical(steps, fast=fast)
            return
        new_length = length_after_wheel(self._length, steps, fast=fast)
        if new_length != self._length:
            self._length = new_length
            self.refresh_position()

    def _smart_adjust_vertical(self, steps, *, fast=False):
        """Wheel: tip moves vertically; actual blue cursor stays on its ray.

        Compute in pad-local coordinates to avoid virtual desktop/DPI offsets.
        The OS pointer is only warped when SMART mode is explicitly enabled.
        """
        if not steps or not self._cursor_on_blue():
            return
        from mouse_pointer_rod_smart_model import smart_vertical_step
        from mouse_pointer_rod_smart_cursor import move_smart_cursor
        origin = self.origin_local()
        tip = rod_endpoint(origin, self._direction, self._length)
        original_global = QCursor.pos()
        current = self.mapFromGlobal(original_global)
        current_local = (float(current.x()), float(current.y()))
        button = self._wheel_pad.geometry() if self._wheel_pad is not None else None
        exclusion = ((button.left(), button.top(), button.right(), button.bottom())
                     if button is not None else None)
        dy = -int(steps) * (FAST_WHEEL_STEP_PX if fast else NORMAL_WHEEL_STEP_PX)
        result = smart_vertical_step(
            origin, tip, current_local, dy,
            (0, 0, self.width() - 1, self.height() - 1), exclusion)
        if result is None:
            return  # At the pad/central-button/length boundary: hold position.
        new_local = QPoint(round(result.cursor[0]), round(result.cursor[1]))
        if not self._in_blue(new_local):
            return  # Pixel rounding must never land on ぐりぐり or outside blue.
        new_global = self.mapToGlobal(new_local)
        old_length, old_direction = self._length, self._direction
        # Publish the new geometry AND the warp guard before setPos(). Some
        # Qt platforms deliver synthetic mouse events synchronously.
        self._length = result.length
        self._direction = result.direction
        self._smart_expected_cursor = new_global
        if not move_smart_cursor(QCursor, new_global):
            self._length, self._direction = old_length, old_direction
            self._smart_expected_cursor = None
            return  # A denied cursor move must not change rod geometry.
        # Next *physical* move clears the guard, and aiming resumes exactly
        # from the new blue-pad cursor position (no stale-event snap).
        self.refresh_position()

    def _in_blue(self, local_point):
        return (self.rect().contains(local_point) and
                (self._wheel_pad is None or
                 not self._wheel_pad.geometry().contains(local_point)))

    def _launch_has_foreground(self):
        owned = foreground_owned_by_process()
        if owned is None:
            return QApplication.applicationState() == Qt.ApplicationState.ApplicationActive
        return owned

    def _watch_foreground(self):
        if not self._launch_has_foreground():
            self._cancel_pending_native_click()
            self._stop_aiming()

    def _cursor_on_blue(self):
        return (self._enabled and self.isVisible() and
                self._launch_has_foreground() and
                self._in_blue(self.mapFromGlobal(QCursor.pos())))

    def _sync_hover(self):
        """Start one delay per blue entry; do not restart on every move."""
        if not self._cursor_on_blue():
            self._stop_aiming()
        else:
            # Entering the area without moving must still aim at the actual
            # cursor position rather than at the previous stored direction.
            cursor = QCursor.pos()
            expected = getattr(self, '_smart_expected_cursor', None)
            if not (getattr(self, '_smart_mode', False) and
                    expected is not None and cursor == expected):
                self._smart_expected_cursor = None
                here = self.mapFromGlobal(cursor)
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
            if getattr(self, '_native_warp_guard', False):
                event.accept()
                return
            origin = self.origin_local()
            expected = getattr(self, '_smart_expected_cursor', None)
            if getattr(self, '_smart_mode', False) and expected is not None:
                if QCursor.pos() == expected:
                    event.accept()  # Warp event: the tip geometry is already set.
                    return
                self._smart_expected_cursor = None
            # A programmatic cursor warp can leave a queued stale Qt move
            # event behind.  In SMART mode always read the REAL current
            # position, so the next manual sideways movement never jumps.
            local_pos = (self.mapFromGlobal(QCursor.pos())
                         if getattr(self, '_smart_mode', False) else
                         event.position().toPoint())
            pointer = (float(local_pos.x()), float(local_pos.y())) if getattr(
                self, '_smart_mode', False) else (event.position().x(), event.position().y())
            # Moving across the central native pad must not change aim.
            if not self._in_blue(local_pos):
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
        # Temporary native pointer warping generates a synthetic Leave during a native click.
        # The OS pointer is already back on the pad when Qt delivers it.
        if not getattr(self, '_native_warp_guard', False):
            self._stop_aiming()
        super().leaveEvent(event)

    def _dispatch_tip_action(self, action):
        foreground_check = getattr(self, '_launch_has_foreground', None)
        if not self._enabled or (callable(foreground_check) and not foreground_check()):
            return False
        remote = self.parentWidget()
        launcher = remote.parent() if remote is not None else None
        if launcher is None:
            return False
        if self._windows_click_mode:
            return self._dispatch_windows_click(action, remote, launcher)
        from mouse_pointer_rod_direct import direct_files_action
        return direct_files_action(launcher, self.tip_global(), action)

    def _dispatch_windows_click(self, action, remote, launcher, target_override=None):
        """Single click or two-click native sequence at ONE fixed screen point.

        Native double clicks must not warp the cursor away between clicks.
        The first physical release is buffered so a second release can replace
        it with one reliable OS double click, not a triple click.
        """
        if action not in ('select', 'double'):
            return False
        if not self._cursor_on_blue():
            return False
        tip_x, tip_y = self.tip_global() if target_override is None else target_override
        target = QPoint(round(tip_x), round(tip_y))
        if QApplication.screenAt(target) is None:
            return False  # Do not click an invalid off-desktop point.
        if remote.frameGeometry().contains(target):
            return False  # The blue pad must never recursively click itself.

        # Page columns are non-grabbing QMenus in THIS Qt process. Windows
        # SendInput can reach Chrome and the Files history menu, but its
        # button sequence may not activate these cascade QActions. Resolve
        # the visible item once by the exact rod tip and let the existing
        # QAction callback perform its own operation. No per-item logic.
        from mouse_pointer_rod_qt_menu import dispatch_page_cascade_action
        top_levels = getattr(QApplication, 'topLevelWidgets', None)
        if (callable(top_levels) and
                dispatch_page_cascade_action(target, top_levels())):
            return True

        # Our QMenus run in the SAME Qt GUI thread as the pad.  SendInput
        # queues native events, but restoring the pointer immediately can move
        # it away before the QAction receives the release.  Chrome runs in a
        # separate process, so the previous immediate restore worked there.
        top_levels = getattr(QApplication, 'topLevelWidgets', None)
        own_menu_at_tip = (callable(top_levels) and any(
            isinstance(widget, QMenu) and widget.isVisible()
            and widget.frameGeometry().contains(target)
            for widget in top_levels()))

        self._native_warp_guard = True
        restore_deferred = False
        try:
            from mouse_pointer_rod_windows import click_at
            if own_menu_at_tip:
                # Keep the OS cursor at the QAction briefly while Qt processes
                # WM_LBUTTONDOWN/UP. This is a nonblocking timer, not sleep() on
                # the GUI thread. Leave the cursor alone if the user moved it.
                def restore_after_menu_click(original, clicked_tip):
                    def finish():
                        try:
                            from mouse_pointer_rod_windows import restore_cursor_if_unchanged
                            restore_cursor_if_unchanged(QCursor, original, clicked_tip)
                        finally:
                            self._finish_native_warp()
                    QTimer.singleShot(70, finish)
                restore_deferred = True
                click_at(target, cursor=QCursor, double=(action == 'double'),
                         defer_restore=restore_after_menu_click)
            else:
                # Windows apps and normal Launch widgets retain the tested
                # immediate cursor-restoration behavior of v0.2.
                click_at(target, cursor=QCursor, double=(action == 'double'))
            return True
        except OSError as exc:
            # Native input can be blocked (elevated app, Citrix, locked desktop).
            footer = getattr(launcher, 'footer', None)
            if footer is not None:
                footer.setText(f'Windowsマウス方式：クリック失敗: {exc}')
            return False
        finally:
            if not restore_deferred:
                QTimer.singleShot(85, self._finish_native_warp)

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
                if getattr(self, '_windows_click_mode', False):
                    if self._double_pending:
                        self._cancel_pending_native_click()
                        self._dispatch_tip_action('double')
                    else:
                        self._queue_native_single_click()
                else:
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
            if getattr(self, '_windows_click_mode', False):
                self._cancel_pending_native_click()
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
        self._update_windows_watchdog()
        if self._enabled:
            self._foreground_watchdog.start()
        QTimer.singleShot(0, self._sync_hover)

    def hideEvent(self, event):
        self._cancel_pending_native_click()
        self._native_hover_watchdog.stop()
        self._foreground_watchdog.stop()
        self._native_warp_guard = False
        self._smart_expected_cursor = None
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
            # The real green origin is a transparent child above ぐりぐり.
            # Paint a fallback dot only for standalone/no-marker previews.
            if self._origin_marker is None:
                x, y = self.origin_local()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor('#6aa94a'))
                painter.drawEllipse(QPointF(x, y), 11.0, 11.0)
            # Same compact 10px glyph height as the '1の手' shuriken caption.
            font = QFont('Yu Gothic UI', 9)
            font.setPixelSize(10)
            painter.setFont(font)
            painter.setPen(QColor('#365d53' if is_light else '#d9eee3'))
            painter.drawText(QRectF(6, 5, self.width() - 12, 12),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             'ワープ差し棒 ～ぐりぐりスピナー～' if self._smart_mode else 'マウス差し棒')
            painter.drawText(QRectF(6, 19, self.width() - 12, 12),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f'長さ：{round(self._length)} px')
            # Single line stays ABOVE the centered ぐりぐり button.
            painter.drawText(QRectF(6, 33, self.width() - 12, 12),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f'通常：{NORMAL_WHEEL_STEP_PX}px / 押下：{FAST_WHEEL_STEP_PX}px')
            if self._windows_click_mode:
                painter.setPen(QColor('#1765a8' if is_light else '#91c9ff'))
                painter.drawText(QRectF(6, 47, self.width() - 12, 12),
                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                                 'Windowsマウス方式 ON')
        finally:
            painter.end()
