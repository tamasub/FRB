"""Remote-assisted text confirmation without taking away keyboard editing.

For Launch-owned QDialogs only: the QLineEdit keeps native focus on open.
Remote wheel/left/right moves a *visible focus frame* on the actual OK/Cancel
QPushButton. Remote centre clicks that actual button. Background input is
blocked, while text entry/ordinary mouse operation remains native.
"""

from PySide6.QtCore import QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialogButtonBox
from remote_confirmation import ConfirmationInputGuard
from dialog_button_selection import DialogButtonSelection


class RemoteTextDialog:
    """Shared ぐりぐり adapter for ANY Launch-owned button dialog.

    Supports text, choices, other editable forms, and a one-button notice.
    A visible Remote is optional; never a condition for installing the guard.
    """

    FOCUS_BUTTON_STYLE = DialogButtonSelection.FOCUS_BUTTON_STYLE

    def __init__(self, launcher, dialog, editor, buttons):
        self.launcher = launcher
        self.dialog = dialog
        self.editor = editor
        # Discover every QDialogButtonBox button. New dialogs need zero
        # per-dialog wheel/Remote wiring, including forms with custom buttons.
        self.buttons = {}
        self._accept_key = None
        self._reject_key = None
        for index, button in enumerate(buttons.buttons()):
            standard = buttons.standardButton(button)
            if standard == QDialogButtonBox.StandardButton.Ok:
                key = 'OK'
            elif standard == QDialogButtonBox.StandardButton.Cancel:
                key = 'Cancel'
            else:
                key = f'Button{index}'
            self.buttons[key] = button
            role = buttons.buttonRole(button)
            if role in (QDialogButtonBox.ButtonRole.AcceptRole,
                        QDialogButtonBox.ButtonRole.YesRole) and self._accept_key is None:
                self._accept_key = key
            if role in (QDialogButtonBox.ButtonRole.RejectRole,
                        QDialogButtonBox.ButtonRole.NoRole) and self._reject_key is None:
                self._reject_key = key
        if not self.buttons:
            raise ValueError('Launch dialog needs a nonempty QDialogButtonBox')
        self._accept_key = self._accept_key or next(iter(self.buttons))
        self._reject_key = self._reject_key or self._accept_key
        self.selected = self._reject_key
        self.selection = DialogButtonSelection(dialog, self.buttons, self.selected)
        # A genuine user wheel selection arms background click-to-confirm.
        self.remote_has_selected = False
        self._background_wheel_angle = 0
        self._background_wheel_pixel = 0

    def background_wheel(self, event):
        """The originating Files List wheel can select OK/Cancel too."""
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

    def choose(self, name):
        if not self.selection.choose(name, focus_reason=Qt.FocusReason.TabFocusReason):
            return
        self.selected = self.selection.selected
        self.remote_has_selected = True
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        if remote is not None and remote.isVisible() and label is not None:
            label.setText('入力確定：' + name)

    def remote_command(self, command):
        if command in ('UP', 'DOWN'):
            names = list(self.buttons)
            pos = names.index(self.selected)
            self.choose(names[(pos + (1 if command == 'DOWN' else -1)) % len(names)])
        elif command == 'LEFT':
            self.choose(self._reject_key)
        elif command == 'RIGHT':
            self.choose(self._accept_key)
        elif command == 'CLOSE':
            self.selection.click(self._reject_key)
        elif command in ('ENTER', 'CLICK', 'DOUBLE_CLICK'):
            # Never discard an explicit wheel-selected Cancel. On initial
            # Remote-centre click, use the dialog's semantic accept button.
            target = self.selected if self.remote_has_selected else self._accept_key
            self.selection.click(target)
        return True  # No Remote action falls through to underlying Launch.

    def ask(self):
        loop = QEventLoop(self.dialog)
        self.dialog.finished.connect(loop.quit)
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        previous_text = label.text() if label is not None else None
        guard = ConfirmationInputGuard(self.dialog, remote, self)
        application = QApplication.instance()
        # A context menu may still hold a wheel adapter for a queued QAction.
        # Release it before the text prompt takes input ownership.
        menu_wheel = getattr(self.launcher, '_remote_context_wheel', None)
        if menu_wheel is not None:
            menu_wheel.stop()
        application.installEventFilter(guard)
        try:
            self.dialog.setWindowModality(Qt.WindowModality.NonModal)
            self.dialog.setModal(False)
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()
            if self.editor is not None:
                self.editor.setFocus(Qt.FocusReason.OtherFocusReason)
            if remote is not None and remote.isVisible():
                QTimer.singleShot(0, remote.raise_)
            loop.exec()
            return self.dialog.result() == int(self.dialog.DialogCode.Accepted)
        finally:
            application.removeEventFilter(guard)
            if label is not None and previous_text is not None:
                try:
                    label.setText(previous_text)
                except RuntimeError:
                    pass
            self.dialog.hide()
            self.dialog.deleteLater()
