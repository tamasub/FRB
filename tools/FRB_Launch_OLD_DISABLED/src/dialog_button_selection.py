"""One button-selection mechanism shared by all Launch-owned dialog controllers.

Selection and activation are separate. A direct click on the REAL QPushButton
is never redirected, and no synthetic desktop click is issued.
"""


class DialogButtonSelection:
    FOCUS_BUTTON_STYLE = (
        'QPushButton { border: 2px solid #27865D; border-radius: 5px; '
        'padding: 5px 14px; background-color: #EAF7EF; '
        'color: #17472F; font-weight: 600; }'
        'QPushButton:pressed { background-color: #D1EAD9; }'
    )

    def __init__(self, dialog, buttons, selected):
        self.dialog = dialog
        self.buttons = dict(buttons)
        self.selected = selected

    def choose(self, name, *, focus_reason=None):
        if name not in self.buttons or self.buttons[name] is None:
            return False
        self.selected = name
        for key, button in self.buttons.items():
            if button is None:
                continue
            button.setStyleSheet(self.FOCUS_BUTTON_STYLE if key == name else '')
            if key == name:
                # QMessageBox has setDefaultButton; ordinary QDialog does not.
                set_default = getattr(self.dialog, 'setDefaultButton', None)
                if callable(set_default):
                    set_default(button)
                if focus_reason is not None:
                    button.setFocus(focus_reason)
                button.update()
        return True

    def cycle(self, *, focus_reason=None):
        names = [name for name, button in self.buttons.items() if button is not None]
        if not names:
            return False
        current = names.index(self.selected) if self.selected in names else -1
        return self.choose(names[(current + 1) % len(names)], focus_reason=focus_reason)

    def click(self, name=None):
        button = self.buttons.get(self.selected if name is None else name)
        if button is None:
            return False
        button.click()
        return True
