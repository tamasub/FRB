"""Validated declarative context menu configuration. No arbitrary shell steps."""
import json
from pathlib import Path

ALLOWED_ACTIONS = {
    'file': frozenset(('copy_full_path', 'copy_file_name', 'rename', 'properties')),
    'folder': frozenset(('open_explorer', 'open_terminal', 'copy_path', 'rename', 'properties')),
}


def load_context_menus(path):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('version: 1 が必要です')
    definitions = data.get('menus')
    if not isinstance(definitions, dict) or set(definitions) != set(ALLOWED_ACTIONS):
        raise ValueError('menusには file と folder が必要です')
    result = {}
    for kind, allowed in ALLOWED_ACTIONS.items():
        entries = definitions[kind]
        if not isinstance(entries, list):
            raise ValueError(f'menus.{kind} は配列です')
        seen = set()
        result[kind] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f'menus.{kind} の要素はオブジェクトです')
            action = entry.get('action_id')
            title = entry.get('title')
            enabled = entry.get('enabled', True)
            if action not in allowed or action in seen:
                raise ValueError(f'menus.{kind} の action_id が重複または未対応です: {action}')
            if not isinstance(title, str) or not title.strip():
                raise ValueError(f'menus.{kind}.{action} の title が必要です')
            if not isinstance(enabled, bool):
                raise ValueError(f'menus.{kind}.{action} の enabled は真偽値です')
            seen.add(action)
            if enabled:
                result[kind].append({'action_id': action, 'title': title})
    return result
