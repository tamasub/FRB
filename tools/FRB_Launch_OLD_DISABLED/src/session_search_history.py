"""Volatile search-history candidates: never read from or written to disk.

A session entry is promoted explicitly to SearchHistory / SearchHistoryCategories.
The launcher remains alive in the system tray, so this state survives hiding
its window but disappears when the process exits.
"""
from search_history import normalize_keyword

SESSION_HISTORY = 'session_history'


class SessionSearchHistory:
    def __init__(self, limit=100):
        self.limit = max(1, int(limit))
        self.keywords = []

    def remember(self, value, persistent=()):
        text = normalize_keyword(value)
        if not text:
            return False
        key = text.casefold()
        if any(word.casefold() == key for word in persistent):
            return False
        if any(word.casefold() == key for word in self.keywords):
            return False
        # Only append; never disturb the position the user has learned.
        self.keywords.append(text)
        if len(self.keywords) > self.limit:
            self.keywords.pop(0)
        return True

    def remove(self, value):
        for index, word in enumerate(self.keywords):
            if word.casefold() == str(value).casefold():
                self.keywords.pop(index)
                return True
        return False

    def has(self, value):
        return any(word.casefold() == str(value).casefold() for word in self.keywords)
