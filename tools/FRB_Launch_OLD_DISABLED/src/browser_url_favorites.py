"""JSON-persisted Browser address-bar favorites (independent of authored bookmarks)."""
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


def normalize_favorite_url(value):
    """Only store HTTP(S) URLs; retain the exact usable address and query."""
    text = str(value or '').strip()
    if not text or any(ord(c) < 32 for c in text):
        return ''
    try:
        parts = urlsplit(text)
        if parts.scheme.lower() not in ('http', 'https') or not parts.netloc:
            return ''
        if not parts.hostname or any(c.isspace() for c in parts.netloc):
            return ''
        _ = parts.port  # Reject malformed port numbers.
    except ValueError:
        return ''
    return text


class BrowserUrlFavorites:
    def __init__(self, path, limit=100):
        self.path = Path(path)
        self.limit = max(1, int(limit))
        self.urls = self._load()

    def _clean(self, values):
        result, seen = [], set()
        for value in values:
            if not isinstance(value, str):
                continue
            url = normalize_favorite_url(value)
            if url and url not in seen:
                result.append(url)
                seen.add(url)
                if len(result) >= self.limit:
                    break
        return result

    def _load(self):
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8-sig'))
            values = raw.get('urls', []) if isinstance(raw, dict) else []
            return self._clean(values) if isinstance(values, list) else []
        except (OSError, ValueError, UnicodeError):
            return []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.path.parent,
                    prefix='.browser_url_favorites_', suffix='.tmp', delete=False) as stream:
                temp = Path(stream.name)
                json.dump({'version': 1, 'urls': self.urls}, stream,
                          ensure_ascii=False, indent=2)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def add(self, value):
        url = normalize_favorite_url(value)
        if not url or url in self.urls:
            return False
        before = self.urls[:]
        self.urls.insert(0, url)
        self.urls = self.urls[:self.limit]
        try:
            self._save()
        except OSError:
            self.urls = before
            raise
        return True

    def remove(self, value):
        before = self.urls[:]
        self.urls = [url for url in self.urls if url != value]
        if before == self.urls:
            return False
        try:
            self._save()
        except OSError:
            self.urls = before
            raise
        return True

    def reorder(self, values):
        ordered = self._clean(values)
        if (len(ordered) != len(self.urls) or
                set(ordered) != set(self.urls) or ordered == self.urls):
            return False
        before = self.urls[:]
        self.urls = ordered
        try:
            self._save()
        except OSError:
            self.urls = before
            raise
        return True
