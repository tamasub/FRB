"""Explicit Files List filter history, independent of global Launch search.

Keep Windows filenames and Boolean search expressions verbatim (in contrast
with the main-search '/' hotkey). The data live outside the user Launch JSON.
"""
import json
import os
import tempfile
from pathlib import Path


class FilesListSearchHistory:
    def __init__(self, path, limit=50):
        self.path = Path(path)
        self.limit = max(1, int(limit))
        self.keywords = self._load()

    def _load(self):
        try:
            payload = json.loads(self.path.read_text(encoding='utf-8-sig'))
        except (OSError, UnicodeError, ValueError):
            return []
        values = payload.get('keywords', []) if isinstance(payload, dict) else []
        if not isinstance(values, list):
            return []
        result, seen = [], set()
        for text in values:
            if not isinstance(text, str):
                continue
            value = text.strip()
            if value and value.casefold() not in seen:
                result.append(value)
                seen.add(value.casefold())
                if len(result) == self.limit:
                    break
        return result

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps({'version': 1, 'keywords': self.keywords},
                          ensure_ascii=False, indent=2) + '\n'
        temp = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.files_list_search_', suffix='.tmp',
                                             delete=False) as stream:
                temp = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def remember(self, text):
        value = str(text or '').strip()
        if not value or any(v.casefold() == value.casefold() for v in self.keywords):
            return False
        previous = self.keywords[:]
        self.keywords.insert(0, value)
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
        previous = self.keywords[:]
        self.keywords.remove(value)
        try:
            self._save()
        except OSError:
            self.keywords = previous
            raise
        return True
