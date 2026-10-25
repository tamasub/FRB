"""Persistent, manually ordered temporary work-directory favorites.

This is intentionally independent of Launch's authored JSON menu data.
"""
import json
import ntpath
import os
import tempfile
from pathlib import Path


def normalize_favorite_path(path):
    """Preserve Windows drive/UNC spelling; reject relative and malformed paths."""
    text = str(path or '').strip().strip('"')
    if not text:
        return ''
    # On Windows, all drive and UNC paths use the native path separator.
    text = text.replace('/', '\\')
    if not ntpath.isabs(text):
        return ''
    return ntpath.normpath(text)


class FolderFavorites:
    def __init__(self, path, limit=100):
        self.path = Path(path)
        self.limit = max(1, int(limit))
        self.paths = self._load()

    def _clean(self, values):
        output, seen = [], set()
        for path in values:
            if not isinstance(path, str):
                continue
            normalized = normalize_favorite_path(path)
            key = ntpath.normcase(normalized)
            if normalized and key not in seen:
                output.append(normalized)
                seen.add(key)
                if len(output) >= self.limit:
                    break
        return output

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding='utf-8-sig'))
            paths = data.get('paths', []) if isinstance(data, dict) else []
            return self._clean(paths) if isinstance(paths, list) else []
        except (OSError, ValueError, UnicodeError):
            return []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.path.parent,
                    prefix='.folder_favorites_', suffix='.tmp', delete=False) as f:
                temp = Path(f.name)
                json.dump({'version': 1, 'paths': self.paths}, f, ensure_ascii=False, indent=2)
                f.write('\n')
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def add(self, path):
        normalized = normalize_favorite_path(path)
        if not normalized:
            return False
        if ntpath.normcase(normalized) in {ntpath.normcase(x) for x in self.paths}:
            return False
        prior = self.paths[:]
        self.paths.insert(0, normalized)
        self.paths = self.paths[:self.limit]
        try:
            self._save()
        except OSError:
            self.paths = prior
            raise
        return True

    def remove(self, path):
        key = ntpath.normcase(normalize_favorite_path(path))
        previous = self.paths[:]
        self.paths = [p for p in self.paths if ntpath.normcase(p) != key]
        if previous == self.paths:
            return False
        try:
            self._save()
        except OSError:
            self.paths = previous
            raise
        return True

    def reorder(self, paths):
        ordered = self._clean(paths)
        if len(ordered) != len(self.paths) or {ntpath.normcase(p) for p in ordered} != {ntpath.normcase(p) for p in self.paths}:
            return False
        if ordered == self.paths:
            return False
        previous = self.paths[:]
        self.paths = ordered
        try:
            self._save()
        except OSError:
            self.paths = previous
            raise
        return True
