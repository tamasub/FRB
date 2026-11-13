"""In-memory browser-style history for FRB Launch view states.

Search text is committed by the caller after an idle interval, not per key.
Current-row movement/checkbox changes are properties of the view rather than
separate destinations, so neither creates a new browser-history entry.
"""


class ViewNavigationHistory:
    def __init__(self, limit=100):
        self.limit = max(2, int(limit))
        self.entries = []
        self.index = -1

    @staticmethod
    def destination(state):
        return (state['page_id'],
                tuple(row['item_id'] for row in state['stack']),
                state['selection']['item_id'] if state['selection'] else None,
                state['query'])

    @property
    def current(self):
        return self.entries[self.index] if self.index >= 0 else None

    @property
    def can_back(self):
        return self.index > 0

    @property
    def can_forward(self):
        return 0 <= self.index < len(self.entries) - 1

    def reset(self, state):
        self.entries = [state]
        self.index = 0

    def update_current(self, state):
        """Keep cursor/check status current WITHOUT adding a history step."""
        if self.index < 0:
            self.reset(state)
        elif self.destination(self.current) == self.destination(state):
            self.entries[self.index] = state

    def push(self, state):
        if self.index < 0:
            self.reset(state)
            return False
        if self.destination(self.current) == self.destination(state):
            self.entries[self.index] = state
            return False
        del self.entries[self.index + 1:]
        self.entries.append(state)
        if len(self.entries) > self.limit:
            del self.entries[:len(self.entries) - self.limit]
        self.index = len(self.entries) - 1
        return True

    def back(self):
        if not self.can_back:
            return None
        self.index -= 1
        return self.current

    def forward(self):
        if not self.can_forward:
            return None
        self.index += 1
        return self.current
