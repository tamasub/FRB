"""Remote-operable yes/no confirmations for FRB Launch.

A native modal QMessageBox blocks clicks on the separate non-activating Remote
Qt.Tool window. Use a visible *nonmodal* QMessageBox and a synchronous local
QEventLoop, with an application input guard so no background Launch action can
run while an answer is pending. No SendKeys, focus stealing, or auto-approval.
"""
from PySide6.QtCore import QObject, QEvent, QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


class ConfirmationInputGuard(QObject):
    """Allow only the question and Remote to receive user input."""

    BLOCKED = (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
               QEvent.Type.MouseButtonDblClick, QEvent.Type.Wheel,
               QEvent.Type.ContextMenu, QEvent.Type.KeyPress,
               QEvent.Type.KeyRelease, QEvent.Type.ShortcutOverride)

    def __init__(self, question, remote):
        super().__init__(question)
        self.question = question
        self.remote = remote

    def eventFilter(self, obj, event):
        if event.type() not in self.BLOCKED or not isinstance(obj, QWidget):
            return False
        window = obj.window()
        if window is self.question or (self.remote is not None and window is self.remote):
            return False
        event.accept()
        return True


class RemoteConfirmation:
    """UI selection and Remote dispatch for a single safety-critical question."""

    YES = QMessageBox.StandardButton.Yes
    NO = QMessageBox.StandardButton.No

    def __init__(self, launcher, title, message, informative=''):
        self.launcher = launcher
        self.dialog = QMessageBox(launcher)
        self.dialog.setIcon(QMessageBox.Icon.Question)
        self.dialog.setWindowTitle(str(title))
        self.dialog.setText(str(message))
        if informative:
            self.dialog.setInformativeText(str(informative))
        self.dialog.setStandardButtons(self.YES | self.NO)
        self.dialog.setDefaultButton(self.NO)
        self.dialog.setEscapeButton(self.NO)
        # Critical: Qt.WindowModal would block the separate Remote as a child
        # tool window of the Launcher, even with WindowDoesNotAcceptFocus.
        self.dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.dialog.setModal(False)
        self.selected = self.NO

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
            label.setText('確認応答：' + ('Yes' if answer == self.YES else 'No'))

    def remote_command(self, command):
        if command in ('UP', 'DOWN'):
            self.choose(self.YES if self.selected == self.NO else self.NO)
        elif command == 'LEFT':
            self.choose(self.NO)
        elif command == 'RIGHT':
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
        guard = ConfirmationInputGuard(self.dialog, remote)
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
