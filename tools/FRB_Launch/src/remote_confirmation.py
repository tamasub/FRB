"""Remote-operable yes/no confirmations for FRB Launch.

A native modal QMessageBox blocks clicks on the separate non-activating Remote
Qt.Tool window. Use a visible *nonmodal* QMessageBox and a synchronous local
QEventLoop, with an application input guard so no background Launch action can
run while an answer is pending. No SendKeys, focus stealing, or auto-approval.
"""
from time import monotonic

from PySide6.QtCore import QObject, QEvent, QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


class ConfirmationInputGuard(QObject):
    """Give active confirmation exclusive input, including real mouse clicks.

    A confirmation can cover both the Files List item and the Remote pad.
    The dialog surface itself must accept wheel selection and the following
    deliberate left click. The same gate also handles the List and Remote pad.
    No right-click, opening-menu release, drag, or unselected List click can
    confirm a potentially destructive operation.
    """

    BLOCKED = (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
               QEvent.Type.MouseButtonDblClick, QEvent.Type.Wheel,
               QEvent.Type.ContextMenu, QEvent.Type.KeyPress,
               QEvent.Type.KeyRelease, QEvent.Type.ShortcutOverride)
    CLICK_OPEN_GRACE_SECONDS = .25
    CLICK_MAX_DRIFT_PX = 6
    CLICK_MAX_HOLD_SECONDS = 1.5

    def __init__(self, question, remote, wheel_receiver=None):
        super().__init__(question)
        self.question = question
        self.remote = remote
        self.wheel_receiver = wheel_receiver
        self._opened_at = monotonic()
        self._click_press = None

    def _files_list_object(self, obj):
        """Only the actual Files List viewport/tree, not every Launch widget."""
        receiver = self.wheel_receiver
        launcher = getattr(receiver, 'launcher', None)
        view = getattr(launcher, 'expanded_view', None)
        if getattr(view, '_workspace_mode', None) != 'files':
            return False
        tree = getattr(getattr(view, 'middle', None), 'tree', None)
        if tree is None:
            return False
        return obj is tree or obj is tree.viewport()

    def _list_click_armed(self):
        """Background-surface clicks require an explicit selection first."""
        receiver = self.wheel_receiver
        return bool(getattr(receiver, 'remote_has_selected', False)
                    or getattr(receiver, '_explicit_choice', False))

    @staticmethod
    def _left_button(event):
        try:
            return event.button() == Qt.MouseButton.LeftButton
        except (AttributeError, TypeError):
            return False

    @staticmethod
    def _point(event):
        try:
            return event.globalPosition().toPoint()
        except (AttributeError, TypeError):
            try:
                return event.position().toPoint()
            except (AttributeError, TypeError):
                return None

    @staticmethod
    def _within_click_slop(first, last, tolerance):
        if first is None or last is None:
            return True
        try:
            return (last - first).manhattanLength() <= tolerance
        except (TypeError, AttributeError):
            return first == last

    def _native_dialog_control(self, obj):
        """Keep real Yes/No buttons and text editors normally clickable.

        The common input guard also serves Git's editable message prompt.
        A click inside its QLineEdit must NEVER be treated as confirmation.
        Check Qt ancestry because the event target can be an editor viewport.
        A generic QAbstractScrollArea is NOT an editor: Qt can wrap a long
        QMessageBox message in a scroll area. It must remain clickable after
        a wheel selection, without moving the cursor outside the dialog.
        """
        current = obj
        while current is not None:
            try:
                if any(current.inherits(name) for name in (
                        'QAbstractButton', 'QLineEdit', 'QTextEdit',
                        'QPlainTextEdit', 'QAbstractSlider', 'QComboBox')):
                    return True
            except (AttributeError, RuntimeError, TypeError):
                pass
            if current is self.question:
                break
            parent = getattr(current, 'parentWidget', None)
            current = parent() if callable(parent) else None
        return False

    def _click_event(self, source, obj, event):
        """Consume a complete, fresh, left-button click exactly once."""
        kind = event.type()
        if kind == QEvent.Type.MouseButtonDblClick:
            self._click_press = None
        elif kind == QEvent.Type.MouseButtonPress:
            self._click_press = None
            if (self._left_button(event)
                    and monotonic() - self._opened_at >= self.CLICK_OPEN_GRACE_SECONDS):
                self._click_press = (source, obj, self._point(event), monotonic())
        elif kind == QEvent.Type.MouseButtonRelease:
            pending = self._click_press
            self._click_press = None
            # The contents of a long QMessageBox can be split into several
            # Qt child widgets (labels, text containers, the box itself).
            # Qt may deliver Press and Release to different children even when
            # the pointer stays at the same screen coordinate. Identity of a
            # *child* is not part of the user's click intent. For a dialog,
            # both events have already been verified as belonging to this one
            # question window by eventFilter(). Keep the strict same-widget
            # rule for the Remote pad and the Files List.
            same_target = (pending is not None and
                           (pending[1] is obj if source != 'dialog' else True))
            if (pending is not None and pending[0] == source and same_target
                    and self._left_button(event)
                    and monotonic() - pending[3] <= self.CLICK_MAX_HOLD_SECONDS
                    and self._within_click_slop(
                        pending[2], self._point(event), self.CLICK_MAX_DRIFT_PX)
                    and (source == 'pad' or self._list_click_armed())):
                receiver = self.wheel_receiver
                if receiver is not None:
                    receiver.remote_command('CLICK')
        event.accept()
        return True

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind not in self.BLOCKED or not isinstance(obj, QWidget):
            return False
        window = obj.window()
        # Native combobox lists are separate Qt.Popup windows.  They still
        # belong to the editable dialog, not to the blocked background Launch
        # surface.  The icon chooser must allow both clicking the dropdown and
        # selecting its popup row; the Remote button selector is unaffected.
        try:
            for combo in (widget for widget in self.question.findChildren(QWidget)
                          if widget.inherits('QComboBox')):
                if combo.view().isVisible() and window is combo.view().window():
                    return False
        except (AttributeError, RuntimeError):
            pass
        pad = getattr(self.remote, 'pad', None)
        # QApplication-level filter runs before the pad's QWidget handler.
        # Consume BOTH press/release here and dispatch only once, rather than
        # depending on a non-activating Tool window's native clicked signal.
        if obj is pad and kind in (QEvent.Type.MouseButtonPress,
                                   QEvent.Type.MouseButtonRelease,
                                   QEvent.Type.MouseButtonDblClick):
            return self._click_event('pad', obj, event)
        if window is self.question:
            if self.wheel_receiver is None:
                return False  # Keep native dialog behavior without a Remote.
            # Git confirmation is a separate top-level window. On Windows it
            # often covers both the original Files List and the Remote pad.
            # Events received *on the question itself* must therefore be a
            # first-class input route, not handed to a passive QMessageBox.
            if kind == QEvent.Type.Wheel and self._native_dialog_control(obj):
                return False  # Icon combobox/description editor keep native wheel.
            if kind == QEvent.Type.Wheel and self.wheel_receiver is not None:
                self._click_press = None  # Wheel-during-press cannot arm a click.
                self.wheel_receiver.background_wheel(event)
                event.accept()
                return True
            if kind in (QEvent.Type.MouseButtonPress,
                        QEvent.Type.MouseButtonRelease,
                        QEvent.Type.MouseButtonDblClick):
                if self._native_dialog_control(obj):
                    # A native button/editor gets the entire click; never
                    # reinterpret its trailing Release as a dialog-surface
                    # confirmation, even if a previous Press was armed.
                    self._click_press = None
                    return False
                # A long QMessageBox may send Press and Release to different
                # label/viewport children. Both are on this same question
                # window; the screen-coordinate movement tolerance is still
                # checked before an explicit choice can be confirmed.
                return self._click_event('dialog', obj, event)
            return False
        if self.remote is not None and window is self.remote:
            return False  # Preserve normal Remote wheel and other controls.
        list_target = self._files_list_object(obj)
        if kind == QEvent.Type.Wheel and self.wheel_receiver is not None:
            # Wheel over the original List changes only the confirmation.
            self.wheel_receiver.background_wheel(event)
        elif list_target and kind in (QEvent.Type.MouseButtonPress,
                                     QEvent.Type.MouseButtonRelease,
                                     QEvent.Type.MouseButtonDblClick):
            return self._click_event('list', obj, event)
        elif kind in (QEvent.Type.MouseButtonPress,
                     QEvent.Type.MouseButtonRelease,
                     QEvent.Type.MouseButtonDblClick):
            self._click_press = None
        event.accept()
        return True


class RemoteConfirmation:
    """UI selection and Remote dispatch for a single safety-critical question."""

    YES = QMessageBox.StandardButton.Yes
    NO = QMessageBox.StandardButton.No

    def __init__(self, launcher, title, message, informative='', *,
                 yes_text=None, no_text=None, rich_text=False,
                 warning=False, information=False):
        self.launcher = launcher
        self.dialog = QMessageBox(launcher)
        icon = (QMessageBox.Icon.Warning if warning else
                QMessageBox.Icon.Information if information else
                QMessageBox.Icon.Question)
        self.dialog.setIcon(icon)
        self.dialog.setWindowTitle(str(title))
        if rich_text:
            self.dialog.setTextFormat(Qt.TextFormat.RichText)
        self.dialog.setText(str(message))
        if informative:
            self.dialog.setInformativeText(str(informative))
        self.dialog.setStandardButtons(self.YES | self.NO)
        if yes_text is not None:
            self.dialog.button(self.YES).setText(yes_text)
        if no_text is not None:
            self.dialog.button(self.NO).setText(no_text)
        self.yes_text = self.dialog.button(self.YES).text()
        self.no_text = self.dialog.button(self.NO).text()
        self.dialog.setDefaultButton(self.NO)
        self.dialog.setEscapeButton(self.NO)
        # Critical: Qt.WindowModal would block the separate Remote as a child
        # tool window of the Launcher, even with WindowDoesNotAcceptFocus.
        self.dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.dialog.setModal(False)
        self.selected = self.NO
        self._background_wheel_angle = 0
        self._background_wheel_pixel = 0
        self._explicit_choice = False

    def background_wheel(self, event):
        """Wheel over the originating List selects No/Yes, never the List."""
        angle = event.angleDelta().y()
        pixel = event.pixelDelta().y()
        if angle:
            self._background_wheel_angle += angle
            steps = int(self._background_wheel_angle / 120)
            self._background_wheel_angle -= steps * 120
        else:
            self._background_wheel_pixel += pixel
            steps = int(self._background_wheel_pixel / 36)
            self._background_wheel_pixel -= steps * 36
        for _ in range(min(abs(steps), 5)):
            self.remote_command('UP' if steps > 0 else 'DOWN')

    # Do not rely on the Windows "hide focus indicators until keyboard input"
    # setting. The Remote is a separate non-activating Tool window: Qt may
    # update focusWidget() correctly without painting a native focus rectangle.
    # Draw the active button's focus border *on the actual QMessageBox button*.
    # The other button retains its normal platform appearance.
    FOCUS_BUTTON_STYLE = (
        'QPushButton {'
        ' border: 2px solid #27865D;'
        ' border-radius: 5px;'
        ' padding: 5px 14px;'
        ' background-color: #EAF7EF;'
        ' color: #17472F;'
        ' font-weight: 600;'
        '}'
        'QPushButton:pressed { background-color: #D1EAD9; }'
    )

    def choose(self, answer):
        """Move both Qt keyboard focus and a visible border on the dialog itself."""
        if answer not in (self.YES, self.NO):
            return
        self.selected = answer
        for candidate in (self.NO, self.YES):
            button = self.dialog.button(candidate)
            if button is None:
                continue
            button.setStyleSheet(self.FOCUS_BUTTON_STYLE if candidate == answer else '')
            if candidate == answer:
                self.dialog.setDefaultButton(button)
                button.setFocus(Qt.FocusReason.TabFocusReason)
                button.update()
        # A translucent Remote needs a clear, local indication that its wheel
        # currently controls an answer rather than the Files list.
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        if label is not None and remote.isVisible():
            label.setText('確認応答：' + (getattr(self, 'yes_text', 'Yes') if answer == self.YES else getattr(self, 'no_text', 'No')))

    def remote_command(self, command):
        if command in ('UP', 'DOWN'):
            self._explicit_choice = True
            self.choose(self.YES if self.selected == self.NO else self.NO)
        elif command == 'LEFT':
            self._explicit_choice = True
            self.choose(self.NO)
        elif command == 'RIGHT':
            self._explicit_choice = True
            self.choose(self.YES)
        elif command in ('CLICK', 'ENTER'):
            # Use the real QMessageBox button. Its clicked() path owns the
            # result, exactly like the user pressing it with the mouse.
            button = self.dialog.button(self.selected)
            if button is not None:
                button.click()
        elif command == 'CLOSE':
            # Closing the Remote while a question is active is always No.
            button = self.dialog.button(self.NO)
            if button is not None:
                button.click()
        # Never let any Remote action reach the background while confirmation
        # is visible, even if it is not one of the navigation commands.
        return True

    def ask(self):
        loop = QEventLoop(self.dialog)
        self.dialog.finished.connect(loop.quit)
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        previous_area_text = label.text() if label is not None else None
        guard = ConfirmationInputGuard(self.dialog, remote, self)
        application = QApplication.instance()
        application.installEventFilter(guard)
        try:
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()  # Give the question real keyboard focus.
            self.choose(self.NO)
            # Reassert after the native show/layout passes, which can reset
            # QMessageBox's initially focused default button on Windows.
            QTimer.singleShot(0, lambda: self.choose(self.NO)
                              if self.dialog.isVisible() and self.selected == self.NO
                              else None)
            # Non-activating Remote remains clickable in front of the question.
            if remote is not None and remote.isVisible():
                QTimer.singleShot(0, remote.raise_)
            loop.exec()
            result = self.dialog.result()
            return self.YES if result == int(self.YES) else self.NO
        finally:
            application.removeEventFilter(guard)
            if previous_area_text is not None:
                try:
                    label.setText(previous_area_text)
                except RuntimeError:
                    pass  # Remote was destroyed while the question was open.
            self.dialog.hide()
            self.dialog.deleteLater()
