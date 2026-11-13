"""Page-root shortcut contract, independent of PySide6 and the Windows API.

A shortcut NAVIGATES to a root item. It never executes the item's action.
"""

MODIFIER_ORDER = ('ctrl', 'shift', 'alt', 'win')
MODIFIER_LABEL = {'ctrl': 'Ctrl', 'shift': 'Shift', 'alt': 'Alt', 'win': 'Win'}
MENU_HOTKEY_ID_START = 100


def canonical_hotkey(value):
    """Normalize a key into a portable identity (e.g. Ctrl+Shift+F).

    Consistent with the existing native hotkey interface, the final key is a
    single character. Control characters, whitespace, bare modifiers and
    duplicate modifiers are not allowed.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError('ショートカットキーを指定してください')
    parts = [part.strip() for part in value.split('+')]
    modifiers = [part.lower() for part in parts[:-1]]
    if (not modifiers or len(modifiers) != len(set(modifiers)) or
            any(part not in MODIFIER_LABEL for part in modifiers)):
        raise ValueError(f'ショートカットの修飾キーが不正です: {value}')
    key = parts[-1].upper()
    if len(key) != 1 or not key.isascii() or key.isspace() or ord(key) < 33:
        raise ValueError(f'ショートカットの末尾は1文字にしてください: {value}')
    return '+'.join([MODIFIER_LABEL[m] for m in MODIFIER_ORDER if m in modifiers] + [key])


def menu_shortcuts(data):
    """Return [(item_id, normalized_hotkey)] for enabled Page-root items.

    Deeply nested items may not define shortcuts. Do not derive shortcuts
    from runtime-merged installed-app or browser-bookmark children.
    """
    pages = {p['page_id']: p for p in data.get('pages', [])}
    occupied = {}
    default_key = canonical_hotkey(data.get('launch_hotkey') or 'Ctrl+Shift+;')
    occupied[default_key] = '通常起動キー'
    result = []
    for row in data.get('items', []):
        raw = row.get('launch_shortcut_key')
        if not raw or (isinstance(raw, str) and not raw.strip()):
            continue
        if row.get('parent_item_id'):
            raise ValueError(f"Page直下以外にはショートカットを設定できません: {row.get('title', row.get('item_id'))}")
        key = canonical_hotkey(raw)
        if key in occupied:
            raise ValueError(f'ショートカットキー重複: {key} ({occupied[key]} / {row.get("title", "")})')
        occupied[key] = row.get('title', '')
        page = pages.get(row.get('page_id'))
        if not row.get('enabled', True) or not page or not page.get('enabled', True):
            continue
        result.append((row['item_id'], key))
    return result
