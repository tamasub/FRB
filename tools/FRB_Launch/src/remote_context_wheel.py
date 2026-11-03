"""Opt-in wheel-pad control of a *real* Qt filesystem context menu.

Only menus opened from the Files List Remote are connected.  QMenu's popup
mouse grab can deliver events addressed to the pad *to the menu instead*;
filtering at QApplication level by global cursor position bridges that gap.
Normal pointer-based menus retain their native behaviour.  No SendKeys and
no alternate filesystem action implementation: a selected QAction is triggered.
"""

from PySide6.QtCore import QObject, QEvent, QTimer, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication


def selectable_actions(menu):
    """Walk only visible, enabled items, skipping headers/separators."""
    return [action for action in menu.actions()
            if action.isVisible() and action.isEnabled() and not action.isSeparator()]


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
        self._previous_label = None
        remote = getattr(launcher, 'remote_window', None)
        if remote is not None:
            label = getattr(remote, 'area_label', None)
            self._previous_label = label.text() if label is not None else None
            if label is not None:
                label.setText('操作先：コンテキストメニュー')
        self.root.aboutToHide.connect(self.stop)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        # QMenu::popup can reset its active action during the native show.
        QTimer.singleShot(0, self._select_first)

    def _select_first(self):
        if self.active and self.current.isVisible():
            items = selectable_actions(self.current)
            if not items:
                return
            current = (self._selected if self._selected in items else
                       self.current.activeAction())
            self._selected = current if current in items else items[0]
            self.current.setActiveAction(self._selected)

    def _hit(self, global_pos):
        """Recognize only pad and its adjacent arrow buttons, not the whole Remote."""
        remote = getattr(self.launcher, 'remote_window', None)
        if remote is None or not remote.isVisible():
            return None
        for name, widget in (('CLICK', getattr(remote, 'pad', None)),
                             ('LEFT', getattr(remote, 'left_button', None)),
                             ('RIGHT', getattr(remote, 'right_button', None))):
            if widget is not None and widget.isVisible():
                if widget.rect().contains(widget.mapFromGlobal(global_pos)):
                    return name
        return None

    def eventFilter(self, obj, event):
        if not self.active or not self.root.isVisible():
            return False
        kind = event.type()
        if kind not in (QEvent.Type.Wheel, QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick):
            return False
        # This also works when native popup grabs redirect the event to QMenu.
        try:
            point = event.globalPosition().toPoint()
        except AttributeError:
            point = QCursor.pos()
        hit = self._hit(point)
        if hit is None:
            return False  # Never interfere with regular QMenu mouse usage.
        if kind == QEvent.Type.Wheel:
            remote = self.launcher.remote_window
            # Reuse the pad's existing wheel-step/pixel accumulation and Ctrl
            # opacity handling; it emits the ordinary UP/DOWN commands.
            remote.pad.wheelEvent(event)
            event.accept()
            return True
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
            self._select_first()
        if name in ('UP', 'DOWN'):
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
                    submenu.popup(point)
                    self.current = submenu
                    self._selected = None
                    QTimer.singleShot(0, self._select_first)
                return True
            if name == 'RIGHT':
                return True  # Right only opens a submenu, never executes a leaf.
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
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
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
