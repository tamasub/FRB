"""Small, pure confirmation gate for the first-hand shuriken.

Flicking only proposes a candidate. A physical wheel action on the SAME
first-hand button selects Cancel/OK, and a separate button click commits.
The initial option is always Cancel, so ghost Qt releases cannot execute.
"""
from dataclasses import dataclass

CANCEL = 'cancel'
OK = 'ok'


@dataclass
class FirstHandConfirmation:
    candidate_id: str
    candidate_title: str
    choice: str = CANCEL
    wheel_selected: bool = False

    def __post_init__(self):
        if not self.candidate_id or not self.candidate_title:
            raise ValueError('A confirmed candidate must have an item ID and title')

    def wheel(self, delta: int):
        """Wheel UP = cancel, wheel DOWN = OK; never wrap to OK accidentally."""
        if delta > 0:
            self.choice = CANCEL
            self.wheel_selected = True
        elif delta < 0:
            self.choice = OK
            self.wheel_selected = True
        return self.choice

    def commit(self, clicked_inside: bool):
        """Return an item ID ONLY after explicit wheel-to-OK and click."""
        if clicked_inside and self.wheel_selected and self.choice == OK:
            return self.candidate_id
        return None
