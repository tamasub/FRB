"""User-owned categories for main-search history (Qt-independent).

The original search_history.json remains the authoritative keyword registry.
Category membership, per-folder manual ordering and expansion state are kept
separately so existing keyword history is never rewritten during migration.
"""
import copy
import json
import os
import tempfile
import uuid
from pathlib import Path

UNCATEGORIZED = 'uncategorized'
INITIAL_CATEGORIES = (
    ('windows', 'Windows'),
    ('development', '開発'),
    ('web', 'Web'),
    ('files', 'ファイル・フォルダー'),
    ('contacts', '連絡先'),
)


class SearchHistoryCategories:
    def __init__(self, path, keywords=()):
        self.path = Path(path)
        self.categories = [
            {'id': identifier, 'name': name, 'expanded': False, 'items': []}
            for identifier, name in INITIAL_CATEGORIES
        ]
        self.uncategorized_order = list(keywords)
        self.uncategorized_expanded = True
        self._read()
        self.sync(keywords)

    def _read(self):
        try:
            data = json.loads(self.path.read_text(encoding='utf-8-sig'))
        except (OSError, ValueError, UnicodeError):
            return
        if not isinstance(data, dict) or data.get('version') != 1:
            return
        raw_categories = data.get('categories')
        if not isinstance(raw_categories, list):
            return
        clean = []
        seen_ids = set()
        seen_keywords = set()
        for raw in raw_categories[:100]:
            if not isinstance(raw, dict):
                continue
            identifier = raw.get('id')
            name = raw.get('name')
            if (not isinstance(identifier, str) or not identifier or
                    identifier == UNCATEGORIZED or identifier in seen_ids or
                    not isinstance(name, str) or not name.strip()):
                continue
            items = []
            for word in raw.get('items', []) if isinstance(raw.get('items'), list) else []:
                if isinstance(word, str) and word not in seen_keywords:
                    items.append(word)
                    seen_keywords.add(word)
            clean.append({'id': identifier, 'name': name.strip()[:80],
                          'expanded': bool(raw.get('expanded', False)), 'items': items})
            seen_ids.add(identifier)
        # An intentionally empty category list is valid (user removed all).
        self.categories = clean
        raw_order = data.get('uncategorized_order', [])
        self.uncategorized_order = [x for x in raw_order if isinstance(x, str)] if isinstance(raw_order, list) else []
        self.uncategorized_expanded = bool(data.get('uncategorized_expanded', True))

    def _data(self):
        return {'version': 1, 'categories': self.categories,
                'uncategorized_order': self.uncategorized_order,
                'uncategorized_expanded': self.uncategorized_expanded}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(self._data(), ensure_ascii=False, indent=2) + '\n'
        temp = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.history_categories_', suffix='.tmp', delete=False) as output:
                temp = Path(output.name)
                output.write(serialized)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def _apply(self, action):
        before = copy.deepcopy(self._data())
        changed = action()
        if not changed:
            return False
        try:
            self._save()
        except OSError:
            self.categories = before['categories']
            self.uncategorized_order = before['uncategorized_order']
            self.uncategorized_expanded = before['uncategorized_expanded']
            raise
        return True

    def sync(self, keywords):
        """Reconcile external keyword edits without reordering surviving rows."""
        valid = set(keywords)
        before = copy.deepcopy(self._data())
        seen = set()
        for group in self.categories:
            cleaned = []
            for word in group['items']:
                if word in valid and word not in seen:
                    cleaned.append(word)
                    seen.add(word)
            group['items'] = cleaned
        unclassified = []
        seen_unclassified = set(seen)
        for word in self.uncategorized_order:
            if word in valid and word not in seen_unclassified:
                unclassified.append(word)
                seen_unclassified.add(word)
        # New history is added at the top of Unclassified, not auto-categorized.
        missing = [x for x in keywords if x not in seen and x not in unclassified]
        self.uncategorized_order = missing + unclassified
        if self._data() == before:
            return False
        try:
            self._save()
        except OSError:
            self.categories = before['categories']
            self.uncategorized_order = before['uncategorized_order']
            self.uncategorized_expanded = before['uncategorized_expanded']
            raise
        return True

    def group_items(self, category_id):
        if category_id == UNCATEGORIZED:
            return list(self.uncategorized_order)
        group = self.get(category_id)
        return list(group['items']) if group is not None else []

    def get(self, category_id):
        return next((g for g in self.categories if g['id'] == category_id), None)

    def create(self, name):
        name = str(name).strip()
        if not name or len(name) > 80 or name == '未分類' or any(
                g['name'].casefold() == name.casefold() for g in self.categories):
            return None
        identifier = 'user_' + uuid.uuid4().hex
        self._apply(lambda: self.categories.append(
            {'id': identifier, 'name': name, 'expanded': True, 'items': []}) or True)
        return identifier

    def rename(self, category_id, name):
        group = self.get(category_id)
        name = str(name).strip()
        if (group is None or not name or len(name) > 80 or name == '未分類' or
                any(g is not group and g['name'].casefold() == name.casefold()
                    for g in self.categories) or group['name'] == name):
            return False
        return self._apply(lambda: group.update(name=name) or True)

    def delete(self, category_id):
        group = self.get(category_id)
        if group is None:
            return False
        def change():
            self.uncategorized_order.extend(group['items'])
            self.categories.remove(group)
            return True
        return self._apply(change)

    def expanded(self, category_id):
        if category_id == UNCATEGORIZED:
            return self.uncategorized_expanded
        group = self.get(category_id)
        return bool(group and group['expanded'])

    def set_expanded(self, category_id, expanded):
        expanded = bool(expanded)
        if category_id == UNCATEGORIZED:
            if self.uncategorized_expanded == expanded:
                return False
            return self._apply(lambda: setattr(self, 'uncategorized_expanded', expanded) or True)
        group = self.get(category_id)
        if group is None or group['expanded'] == expanded:
            return False
        return self._apply(lambda: group.update(expanded=expanded) or True)

    def expand_all(self, expanded):
        expanded = bool(expanded)
        if (self.uncategorized_expanded == expanded and
                all(g['expanded'] == expanded for g in self.categories)):
            return False
        def change():
            self.uncategorized_expanded = expanded
            for group in self.categories:
                group['expanded'] = expanded
            return True
        return self._apply(change)

    def move_keyword(self, keyword, destination, index):
        """Move a keyword between folders (or reposition within one folder)."""
        if destination != UNCATEGORIZED and self.get(destination) is None:
            return False
        buckets = [self.uncategorized_order] + [g['items'] for g in self.categories]
        source = next((bucket for bucket in buckets if keyword in bucket), None)
        if source is None:
            return False
        target = (self.uncategorized_order if destination == UNCATEGORIZED
                  else self.get(destination)['items'])
        try:
            index = int(index)
        except (ValueError, TypeError):
            return False
        old_index = source.index(keyword)
        # Index indicates the insert position in target *before* removing source.
        if source is target and index > old_index:
            index -= 1
        index = max(0, min(index, len(target) - (source is target)))
        if source is target and index == old_index:
            return False
        def change():
            source.remove(keyword)
            target.insert(index, keyword)
            return True
        return self._apply(change)

    def move_category(self, category_id, target_index):
        group = self.get(category_id)
        if group is None:
            return False
        previous = self.categories.index(group)
        target_index = max(0, min(int(target_index), len(self.categories)))
        if target_index > previous:
            target_index -= 1
        if previous == target_index:
            return False
        def change():
            self.categories.remove(group)
            self.categories.insert(target_index, group)
            return True
        return self._apply(change)
