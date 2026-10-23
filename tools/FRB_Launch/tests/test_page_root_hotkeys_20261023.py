"""Regression contract for FRB Launch's Page-root shortcuts.

The native WM_HOTKEY and Qt focus are verified by GUI tests on Windows;
these tests guard the portable contract and desktop wiring.
"""
from copy import deepcopy
import json
from pathlib import Path
import pytest

from core import validate
from menu_hotkeys import canonical_hotkey, menu_shortcuts

ROOT = Path(__file__).resolve().parents[1]


def sample():
    return json.loads((ROOT / 'config/frb_launch_sample_data_v0_1.json').read_text(encoding='utf-8-sig'))


def test_four_root_hotkeys_and_normal_open_are_independent():
    config = validate(sample())
    assert config['launch_hotkey'] == 'Ctrl+Shift+;'
    assert dict(menu_shortcuts(config)) == {
        'studio_app': 'Ctrl+Shift+S',
        'zip': 'Ctrl+Shift+Z',
        'folders': 'Ctrl+Shift+F',
        '__browser_bookmarks_root': 'Ctrl+Shift+B',
    }


def test_key_normalization_and_collision_detection():
    assert canonical_hotkey('shift + ctrl + f') == 'Ctrl+Shift+F'
    config = sample()
    for row in config['items']:
        if row['item_id'] == 'zip':
            row['launch_shortcut_key'] = 'shift+ctrl+f'
    with pytest.raises(ValueError, match='重複'):
        validate(config)
    for row in config['items']:
        if row['item_id'] == 'zip':
            row['launch_shortcut_key'] = 'Ctrl+Shift+;'
    with pytest.raises(ValueError, match='重複'):
        validate(config)


def test_reject_shortcuts_below_page_root():
    config = sample()
    child = next(row for row in config['items'] if row.get('parent_item_id'))
    child['launch_shortcut_key'] = 'Ctrl+Shift+Q'
    with pytest.raises(ValueError, match='Page直下'):
        validate(config)


def test_disabled_root_shortcuts_are_not_registered():
    config = sample()
    for row in config['items']:
        if row['item_id'] == 'folders':
            row['enabled'] = False
    assert 'folders' not in dict(menu_shortcuts(validate(config)))
    for page in config['pages']:
        if page['page_id'] == 'work':
            page['enabled'] = False
    assert not menu_shortcuts(validate(config))


def test_empty_shortcuts_keep_backward_compatibility():
    config = sample()
    for row in config['items']:
        row.pop('launch_shortcut_key', None)
    assert menu_shortcuts(validate(config)) == []


def test_studio_viewdef_exposes_shortcut_field():
    view = json.loads((ROOT / 'defs/launch/frb_launch_maintenance_view_def_v0_1.json').read_text(encoding='utf-8'))
    fields = next(section['fields'] for v in view['views'] for section in v.get('sections', [])
                  if section.get('dataPath') == '$.items')
    shortcut = next(f for f in fields if f['field'] == 'launch_shortcut_key')
    assert shortcut['edit']['visible']


def test_native_event_uses_hotkey_ids_and_never_executes():
    source = (ROOT / 'src/app.py').read_text(encoding='utf-8')
    assert 'self.registered_menu_hotkeys.get(int(msg.wParam))' in source
    assert 'self.summon_menu(target)' in source
    segment = source.split('    def summon_menu(self, item_id):', 1)[1].split('    def restore_keyboard_focus', 1)[0]
    assert 'self.execute(' not in segment
    assert 'self.stack = [row] if row.get(\'item_kind\') == \'category\' else []' in segment
    assert 'self.list.setCurrentItem(item)' in segment


def test_win32_hotkey_ids_are_distinct(monkeypatch):
    import windows
    calls = []

    class FakeUser32:
        def VkKeyScanW(self, key):
            return ord(key)

        def RegisterHotKey(self, hwnd, hotkey_id, modifiers, key):
            calls.append(('register', hotkey_id, modifiers, key))
            return True

        def UnregisterHotKey(self, hwnd, hotkey_id):
            calls.append(('unregister', hotkey_id))
            return True

    monkeypatch.setattr(windows, 'IS_WINDOWS', True)
    monkeypatch.setattr(windows, 'user', FakeUser32(), raising=False)
    windows.hotkey(12, 'Ctrl+Shift+;', 1)
    windows.hotkey(12, 'Ctrl+Shift+F', 100)
    windows.hotkey(12, 'Ctrl+Shift+Z', 101)
    windows.unhotkey(12, 101)
    assert [call[1] for call in calls] == [1, 100, 101, 101]
    assert all(call[2] & 0x4000 for call in calls[:3])
