"""Remote-assisted text confirmation without taking away keyboard editing.

For Launch-owned QDialogs only: the QLineEdit keeps native focus on open.
Remote wheel/left/right moves a *visible focus frame* on the actual OK/Cancel
QPushButton. Remote centre clicks that actual button. Background input is
blocked, while text entry/ordinary mouse operation remains native.
"""

from PySide6.QtCore import QEventLoop, Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialogButtonBox
from remote_confirmation import ConfirmationInputGuard


class RemoteTextDialog:
    FOCUS_BUTTON_STYLE = (
        'QPushButton { border: 2px solid #27865D; border-radius: 5px; '
        'padding: 5px 14px; background-color: #EAF7EF; '
        'color: #17472F; font-weight: 600; }'
        'QPushButton:pressed { background-color: #D1EAD9; }'
    )

    def __init__(self, launcher, dialog, editor, buttons):
        self.launcher = launcher
        self.dialog = dialog
        self.editor = editor
        self.buttons = {
            'OK': buttons.button(QDialogButtonBox.StandardButton.Ok),
            'Cancel': buttons.button(QDialogButtonBox.StandardButton.Cancel),
        }
        # Do not take editing focus until the user moves the Remote wheel/pad.
        self.selected = 'Cancel'
        self.remote_has_selected = False

    def choose(self, name):
        if name not in self.buttons:
            return
        self.selected = name
        self.remote_has_selected = True
        for key, button in self.buttons.items():
            if button is None:
                continue
            button.setStyleSheet(self.FOCUS_BUTTON_STYLE if key == name else '')
            if key == name:
                button.setFocus(Qt.FocusReason.TabFocusReason)
                button.update()
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        if remote is not None and remote.isVisible() and label is not None:
            label.setText('入力確定：' + name)

    def remote_command(self, command):
        if command in ('UP', 'DOWN'):
            self.choose('OK' if self.selected == 'Cancel' else 'Cancel')
        elif command == 'LEFT':
            self.choose('Cancel')
        elif command == 'RIGHT':
            self.choose('OK')
        elif command == 'CLOSE':
            button = self.buttons.get('Cancel')
            if button is not None:
                button.click()
        elif command in ('ENTER', 'CLICK', 'DOUBLE_CLICK'):
            # The first centre press from an editable text field means OK;
            # no extra wheel movement should be required to commit text.
            target = self.selected if self.remote_has_selected else 'OK'
            button = self.buttons.get(target)
            if button is not None:
                button.click()
        return True  # Block all background Remote actions while this dialog is open.

    def ask(self):
        loop = QEventLoop(self.dialog)
        self.dialog.finished.connect(loop.quit)
        remote = getattr(self.launcher, 'remote_window', None)
        label = getattr(remote, 'area_label', None)
        previous_text = label.text() if label is not None else None
        guard = ConfirmationInputGuard(self.dialog, remote)
        application = QApplication.instance()
        application.installEventFilter(guard)
        try:
            self.dialog.setWindowModality(Qt.WindowModality.NonModal)
            self.dialog.setModal(False)
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()
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
