"""Validated declarative context menu configuration. No arbitrary shell steps."""
import json
from pathlib import Path

ALLOWED_ACTIONS = {
    'file': frozenset(('copy', 'cut', 'paste', 'delete', 'copy_full_path', 'copy_file_name', 'open_with', 'open_parent_folder', 'open_parent_terminal', 'run_with_pause', 'rename', 'properties', 'git_commit_from_zip')),
    'folder': frozenset(('copy', 'cut', 'paste', 'delete', 'open_explorer', 'open_terminal', 'copy_path', 'rename', 'properties')),
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
            # A separator is purely presentational and is explicitly placed
            # in JSON. It is not executable, has no title and may repeat.
            if entry.get('type') == 'separator':
                if set(entry) != {'type'}:
                    raise ValueError(f'menus.{kind} の区切り線は type のみ指定できます')
                result[kind].append({'type': 'separator'})
                continue
            if entry.get('type', 'action') != 'action':
                raise ValueError(f'menus.{kind} の type は action / separator のみです')
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


def visible_context_entries(entries, allowed_actions=None):
    """Drop unavailable actions and empty separator groups before showing QMenu.

    A separator specified in JSON may become adjacent to another one when a
    conditional action (e.g. run_with_pause) is not applicable to this file.
    """
    result = []
    pending_separator = False
    for entry in entries:
        if entry.get('type') == 'separator':
            pending_separator = bool(result)
            continue
        if allowed_actions is not None and entry['action_id'] not in allowed_actions:
            continue
        if pending_separator and result:
            result.append({'type': 'separator'})
        result.append(entry)
        pending_separator = False
    return result
