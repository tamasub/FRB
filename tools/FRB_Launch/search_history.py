"""Persistent, manually ordered search keywords for the launcher main search.

This module deliberately has no Qt dependency.  Runtime state and generated
history live outside the user's editable launcher configuration.
"""
import json
import os
import tempfile
from pathlib import Path


HISTORY_LIMIT = 100


def normalize_keyword(value):
    """A slash is the history hotkey, not a searchable character."""
    return str(value or '').replace('/', '').strip()


class SearchHistory:
    def __init__(self, path, limit=HISTORY_LIMIT):
        self.path = Path(path)
        self.limit = max(1, int(limit))
        self.keywords = self._load()

    def _load(self):
        try:
            source = json.loads(self.path.read_text(encoding='utf-8-sig'))
            values = source.get('keywords', []) if isinstance(source, dict) else []
            if not isinstance(values, list):
                return []
        except (OSError, ValueError, UnicodeError):
            return []
        cleaned = []
        seen = set()
        for value in values:
            if not isinstance(value, str):
                continue
            keyword = normalize_keyword(value)
            if keyword and keyword.casefold() not in seen:
                seen.add(keyword.casefold())
                cleaned.append(keyword)
                if len(cleaned) >= self.limit:
                    break
        return cleaned

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps({'version': 1, 'keywords': self.keywords}, ensure_ascii=False, indent=2) + '\n'
        temporary = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.search_history_', suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def remember(self, value):
        keyword = normalize_keyword(value)
        if not keyword:
            return False
        if any(item.casefold() == keyword.casefold() for item in self.keywords):
            return False  # Preserve the user's custom order and original spelling.
        previous = list(self.keywords)
        self.keywords.insert(0, keyword)
        del self.keywords[self.limit:]
        try:
            self._save()
        except OSError:
            self.keywords = previous
            raise
        return True

    def remove(self, value):
        if value not in self.keywords:
            return False
        previous = list(self.keywords)
        self.keywords.remove(value)
        try:
            self._save()
        except OSError:
            self.keywords = previous
            raise
        return True

    def move(self, value, offset):
        if value not in self.keywords or offset not in (-1, 1):
            return False
        current = self.keywords.index(value)
        target = current + offset
        if target < 0 or target >= len(self.keywords):
            return False
        self.keywords[current], self.keywords[target] = self.keywords[target], self.keywords[current]
        try:
            self._save()
        except OSError:
            self.keywords[current], self.keywords[target] = self.keywords[target], self.keywords[current]
            raise
        return True
