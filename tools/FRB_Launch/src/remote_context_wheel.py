"""Hybrid wheel-pad control of a *real* Qt context menu.

Pointer-opened and Remote-opened QMenus share the same QAction cursor.
A wheel on the Remote pad OR over the open context menu (where right-click
left the pointer) changes the highlighted action. Ordinary mouse clicks on
the menu remain native. No transparent hit target, SendKeys or duplicated
filesystem implementation is required.
"""

from PySide6.QtCore import QObject, QEvent, QTimer, Qt
try:
    from PySide6.QtCore import QAbstractNativeEventFilter
except ImportError:  # Qt-free test doubles may not expose this optional class.
    QAbstractNativeEventFilter = object
import os
import ctypes
from ctypes import wintypes
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication
try:
    from PySide6.QtWidgets import QMenu
except ImportError:  # Legacy Qt-free test doubles do not always expose QMenu.
    class QMenu:
        pass


def selectable_actions(menu):
    """Walk only visible, enabled items, skipping headers/separators."""
    return [action for action in menu.actions()
            if action.isVisible() and action.isEnabled() and not action.isSeparator()]


class _NativePopupWheel(QAbstractNativeEventFilter):
    """Win32 fallback for QMenu mouse grabs which bypass Qt Wheel events.

    Only intercept WM_MOUSEWHEEL delivered to this process when the pointer
    is on the Remote pad OR the visible context menu / original right-click
    point. The latter lets users turn the wheel without moving to Remote.
    No system-wide hook, no key simulation and no off-menu input hijacking.
    """
    WM_MOUSEWHEEL = 0x020A

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.remainder = 0

    def nativeEventFilter(self, event_type, message):
        owner = self.controller
        if not owner.active or not owner.root.isVisible() or os.name != 'nt':
            return False, 0
        try:
            msg = wintypes.MSG.from_address(int(message))
        except (TypeError, ValueError, OSError):
            return False, 0
        if (msg.message != self.WM_MOUSEWHEEL
                or owner._wheel_target(QCursor.pos()) is None):
            return False, 0
        delta = ctypes.c_short((int(msg.wParam) >> 16) & 0xffff).value
        self.remainder += delta
        steps = int(self.remainder / 120)
        self.remainder -= steps * 120
        # Consume the native message even for partial high-resolution wheels;
        # Qt must not also move the underlying Files List or popup viewport.
        for _ in range(min(abs(steps), 5)):
            owner.command('UP' if steps > 0 else 'DOWN')
        return True, 0


class RemoteContextWheel(QObject):
    """Short-lived adapter: Remote wheel/arrows/● -> existing QAction cursor."""

    def __init__(self, launcher, menu):
        super().__init__(launcher)
        self.launcher = launcher
        self.root = menu
        self.current = menu
        self.active = True
        self._selected = None  # Stable even if native popup hover clears activeAction.
        self._parent_action = None
        self._mouse_down = None
        self._wheel_menu_mouse_down = False
        self._previous_label = None
        # The context menu is not guaranteed to cover the exact click point
        # (screen-edge repositioning). Keep a tiny, popup-lifetime hit zone.
        self._popup_anchor = QCursor.pos()
        # After wheel navigation starts, Qt can keep selecting the QAction
        # under the *stationary* mouse pointer (often "新規作成"), which opens
        # its submenu and steals the wheel cursor.  While that pointer does
        # not physically move, the wheel/keyboard cursor owns selection.
        self._wheel_owned_selection = False
        self._wheel_pointer_origin = None
        self._explicit_submenu = None
        self._hover_guard_connections = []
        self._hover_guard_menu_ids = set()
        self._menu_wheel_angle_remainder = 0
        self._menu_wheel_pixel_remainder = 0
        remote = getattr(launcher, 'remote_window', None)
        if remote is not None:
            label = getattr(remote, 'area_label', None)
            self._previous_label = label.text() if label is not None else None
            if label is not None:
                label.setText('操作先：コンテキストメニュー')
        self.root.aboutToHide.connect(self.stop)
        self._install_hover_guards()
        app = QApplication.instance()
        self._native_wheel = None
        if app is not None:
            app.installEventFilter(self)
            if os.name == 'nt' and QAbstractNativeEventFilter is not object:
                self._native_wheel = _NativePopupWheel(self)
                app.installNativeEventFilter(self._native_wheel)
        # QMenu::popup can reset its active action during the native show.
        QTimer.singleShot(0, self._select_first)

    def _select_first(self):
        if self.active and self.current.isVisible():
            items = selectable_actions(self.current)
            if not items:
                return
            # A Files Exp folder can request 戻る as its initial cursor.
            # Prefer it to Qt's native hover selection (often Filesリスト),
            # but never override a selection already moved by the user.
            if self._selected in items:
                current = self._selected
            else:
                preferred = (getattr(self.root, '_remote_pad_initial_action', None)
                             if self.current is self.root else None)
                # A pointer-opened menu must also begin on its first
                # selectable row. Never inherit the incidental Qt hover item.
                current = preferred if preferred in items else items[0]
            self._selected = current if current in items else items[0]
            self.current.setActiveAction(self._selected)

    @staticmethod
    def _pointer_moved(first, current, tolerance=3):
        """Only a *physical* pointer move gives Qt mouse hover ownership.

        The Qt QPoint objects have manhattanLength(); string test doubles
        intentionally use the equality fallback.  No timer-based guesswork.
        """
        try:
            return (current - first).manhattanLength() > tolerance
        except (TypeError, AttributeError):
            return first != current

    def _pointer_still_owned_by_wheel(self):
        if not self._wheel_owned_selection:
            return False
        if self._pointer_moved(self._wheel_pointer_origin, QCursor.pos()):
            self._wheel_owned_selection = False
            self._explicit_submenu = None
            return False
        return True

    def _connect_guard(self, signal, callback):
        signal.connect(callback)
        self._hover_guard_connections.append((signal, callback))

    def _install_hover_guards(self):
        """Listen to Qt's native hover & submenu-open signals, too.

        Blocking synthetic MouseMove alone is insufficient: QMenu can reopen
        a submenu from an already scheduled hover timer.  Connections are
        removed on stop because the Settings QMenu is a persistent widget.
        """
        try:
            menus = [self.root, *self.root.findChildren(QMenu)]
        except (AttributeError, RuntimeError):
            menus = [self.root]
        for menu in menus:
            if id(menu) in self._hover_guard_menu_ids:
                continue
            self._hover_guard_menu_ids.add(id(menu))
            hovered = getattr(menu, 'hovered', None)
            if hovered is not None:
                self._connect_guard(
                    hovered, lambda action, m=menu: self._native_hover(m, action))
            if menu is not self.root:
                about_to_show = getattr(menu, 'aboutToShow', None)
                if about_to_show is not None:
                    self._connect_guard(
                        about_to_show, lambda m=menu: self._native_submenu_open(m))

    def _begin_wheel_selection(self):
        self._install_hover_guards()
        if not self._wheel_owned_selection:
            self._wheel_pointer_origin = QCursor.pos()
            self._wheel_owned_selection = True
        # A submenu opened by an earlier stationary hover is not an explicit
        # RIGHT/ENTER request. Close it before processing the wheel step.
        if self.current is self.root:
            self._explicit_submenu = None
            for submenu in self.root.findChildren(QMenu):
                if submenu.isVisible():
                    submenu.close()

    def _restore_wheel_selection(self):
        if (not self.active or not self._pointer_still_owned_by_wheel()
                or not self.current.isVisible()):
            return
        actions = selectable_actions(self.current)
        if self._selected in actions and self.current.activeAction() is not self._selected:
            self.current.setActiveAction(self._selected)

    def _native_hover(self, menu, action):
        # Qt may emit hovered even when the mouse has NOT moved (e.g. after a
        # programmatic setActiveAction or popup reposition). A true mouse move
        # releases ownership and restores normal hover/click submenu use.
        if (self.active and menu is self.current and
                self._pointer_still_owned_by_wheel() and
                action is not self._selected):
            QTimer.singleShot(0, self._restore_wheel_selection)

    def _native_submenu_open(self, submenu):
        if (not self.active or not self._pointer_still_owned_by_wheel()
                or submenu is self._explicit_submenu):
            return
        # aboutToShow is emitted before QMenu actually becomes visible.
        # Closing on the next event tick avoids reopening on stale hover.
        QTimer.singleShot(0, lambda m=submenu: self._close_hover_submenu(m))

    def _close_hover_submenu(self, submenu):
        if (self.active and self._pointer_still_owned_by_wheel() and
                submenu is not self._explicit_submenu):
            if submenu.isVisible():
                submenu.close()
            self._restore_wheel_selection()

    def _hit(self, global_pos):
        """Recognize only the ぐりぐり pad; the arrow buttons were retired."""
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is None or not remote.isVisible():
            return None
        for name, widget in (('CLICK', getattr(remote, 'pad', None)),):
            if widget is not None and widget.isVisible():
                if widget.rect().contains(widget.mapFromGlobal(global_pos)):
                    return name
        return None

    def _menu_under_pointer(self, global_pos):
        """True for the visible QMenu surface or its opening click position.

        This is the missing half of hybrid wheel control: the old adapter
        recognized ONLY the Remote pad, requiring a pointless cursor trip.
        Keep native clicks unchanged; only wheel input uses this test.
        """
        if not self.root.isVisible():
            return False
        menus = [self.root]
        if self.current is not self.root:
            menus.append(self.current)
        try:
            from PySide6.QtWidgets import QMenu
            menus.extend(self.root.findChildren(QMenu))
        except (AttributeError, ImportError, RuntimeError):
            pass
        for menu in menus:
            try:
                if menu.isVisible() and menu.frameGeometry().contains(global_pos):
                    return True
            except (AttributeError, RuntimeError, TypeError):
                continue
        # On the bottom/right edge Qt may place the popup BESIDE the click.
        # This small radius does not capture unrelated Files scrolling.
        anchor = self._popup_anchor
        try:
            return (global_pos - anchor).manhattanLength() <= 18
        except (AttributeError, TypeError):
            return False

    def _wheel_target(self, global_pos):
        """Capture only wheel gestures belonging to an open hybrid menu."""
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is None or not remote.isVisible() or not self.root.isVisible():
            return None
        if self._hit(global_pos) is not None:
            return 'pad'
        if self._menu_under_pointer(global_pos):
            return 'menu'
        return None

    def _consume_menu_wheel(self, event):
        """Move the *same* action cursor as the Remote pad, not QMenu scroll."""
        angle = event.angleDelta().y()
        pixel = event.pixelDelta().y()
        if angle:
            self._menu_wheel_angle_remainder += angle
            steps = int(self._menu_wheel_angle_remainder / 120)
            self._menu_wheel_angle_remainder -= steps * 120
        else:
            self._menu_wheel_pixel_remainder += pixel
            steps = int(self._menu_wheel_pixel_remainder / 36)
            self._menu_wheel_pixel_remainder -= steps * 36
        for _ in range(min(abs(steps), 5)):
            self.command('UP' if steps > 0 else 'DOWN')
        event.accept()

    def eventFilter(self, obj, event):
        if not self.active or not self.root.isVisible():
            return False
        kind = event.type()
        # QMenu can receive synthesized hover/move events without physical
        # cursor motion after a wheel-driven selection. Ignore only those;
        # moving the pointer >3px restores normal native mouse behavior.
        pointer_event_types = tuple(
            value for value in (
                getattr(QEvent.Type, 'MouseMove', None),
                getattr(QEvent.Type, 'HoverMove', None),
                getattr(QEvent.Type, 'Enter', None),
                getattr(QEvent.Type, 'HoverEnter', None)) if value is not None)
        if (kind in pointer_event_types and isinstance(obj, QMenu)
                and self._pointer_still_owned_by_wheel()):
            event.accept()
            return True
        # When a user has moved the QAction cursor by wheel without moving the
        # physical pointer, a left click at the original context-menu position
        # must activate the *highlighted action*, not Qt's stale hovered row.
        # This reuses the exact CLICK command already used by the Remote pad,
        # including explicit submenu entry. Actual pointer movement gives
        # native mouse hit testing back its normal ownership.
        if (getattr(self, '_wheel_owned_selection', False)
                or getattr(self, '_wheel_menu_mouse_down', False)) and kind in (
                    QEvent.Type.MouseButtonPress,
                    QEvent.Type.MouseButtonRelease,
                    QEvent.Type.MouseButtonDblClick):
            if event.button() == Qt.MouseButton.LeftButton:
                over_wheel_menu = (self._pointer_still_owned_by_wheel()
                                   and self._menu_under_pointer(QCursor.pos()))
                if kind == QEvent.Type.MouseButtonPress:
                    self._wheel_menu_mouse_down = bool(over_wheel_menu)
                    if over_wheel_menu:
                        event.accept()
                        return True
                elif kind == QEvent.Type.MouseButtonDblClick and over_wheel_menu:
                    # One deliberate wheel-selection click is sufficient;
                    # Qt's second native click must not hit a stale row.
                    self._wheel_menu_mouse_down = False
                    event.accept()
                    return True
                elif self._wheel_menu_mouse_down:
                    self._wheel_menu_mouse_down = False
                    if over_wheel_menu and kind == QEvent.Type.MouseButtonRelease:
                        self.command('CLICK')
                    # Do not allow a duplicate native click or double-click.
                    event.accept()
                    return True
            elif kind == QEvent.Type.MouseButtonPress:
                self._wheel_menu_mouse_down = False

        # A non-grabbing Tool menu deliberately leaves the Remote pad usable.
        # Restore the native popup's expected outside-click dismissal without
        # consuming that click. Deactivation also closes orphaned menus.
        if getattr(self.root, '_frb_non_grabbing', False):
            if kind == getattr(QEvent.Type, 'ApplicationDeactivate', None):
                self.root.close()
                return False
            if kind == QEvent.Type.MouseButtonPress:
                try:
                    point = event.globalPosition().toPoint()
                except (AttributeError, TypeError):
                    point = QCursor.pos()
                # Native Qt might report a popup-relative event point. Do
                # not dismiss when either location actually hits the pad.
                if self._hit(QCursor.pos()) is None and self._hit(point) is None:
                    open_menus = [self.root]
                    for submenu in self.root.findChildren(QMenu):
                        if submenu.isVisible():
                            open_menus.append(submenu)
                    if not any(m.frameGeometry().contains(point) for m in open_menus):
                        self.root.close()
                        return False
        if kind not in (QEvent.Type.Wheel, QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick):
            return False
        # QMenu receives the wheel when the pointer stays at the right-click
        # site; Remote receives it when the pointer moves over its pad.
        # Both must drive ONE QAction selection cursor.  Keep regular mouse
        # clicks on the menu under Qt's native hit testing.
        point = QCursor.pos()
        if kind == QEvent.Type.Wheel:
            target = self._wheel_target(point)
            if target is None:
                try:
                    target = self._wheel_target(event.globalPosition().toPoint())
                except (AttributeError, TypeError):
                    pass
            if target == 'menu':
                self._consume_menu_wheel(event)
                return True
            if target == 'pad':
                # The pad retains its own Ctrl-opacity and accumulation rules.
                self.launcher.remote_window.pad.wheelEvent(event)
                event.accept()
                return True
            return False
        hit = self._hit(point)
        if hit is None:
            try:
                hit = self._hit(event.globalPosition().toPoint())
            except (AttributeError, TypeError):
                pass
        if hit is None:
            if kind == QEvent.Type.MouseButtonPress:
                # Explicit mouse selection/hover takes back native ownership.
                self._wheel_owned_selection = False
                self._explicit_submenu = None
            return False  # Native menu click, or unrelated pointer input.
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        if kind == QEvent.Type.MouseButtonPress:
            self._mouse_down = hit
        elif kind == QEvent.Type.MouseButtonRelease:
            if self._mouse_down == hit:
                self.command(hit)
            self._mouse_down = None
        else:
            # Native double click is still one intentional menu action.
            self._mouse_down = None
        event.accept()
        return True

    def command(self, name):
        """Return True only for Remote commands owned by the open menu."""
        if not self.active or not self.root.isVisible():
            return False
        # A submenu can be dismissed by a normal pointer action without
        # closing its parent. Do not keep sending input to a hidden child.
        if self.current is not self.root and not self.current.isVisible():
            self.current = self.root
            self._selected = self._parent_action
            self._explicit_submenu = None
            self._select_first()
        if name in ('UP', 'DOWN'):
            self._begin_wheel_selection()
            actions = selectable_actions(self.current)
            if not actions:
                return True
            current = self._selected if self._selected in actions else self.current.activeAction()
            index = actions.index(current) if current in actions else (-1 if name == 'DOWN' else 0)
            self._selected = actions[(index + (1 if name == 'DOWN' else -1)) % len(actions)]
            self.current.setActiveAction(self._selected)
            return True
        if name == 'LEFT':
            if self.current is not self.root:
                self.current.close()
                self.current = self.root
                self._selected = self._parent_action
                self._explicit_submenu = None
                self._select_first()
            else:
                self.root.close()  # Escape without selecting an action.
            return True
        if name in ('RIGHT', 'ENTER', 'CLICK'):
            actions = selectable_actions(self.current)
            action = self._selected if self._selected in actions else self.current.activeAction()
            if action is None or action not in actions:
                return True
            submenu = action.menu()
            if submenu is not None:
                if self.current is self.root:  # One nested level in the prototype.
                    rect = self.current.actionGeometry(action)
                    point = self.current.mapToGlobal(rect.topRight())
                    self._parent_action = action
                    # Explicit RIGHT/ENTER is allowed to open a submenu;
                    # passive hover over the stationary pointer is not.
                    self._explicit_submenu = submenu
                    self._install_hover_guards()
                    submenu.popup(point)
                    self.current = submenu
                    self._selected = None
                    QTimer.singleShot(0, self._select_first)
                return True
            if name == 'RIGHT':
                return True  # Right only opens a submenu, never executes a leaf.
            # RemoteFolderActionsMenu has a bespoke Filesリスト *cascade*
            # opener, not a QMenu submenu.  Keep its root popup alive when
            # selecting this QAction, then return control to the cascade.
            if action in getattr(self.current, 'openers', {}):
                self.stop()
                QTimer.singleShot(0, action.trigger)
                return True
            # Native QMenu can invalidate submenu action wrappers on close.
            # Extract the saved Open With payload while the menu is alive,
            # then call the EXISTING Launch handler once the popup grab ends.
            # Ordinary mouse selection still goes through QAction.triggered.
            payload = action.data() if hasattr(action, 'data') else None
            if (self.current is not self.root and
                    isinstance(payload, (tuple, list)) and payload and
                    payload[0] in ('open_with_app', 'open_with_dialog')):
                operation = payload[0]
                arguments = tuple(payload[1:])
                if ((operation == 'open_with_app' and len(arguments) == 2) or
                        (operation == 'open_with_dialog' and len(arguments) == 1)):
                    self.stop()
                    self.root.close()
                    if operation == 'open_with_app':
                        QTimer.singleShot(0, lambda args=arguments:
                                          self.launcher.open_file_with_selected_app(*args))
                    else:
                        QTimer.singleShot(0, lambda filename=arguments[0]:
                                          self.launcher.perform_filesystem_context_action(
                                              'open_with', filename, 'file'))
                    return True
            # Dismiss popup/grab BEFORE a potentially modal confirmation or
            # inline rename; do not call the filesystem operation ourselves.
            self.stop()
            self.root.close()
            QTimer.singleShot(0, action.trigger)
            return True
        if name in ('CLOSE', 'ESCAPE'):
            self.root.close()
            return True
        if name == 'CONTEXT_MENU':
            self.root.close()
            return True
        # While menu is up, don't route unrelated Remote keys to Files.
        return True

    def stop(self):
        if not self.active:
            return
        self.active = False
        for signal, callback in self._hover_guard_connections:
            try:
                signal.disconnect(callback)
            except (AttributeError, RuntimeError, TypeError):
                pass
        self._hover_guard_connections.clear()
        try:
            self.root.aboutToHide.disconnect(self.stop)
        except (AttributeError, RuntimeError, TypeError):
            pass
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
            if self._native_wheel is not None:
                app.removeNativeEventFilter(self._native_wheel)
                self._native_wheel = None
        if getattr(self.launcher, '_remote_context_wheel', None) is self:
            self.launcher._remote_context_wheel = None
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        if label is not None and self._previous_label is not None:
            try:
                label.setText(self._previous_label)
            except RuntimeError:
                pass
        self.deleteLater()
