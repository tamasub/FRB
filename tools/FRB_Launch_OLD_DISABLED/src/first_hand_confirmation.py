"""Small, pure confirmation gate for the first-hand shuriken.

Flicking only proposes a candidate. The initial option is Cancel; after
an initial time guard a NEW click on the first-hand button confirms it, even
without a wheel move. Wheel DOWN explicitly chooses OK before execution.
The time guard prevents immediate ghost Press/Release from closing the UI.
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
