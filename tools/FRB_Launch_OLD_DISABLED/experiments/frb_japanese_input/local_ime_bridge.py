"""Windows IME bridge targeting an editor INSIDE FRB Japanese Input.

Unlike v0.6 ExternalImeSession this has no external target window and never
sets WS_EX_NOACTIVATE.  Real Windows IME composition is owned by QLineEdit.
The source KanaInputModel is a provisional gesture history, not a second IME.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from ime_bridge import plan_preedit_transition


@dataclass
class LocalImeSession:
    sender: object
    editor_has_focus: Callable[[], bool]
    synced_preedit: str = ""

    def _require_focus(self) -> None:
        if not self.editor_has_focus():
            raise RuntimeError("FRBかなの入力欄にフォーカスがありません。入力欄をクリックしてください")

    def sync(self, new_preedit: str) -> None:
        # Validate the entire key sequence before sending a single key.
        tokens = plan_preedit_transition(self.synced_preedit, new_preedit)
        if not tokens:
            return
        self._require_focus()
        self.sender.send_tokens(tokens)
        self.synced_preedit = new_preedit

    def commit(self) -> None:
        if not self.synced_preedit:
            return
        self._require_focus()
        self.sender.send_tokens(["ENTER"])
        self.synced_preedit = ""

    def backspace_committed(self) -> None:
        self._require_focus()
        self.sender.send_tokens(["BACKSPACE"])

    def cancel(self) -> None:
        if self.synced_preedit:
            self._require_focus()
            self.sender.send_tokens(["ESCAPE"])
        self.synced_preedit = ""

    def forget(self) -> None:
        """An IME candidate was committed by the user independently."""
        self.synced_preedit = ""
